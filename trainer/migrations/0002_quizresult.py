"""Migration: add QuizResult model."""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Add QuizResult to store completed quiz sessions."""

    dependencies = [
        ('trainer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuizResult',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'score',
                    models.PositiveIntegerField(
                        default=0,
                        verbose_name='Correct answers',
                    ),
                ),
                (
                    'total',
                    models.PositiveIntegerField(
                        default=1,
                        verbose_name='Total questions',
                    ),
                ),
                (
                    'direction',
                    models.CharField(
                        default='orig_trans',
                        max_length=20,
                        verbose_name='Quiz direction',
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'collection',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='quiz_results',
                        to='trainer.collection',
                        verbose_name='Collection',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Quiz Result',
                'verbose_name_plural': 'Quiz Results',
                'ordering': ['-created_at'],
            },
        ),
    ]
