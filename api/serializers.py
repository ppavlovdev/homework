from rest_framework import serializers

from api.models import Image, Annotation


class ImageSerializer(serializers.ModelSerializer):
    width = serializers.IntegerField(read_only=True)
    height = serializers.IntegerField(read_only=True)

    class Meta:
        model = Image
        fields = "__all__"
