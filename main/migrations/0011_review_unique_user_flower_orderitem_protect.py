from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_fix_order_status_choices'),
    ]

    operations = [
        # Уникальность: один отзыв от пользователя на товар
        migrations.AlterUniqueTogether(
            name='review',
            unique_together={('user', 'flower')},
        ),
        # Расширяем max_length receipt_code до 15 (было 12)
        migrations.AlterField(
            model_name='order',
            name='receipt_code',
            field=models.CharField(
                db_index=True,
                default=None,
                max_length=15,
                unique=True,
                verbose_name='Код чека',
            ),
            preserve_default=False,
        ),
        # Добавляем payment_method choices
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(
                choices=[
                    ('cash', 'Наличные'),
                    ('card', 'Карта'),
                    ('pickup', 'Самовывоз'),
                    ('payme', 'Payme'),
                    ('click', 'Click'),
                ],
                default='cash',
                max_length=20,
                verbose_name='Способ оплаты',
            ),
        ),
    ]
