from django.db import transaction
from django.db.models import Q, Sum
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import Compra, Livro
from core.serializers import (
    LivroAjustarEstoqueSerializer,
    LivroAlterarPrecoSerializer,
    LivroMaisVendidoSerializer,
    LivroSerializer,
)


class LivroViewSet(ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer

    @extend_schema(
        request=LivroAlterarPrecoSerializer,
        responses={200: dict},
        description='Altera o preço de um livro específico.',
        summary='Alterar preço do livro',
    )
    @action(detail=True, methods=['patch'])
    def alterar_preco(self, request, pk=None):
        livro = self.get_object()
        serializer = LivroAlterarPrecoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        livro.preco = serializer.validated_data['preco']
        livro.save(update_fields=['preco'])
        return Response(
            {'detail': f'Preço do livro "{livro.titulo}" atualizado para {livro.preco}.'},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=None,
        responses={200: LivroMaisVendidoSerializer(many=True)},
        description='Lista livros com mais de 10 unidades vendidas em compras finalizadas.',
        summary='Listar livros mais vendidos',
    )
    @action(detail=False, methods=['get'])
    def mais_vendidos(self, request):
        livros = Livro.objects.annotate(
            total_vendidos=Sum(
                'itens_compra__quantidade',
                filter=Q(itens_compra__compra__status=Compra.StatusCompra.FINALIZADO),
            )
        ).filter(total_vendidos__gt=10).order_by('-total_vendidos')
        data = LivroMaisVendidoSerializer(livros, many=True).data
        if not data:
            return Response({'detail': 'Nenhum livro excedeu 10 vendas.'}, status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        request=LivroAjustarEstoqueSerializer,
        responses={200: dict},
        description='Aplica um ajuste positivo ou negativo no estoque sem permitir saldo negativo.',
        summary='Ajustar estoque',
    )
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def ajustar_estoque(self, request, pk=None):
        livro = Livro.objects.select_for_update().get(pk=self.get_object().pk)
        serializer = LivroAjustarEstoqueSerializer(data=request.data, context={'livro': livro})
        serializer.is_valid(raise_exception=True)
        livro.quantidade += serializer.validated_data['quantidade']
        livro.save(update_fields=['quantidade'])
        return Response(
            {'status': 'Quantidade ajustada com sucesso', 'novo_estoque': livro.quantidade},
            status=status.HTTP_200_OK,
        )
