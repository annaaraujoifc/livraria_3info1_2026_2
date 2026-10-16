from django.db import transaction
from rest_framework.serializers import (
    CharField,
    CurrentUserDefault,
    DateTimeField,
    HiddenField,
    ModelSerializer,
    SerializerMethodField,
    ValidationError,
)

from core.models import Compra, ItensCompra


class ItensCompraCreateUpdateSerializer(ModelSerializer):
    # O preço é definido no servidor no momento em que o item é gravado.
    preco = rest_framework_field = __import__('rest_framework.serializers', fromlist=['DecimalField']).DecimalField(
        max_digits=7, decimal_places=2, read_only=True
    )

    class Meta:
        model = ItensCompra
        fields = ('livro', 'quantidade', 'preco')

    def validate_quantidade(self, quantidade):
        if quantidade <= 0:
            raise ValidationError('A quantidade deve ser maior do que zero.')
        return quantidade

    def validate(self, item):
        if item['quantidade'] > item['livro'].quantidade:
            raise ValidationError('Quantidade de itens maior do que a quantidade em estoque.')
        return item


class CompraCreateUpdateSerializer(ModelSerializer):
    usuario = HiddenField(default=CurrentUserDefault())
    itens = ItensCompraCreateUpdateSerializer(many=True)

    class Meta:
        model = Compra
        fields = ('id', 'usuario', 'itens')

    def validate(self, attrs):
        compra = getattr(self, 'instance', None)
        if compra and compra.status != Compra.StatusCompra.CARRINHO:
            raise ValidationError('Somente compras no carrinho podem ser alteradas.')
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        itens_data = validated_data.pop('itens')
        compra = Compra.objects.create(**validated_data)
        for item_data in itens_data:
            item_data['preco'] = item_data['livro'].preco
            ItensCompra.objects.create(compra=compra, **item_data)
        return compra

    @transaction.atomic
    def update(self, compra, validated_data):
        itens_data = validated_data.pop('itens', None)
        if itens_data is not None:
            compra.itens.all().delete()
            for item_data in itens_data:
                item_data['preco'] = item_data['livro'].preco
                ItensCompra.objects.create(compra=compra, **item_data)
        return super().update(compra, validated_data)


class ItensCompraSerializer(ModelSerializer):
    total = SerializerMethodField()

    def get_total(self, instance):
        return instance.total

    class Meta:
        model = ItensCompra
        fields = ('livro', 'quantidade', 'preco', 'total')
        depth = 1


class CompraSerializer(ModelSerializer):
    usuario = CharField(source='usuario.email', read_only=True)
    status = CharField(source='get_status_display', read_only=True)
    data_criacao = DateTimeField(read_only=True)
    data_atualizacao = DateTimeField(read_only=True)
    tipo_pagamento = CharField(source='get_tipo_pagamento_display', read_only=True)
    itens = ItensCompraSerializer(many=True, read_only=True)
    total = SerializerMethodField()

    def get_total(self, instance):
        return instance.total

    class Meta:
        model = Compra
        fields = (
            'id', 'usuario', 'status', 'total', 'data_criacao',
            'data_atualizacao', 'tipo_pagamento', 'itens',
        )
