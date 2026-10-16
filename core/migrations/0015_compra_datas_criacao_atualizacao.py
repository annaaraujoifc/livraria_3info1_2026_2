from django.db import migrations, models
from django.utils import timezone


def preencher_data_atualizacao(apps, schema_editor):
    Compra = apps.get_model('core', 'Compra')
    Compra.objects.filter(data_atualizacao__isnull=True).update(data_atualizacao=timezone.now())


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0014_compra_data_pagamento_preco_historico'),
    ]

    operations = [
        migrations.RenameField(
            model_name='compra',
            old_name='data',
            new_name='data_criacao',
        ),
        migrations.AddField(
            model_name='compra',
            name='data_atualizacao',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.RunPython(preencher_data_atualizacao, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='compra',
            name='data_atualizacao',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
