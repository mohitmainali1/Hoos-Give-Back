from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('communityservice', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='title',
            field=models.CharField(unique=True),
        ),
    ]