from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """
    Fix OrderItem.flower on_delete: миграция 0002 создала CASCADE,
    но модель объявляет PROTECT. Исправляем до PROTECT.
    """

    dependencies = [
        ('main', '0011_review_unique_user_flower_orderitem_protect'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='flower',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to='main.flower',
                verbose_name='Цветок',
            ),
        ),
    ]
