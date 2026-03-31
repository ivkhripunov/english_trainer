"""Migration: add Language and Collection models, refactor Word fields."""
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Add Language, Collection; rename Word.english/russian fields."""

    dependencies = [
        ('trainer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
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
                    'name',
                    models.CharField(
                        max_length=100,
                        unique=True,
                        validators=[django.core.validators.MinLengthValidator(2)],
                        verbose_name='Language name',
                    ),
                ),
                (
                    'native_name',
                    models.CharField(
                        blank=True,
                        max_length=100,
                        verbose_name='Name in native language',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Language',
                'verbose_name_plural': 'Languages',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Collection',
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
                    'name',
                    models.CharField(
                        max_length=200,
                        validators=[django.core.validators.MinLengthValidator(2)],
                        verbose_name='Collection name',
                    ),
                ),
                (
                    'description',
                    models.TextField(blank=True, verbose_name='Description'),
                ),
                (
                    'language',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='collections',
                        to='trainer.language',
                        verbose_name='Language',
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Collection',
                'verbose_name_plural': 'Collections',
                'ordering': ['-created_at'],
            },
        ),
        migrations.RenameField(
            model_name='word',
            old_name='english',
            new_name='original',
        ),
        migrations.RenameField(
            model_name='word',
            old_name='russian',
            new_name='translation',
        ),
        migrations.AddField(
            model_name='word',
            name='collection',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='words',
                to='trainer.collection',
                verbose_name='Collection',
            ),
        ),
    ]
