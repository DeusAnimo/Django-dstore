# Generated by Django 2.2.3 on 2019-07-27 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dshop', '0006_item_discount_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='description',
            field=models.TextField(default='This is description product, Lorem lorem lorem'),
            preserve_default=False,
        ),
    ]
