"""Migration: add owner field to Collection model."""
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """Add owner ForeignKey to Collection."""

    dependencies = [
        ('trainer', '0002_quizresult'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='owner',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='collections_owned',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Owner',
            ),
        ),
    ]
