# Generated by Django 4.2.2 on 2023-07-04 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0003_cart_order_orderitem_order_items_order_user_cartitem_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Preparing', 'Preparing'), ('Enroute', 'Enroute'), ('Rejected', 'Rejected'), ('Completed', 'Completed')], default='Pending', max_length=20),
        ),
    ]