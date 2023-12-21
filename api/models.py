import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _

from treebeard.mp_tree import MP_Node


class AnnotationClass(models.TextChoices):
    TOOTH = "tooth", _("Tooth")
    CARIES = "caries", _("Caries")


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Image(BaseModel):
    image = models.ImageField(
        upload_to="images/", width_field="width", height_field="height"
    )
    width = models.IntegerField(null=False)
    height = models.IntegerField(null=False)

    class Meta:
        db_table = "images"


class Annotation(MP_Node, BaseModel):
    node_order_by = ["class_id"]

    image = models.OneToOneField(Image, on_delete=models.CASCADE, null=True)
    class_id = models.CharField(
        max_length=100, choices=AnnotationClass.choices, null=False
    )
    start_x = models.IntegerField(null=False)
    start_y = models.IntegerField(null=False)
    end_x = models.IntegerField(null=False)
    end_y = models.IntegerField(null=False)
    confirmed = models.BooleanField(default=False)
    confidence_percent = models.FloatField(null=False)
    tags = ArrayField(models.CharField(max_length=20), blank=True, null=True)
    surface = ArrayField(models.CharField(max_length=10), blank=True, null=True)

    class Meta:
        db_table = "annotations"
