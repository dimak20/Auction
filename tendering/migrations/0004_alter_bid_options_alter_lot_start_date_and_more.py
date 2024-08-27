# Generated by Django 5.1 on 2024-08-25 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tendering', '0003_lot_participant'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bid',
            options={'ordering': ('-amount',)},
        ),
        migrations.AlterField(
            model_name='lot',
            name='start_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AddIndex(
            model_name='lot',
            index=models.Index(fields=['end_date'], name='tendering_l_end_dat_7b5e54_idx'),
        ),
    ]