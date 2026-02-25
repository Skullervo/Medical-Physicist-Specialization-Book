from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sisalto', '0008_alter_epa_options_alter_specialty_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='epa',
            name='slug',
            field=models.SlugField(blank=True, max_length=300, unique=True),
        ),
        migrations.AlterField(
            model_name='specialty',
            name='slug',
            field=models.SlugField(blank=True, max_length=150, unique=True),
        ),
    ]
