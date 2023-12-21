import io
import uuid

import pytest
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image as PILImage

from api.models import Image, Annotation
from api.serializers import ImageSerializer, AnnotationSerializer
from api.type_defs import AnnotationDict, AnnotationExternalDict, AnnotationFlatDict


@pytest.fixture
def image() -> io.BytesIO:
    file = io.BytesIO()
    image = PILImage.new("RGBA", size=(64, 64), color=(256, 0, 0))
    image.save(file, "png")
    file.name = "test.png"
    file.seek(0)
    return file


@pytest.fixture
def annotation_dict() -> AnnotationDict:
    return {
        "id": str(uuid.uuid4()),
        "class_id": "tooth",
        "shape": {
            "start_x": 0,
            "start_y": 0,
            "end_x": 10,
            "end_y": 10,
        },
        "meta": {
            "confirmed": False,
            "confidence_percent": 0.5,
        },
        "tags": ["48"],
    }


@pytest.fixture
def annotation_with_child_dict() -> list[AnnotationDict]:
    return [
        {
            "id": "5b0cd508-587b-493b-98ea-b08a8c31d575",
            "class_id": "tooth",
            "shape": {"end_x": 809, "end_y": 792, "start_x": 600, "start_y": 567},
            "tags": ["48"],
            "meta": {"confirmed": False, "confidence_percent": 0.99},
        },
        {
            "id": "d1b5b119-28ab-4c61-829f-326ade1c5bb7",
            "class_id": "caries",
            "relations": [
                {"type": "child", "label_id": "5b0cd508-587b-493b-98ea-b08a8c31d575"}
            ],
            "surface": ["B", "O", "L"],
            "shape": {"end_x": 781, "end_y": 690, "start_x": 667, "start_y": 566},
            "meta": {"confirmed": False, "confidence_percent": 0.87},
        },
    ]


@pytest.fixture
def annotation() -> Annotation:
    return Annotation.add_root(
        class_id="tooth",
        start_x=0,
        start_y=0,
        end_x=10,
        end_y=10,
        tags=["48"],
        confirmed=False,
        confidence_percent=0.5,
    )


@pytest.fixture
def annotation_external() -> Annotation:
    return Annotation.add_root(
        class_id="tooth",
        start_x=0,
        start_y=0,
        end_x=10,
        end_y=10,
        tags=["48"],
        confirmed=True,
        confidence_percent=0.5,
    )


@pytest.fixture
def annotation_with_child() -> Annotation:
    root = Annotation.add_root(
        class_id="tooth",
        start_x=0,
        start_y=0,
        end_x=10,
        end_y=10,
        tags=["48"],
        confirmed=False,
        confidence_percent=0.5,
    )
    root.add_child(
        class_id="caries",
        start_x=667,
        start_y=566,
        end_x=781,
        end_y=690,
        surface=["B", "O", "L"],
        confirmed=False,
        confidence_percent=0.87,
    )
    return root


@pytest.fixture
def annotation_external_with_child() -> Annotation:
    root = Annotation.add_root(
        class_id="tooth",
        start_x=0,
        start_y=0,
        end_x=10,
        end_y=10,
        tags=["48"],
        confirmed=True,
        confidence_percent=0.5,
    )
    root.add_child(
        class_id="caries",
        start_x=667,
        start_y=566,
        end_x=781,
        end_y=690,
        surface=["B", "O", "L"],
        confirmed=True,
        confidence_percent=0.87,
    )
    return root


class TestImageSerializer:
    @pytest.mark.django_db
    def test_image_serialization(self, image: io.BytesIO):
        stored_img = ImageFile(image)
        instance = Image.objects.create(image=stored_img)

        serializer = ImageSerializer(instance)
        data = serializer.data

        assert data["image"] == r"/images/test.png"
        assert data["width"] == 64
        assert data["height"] == 64

        instance.image.delete(save=False)
        instance.delete()

    @pytest.mark.django_db
    def test_image_deserialization(self, image: io.BytesIO):
        uploaded_img = InMemoryUploadedFile(
            file=image,
            field_name=None,
            name="test.png",
            content_type="image/png",
            size=image.getbuffer().nbytes,
            charset=None,
        )

        data = {
            "image": uploaded_img,
        }
        serializer = ImageSerializer(data=data)
        serializer.is_valid()
        instance: Image = serializer.save()

        assert instance.image.url == "/images/test.png"
        assert instance.width == 64
        assert instance.height == 64

        instance.image.delete(save=False)
        instance.delete()


