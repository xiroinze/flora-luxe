from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_order_transaction_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('new', 'Новый'),
                    ('processing', 'В обработке'),
                    ('paid', 'Оплачен'),
                    ('delivered', 'Доставлен'),
                    ('cancelled', 'Отменён'),
                ],
                default='new',
                max_length=20,
            ),
        ),
    ]
