# Generated migration — combined initial state
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, validators=[django.core.validators.MinLengthValidator(2)], verbose_name='Language name')),
                ('native_name', models.CharField(blank=True, max_length=100, verbose_name='Name in native language')),
            ],
            options={'verbose_name': 'Language', 'verbose_name_plural': 'Languages', 'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, validators=[django.core.validators.MinLengthValidator(2)], verbose_name='Collection name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collections', to='trainer.language', verbose_name='Language')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'verbose_name': 'Collection', 'verbose_name_plural': 'Collections', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original', models.CharField(max_length=200, validators=[django.core.validators.MinLengthValidator(2)], verbose_name='Original word')),
                ('translation', models.CharField(max_length=200, validators=[django.core.validators.MinLengthValidator(2)], verbose_name='Translation (Russian)')),
                ('example', models.TextField(blank=True, verbose_name='Example sentence')),
                ('times_shown', models.PositiveIntegerField(default=0)),
                ('times_correct', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('collection', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='words', to='trainer.collection', verbose_name='Collection')),
            ],
            options={'verbose_name': 'Word', 'verbose_name_plural': 'Words', 'ordering': ['-created_at']},
        ),
    ]