class TestAnnotationSerializer:
    @pytest.mark.django_db
    def test_annotation_serialization(self, annotation: Annotation):
        serializer = AnnotationSerializer(instance=annotation)
        data: AnnotationDict = serializer.data

        assert data["id"] == str(annotation.id)
        assert data["class_id"] == "tooth"
        assert data["shape"]["start_x"] == 0
        assert data["shape"]["start_y"] == 0
        assert data["shape"]["end_x"] == 10
        assert data["shape"]["end_y"] == 10
        assert data["meta"]["confirmed"] is False
        assert data["meta"]["confidence_percent"] == 0.5

    @pytest.mark.django_db
    def test_annotation_with_children_serialization(
        self, annotation_with_child: Annotation
    ):
        data = []
        for instance in [annotation_with_child] + list(
            annotation_with_child.get_children()
        ):
            serializer = AnnotationSerializer(instance=instance)
            data.append(serializer.data)

        assert data[0]["id"] == str(annotation_with_child.id)
        assert data[0]["class_id"] == "tooth"
        assert data[0]["shape"]["start_x"] == 0
        assert data[0]["shape"]["start_y"] == 0
        assert data[0]["shape"]["end_x"] == 10
        assert data[0]["shape"]["end_y"] == 10
        assert data[0]["meta"]["confirmed"] is False
        assert data[0]["meta"]["confidence_percent"] == 0.5
        assert data[0]["tags"] == ["48"]

        assert data[1]["id"] == str(annotation_with_child.get_children()[0].id)
        assert data[1]["class_id"] == "caries"
        assert data[1]["relations"][0]["type"] == "child"
        assert data[1]["relations"][0]["label_id"] == str(annotation_with_child.id)
        assert data[1]["shape"]["start_x"] == 667
        assert data[1]["shape"]["start_y"] == 566
        assert data[1]["shape"]["end_x"] == 781
        assert data[1]["shape"]["end_y"] == 690
        assert data[1]["meta"]["confirmed"] is False
        assert data[1]["meta"]["confidence_percent"] == 0.87
        assert data[1]["surface"] == ["B", "O", "L"]

    @pytest.mark.django_db
    def test_external_annotation_serialization(self, annotation_external: Annotation):
        serializer = AnnotationSerializer(instance=annotation_external)
        data: AnnotationExternalDict = serializer.data

        assert data["kind"] == "tooth"
        assert data["shape"]["x"] == [0, 10]
        assert data["shape"]["y"] == [0, 10]
        assert data["number"] == "48"

    @pytest.mark.django_db
    def test_annotation_external_with_children_serialization(
        self, annotation_external_with_child: Annotation
    ):
        serializer = AnnotationSerializer(instance=annotation_external_with_child)
        data: AnnotationExternalDict = serializer.data

        assert data["kind"] == "tooth"
        assert data["shape"]["x"] == [0, 10]
        assert data["shape"]["y"] == [0, 10]
        assert data["children"][0]["kind"] == "caries"
        assert data["children"][0]["shape"]["x"] == [667, 781]
        assert data["children"][0]["shape"]["y"] == [566, 690]
        assert data["children"][0]["surface"] == "BOL"

    @pytest.mark.django_db
    def test_annotation_deserialization(self, annotation_dict):
        serializer = AnnotationSerializer(data=annotation_dict)
        serializer.is_valid()
        instance: Annotation = serializer.save()

        assert instance.class_id == "tooth"
        assert instance.start_x == 0
        assert instance.start_y == 0
        assert instance.end_x == 10
        assert instance.end_y == 10
        assert instance.confirmed is False
        assert instance.confidence_percent == 0.5

        instance.delete()

    @pytest.mark.django_db
    def test_annotations_deserialization(self, annotation_with_child_dict):
        serializer = AnnotationSerializer(data=annotation_with_child_dict, many=True)
        serializer.is_valid()
        instances: list[Annotation] = serializer.save()

        assert instances[0].class_id == "tooth"
        assert instances[0].start_x == 600
        assert instances[0].start_y == 567
        assert instances[0].end_x == 809
        assert instances[0].end_y == 792
        assert instances[0].confirmed is False
        assert instances[0].confidence_percent == 0.99

        assert instances[1].class_id == "caries"
        assert instances[1].start_x == 667
        assert instances[1].start_y == 566
        assert instances[1].end_x == 781
        assert instances[1].end_y == 690
        assert instances[1].confirmed is False
        assert instances[1].confidence_percent == 0.87

        instances[0].delete()
        instances[1].delete()

    @pytest.mark.django_db
    def test_annotation_update(self, annotation_dict, annotation):
        annotation_dict["id"] = str(annotation.id)
        annotation_dict["tags"] = ["49"]
        annotation_dict["shape"]["start_x"] = 100

        serializer = AnnotationSerializer(instance=annotation, data=annotation_dict)
        serializer.is_valid()
        instance: Annotation = serializer.save()

        assert instance.class_id == "tooth"
        assert instance.start_x == 100
        assert instance.start_y == 0
        assert instance.end_x == 10
        assert instance.end_y == 10
        assert instance.confirmed is False
        assert instance.confidence_percent == 0.5
        assert instance.tags == ["49"]

        instance.delete()
