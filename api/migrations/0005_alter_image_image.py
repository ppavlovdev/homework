# Generated by Django 5.0 on 2023-12-20 20:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0004_rename_path_image_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="image",
            name="image",
            field=models.ImageField(
                height_field="height", upload_to="images/", width_field="width"
            ),
        ),
    ]
