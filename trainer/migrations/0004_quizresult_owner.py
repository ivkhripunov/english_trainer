"""Migration: add owner field to QuizResult model."""
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """Add owner ForeignKey to QuizResult."""

    dependencies = [
        ('trainer', '0003_collection_owner'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='quizresult',
            name='owner',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='quiz_results',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Owner',
            ),
        ),
    ]