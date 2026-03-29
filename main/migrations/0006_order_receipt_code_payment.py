from django.db import migrations, models
import random
import string


def make_receipt_code():
    """Safe default for migration - does NOT query the DB."""
    chars = string.ascii_uppercase + string.digits
    return "FL-" + ''.join(random.choices(chars, k=8))


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_profile_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(default='cash', max_length=20, verbose_name='Способ оплаты'),
        ),
        migrations.AddField(
            model_name='order',
            name='receipt_code',
            field=models.CharField(
                db_index=True,
                default=make_receipt_code,
                max_length=12,
                unique=True,
                verbose_name='Код чека',
            ),
        ),
        migrations.AlterField(
            model_name='order',
            name='phone',
            field=models.CharField(max_length=20, verbose_name='Телефон'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='phone',
            field=models.CharField(blank=True, max_length=20, verbose_name='Телефон'),
        ),
    ]
