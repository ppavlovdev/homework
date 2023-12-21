from __future__ import annotations

from typing import cast, Literal, Optional

from rest_framework import serializers

from api.models import Image, Annotation
from api.type_defs import AnnotationDict, AnnotationExternalDict, AnnotationFlatDict


class ImageSerializer(serializers.ModelSerializer):
    width = serializers.IntegerField(read_only=True)
    height = serializers.IntegerField(read_only=True)

    class Meta:
        model = Image
        fields = "__all__"


class AnnotationSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    parent = serializers.UUIDField(write_only=True, required=False)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=20), required=False
    )
    surface = serializers.ListField(
        child=serializers.CharField(max_length=10), required=False
    )

    class Meta:
        model = Annotation
        fields = [
            "id",
            "image",
            "class_id",
            "start_x",
            "start_y",
            "end_x",
            "end_y",
            "confirmed",
            "confidence_percent",
            "tags",
            "surface",
            "parent",
        ]

    def _exclude_none(self, data: dict) -> dict:
        return {k: v for k, v in data.items() if v is not None}

    def create(self, validated_data) -> Annotation:
        parent = validated_data.pop("parent", None)
        image = validated_data.pop("image", None)
        if parent:
            parent = Annotation.objects.get(pk=parent)
            child = parent.add_child(**validated_data)
            return child
        instance = Annotation.add_root(**validated_data)
        if image:
            instance.image = image
            instance.save(update_fields=["image"])
        return instance

    def update(
        self, instance: Annotation, validated_data: AnnotationFlatDict
    ) -> Annotation:
        parent = validated_data.pop("parent", None)
        if parent:
            parent = Annotation.objects.get(pk=parent)
            instance.move(parent, pos="last-child")
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save(update_fields=[k for k in validated_data.keys() if k != "id"])
        return instance

    def to_internal_value(self, data: AnnotationDict) -> AnnotationFlatDict:
        data_new: AnnotationFlatDict = {
            "id": data["id"],
            "image": data.get("image", None),
            "class_id": data["class_id"],
            "start_x": data["shape"]["start_x"],
            "start_y": data["shape"]["start_y"],
            "end_x": data["shape"]["end_x"],
            "end_y": data["shape"]["end_y"],
            "confirmed": data["meta"]["confirmed"],
            "confidence_percent": data["meta"]["confidence_percent"],
            "tags": data.get("tags", None),
            "surface": data.get("surface", None),
            "parent": data["relations"][0]["label_id"]
            if data.get("relations", None)
            else None,
        }
        return super().to_internal_value(self._exclude_none(data_new))

    def to_representation(
        self, instance: Annotation
    ) -> list[AnnotationDict] | AnnotationExternalDict:
        if not instance.confirmed:
            return [
                self._exclude_none(
                    {
                        "id": str(instance.pk),
                        "class_id": cast(Literal["tooth", "caries"], instance.class_id),
                        "shape": {
                            "start_x": instance.start_x,
                            "start_y": instance.start_y,
                            "end_x": instance.end_x,
                            "end_y": instance.end_y,
                        },
                        "relations": [
                            {"type": "child", "label_id": str(instance.get_parent().pk)}
                        ]
                        if instance.get_parent()
                        else None,
                        "tags": cast(Optional[list[str]], instance.tags),
                        "surface": cast(Optional[list[str]], instance.surface),
                        "meta": {
                            "confirmed": instance.confirmed,
                            "confidence_percent": instance.confidence_percent,
                        },
                    }
                )
                for instance in Annotation.get_tree(instance)
            ]
        else:
            return self._exclude_none(
                {
                    "id": str(instance.pk),
                    "kind": cast(Literal["tooth", "caries"], instance.class_id),
                    "shape": {
                        "x": [instance.start_x, instance.end_x],
                        "y": [instance.start_y, instance.end_y],
                    },
                    "number": cast(Optional[str], instance.tags[0])
                    if instance.tags
                    else None,
                    "surface": "".join(instance.surface) if instance.surface else None,
                    "children": [
                        self.to_representation(child)
                        for child in instance.get_children()
                    ]
                    if instance.get_children()
                    else None,
                }
            )
