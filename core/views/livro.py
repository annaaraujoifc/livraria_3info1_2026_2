from django.db.models import Q, Sum
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

    @action(detail=True, methods=['patch'])
    def alterar_preco(self, request, pk=None):
        livro = self.get_object()
        serializer = LivroAlterarPrecoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        livro.preco = serializer.validated_data['preco']
        livro.save(update_fields=['preco'])
        return Response({'preco': livro.preco}, status=status.HTTP_200_OK)

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

    @action(detail=True, methods=['post'])
    def ajustar_estoque(self, request, pk=None):
        livro = self.get_object()
        serializer = LivroAjustarEstoqueSerializer(data=request.data, context={'livro': livro})
        serializer.is_valid(raise_exception=True)
        livro.quantidade += serializer.validated_data['quantidade']
        livro.save(update_fields=['quantidade'])
        return Response(
            {'status': 'Quantidade ajustada com sucesso', 'novo_estoque': livro.quantidade},
            status=status.HTTP_200_OK,
        )
