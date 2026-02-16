# Generated manually for payment screenshot feature

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_aboutsection_socialmedia_remove_payment_payment_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='payment_reference',
            field=models.CharField(blank=True, help_text='Customer entered payment reference number', max_length=200),
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_screenshot',
            field=models.ImageField(blank=True, help_text='Payment proof screenshot', null=True, upload_to='payment_screenshots/'),
        ),
        migrations.AddField(
            model_name='payment',
            name='verified_at',
            field=models.DateTimeField(blank=True, help_text='When payment was verified by admin', null=True),
        ),
    ]
