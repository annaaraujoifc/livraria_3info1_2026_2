from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer, IntegerField, ValidationError

from core.models import Livro


class LivroSerializer(ModelSerializer):
    class Meta:
        model = Livro
        fields = '__all__'


class LivroAlterarPrecoSerializer(Serializer):
    preco = serializers.DecimalField(max_digits=7, decimal_places=2, min_value=0)


class LivroMaisVendidoSerializer(Serializer):
    id = IntegerField()
    titulo = serializers.CharField()
    total_vendidos = IntegerField()


class LivroAjustarEstoqueSerializer(Serializer):
    quantidade = IntegerField()

    def validate_quantidade(self, value):
        livro = self.context.get('livro')
        if livro and livro.quantidade + value < 0:
            raise ValidationError('A quantidade em estoque não pode ser negativa.')
        return value
