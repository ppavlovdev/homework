import io
from typing import Optional

from django.test import TestCase
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image as PILImage

from api.models import Image
from api.serializers import ImageSerializer


# Test Image serializer
class ImageSerializerTestCase(TestCase):
    def _generate_image(
        self, name: str = "test.png", size: tuple[int, int] = (64, 64)
    ) -> io.BytesIO:
        file = io.BytesIO()
        image = PILImage.new("RGBA", size=size, color=(256, 0, 0))
        image.save(file, "png")
        file.name = name
        file.seek(0)
        return file

    def setUp(self):
        self.instance: Optional[Image] = None

        self.img1 = self._generate_image("test1.png", size=(64, 128))
        self.img2 = self._generate_image("test2.png", size=(64, 128))

    def tearDown(self):
        if self.instance:
            self.instance.image.delete(save=False)
            self.instance.delete()

    def test_serialization(self):
        stored_img = ImageFile(self.img1)
        instance = Image.objects.create(image=stored_img)

        serializer = ImageSerializer(instance)
        data = serializer.data

        self.assertEqual(data["image"], r"/images/test1.png")
        self.assertEqual(data["width"], 64)
        self.assertEqual(data["height"], 128)

        self.instance = instance

    def test_deserialization(self):
        uploaded_img = InMemoryUploadedFile(
            file=self.img2,
            field_name=None,
            name="test2.png",
            content_type="image/png",
            size=self.img2.getbuffer().nbytes,
            charset=None,
        )

        data = {
            "image": uploaded_img,
        }
        serializer = ImageSerializer(data=data)
        serializer.is_valid()
        instance: Image = serializer.save()

        self.assertEqual(instance.image.url, "/images/test2.png")
        self.assertEqual(instance.width, 64)
        self.assertEqual(instance.height, 128)

        self.instance = instance
