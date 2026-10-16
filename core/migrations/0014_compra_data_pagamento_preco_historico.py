# Migration for purchase price snapshots, timestamp, payment type and reverse relation.
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0013_itenscompra'),
    ]

    operations = [
        migrations.AddField(
            model_name='itenscompra',
            name='preco',
            field=models.DecimalField(default=0, max_digits=7, decimal_places=2),
        ),
        migrations.AddField(
            model_name='compra',
            name='data',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AddField(
            model_name='compra',
            name='tipo_pagamento',
            field=models.IntegerField(
                choices=[
                    (1, 'Cartão de Crédito'),
                    (2, 'Cartão de Débito'),
                    (3, 'PIX'),
                    (4, 'Boleto'),
                    (5, 'Transferência Bancária'),
                    (6, 'Dinheiro'),
                    (7, 'Outro'),
                ],
                default=1,
            ),
        ),
        migrations.AlterField(
            model_name='itenscompra',
            name='livro',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='itens_compra',
                to='core.livro',
            ),
        ),
    ]
