from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import Compra, Livro
from core.serializers import CompraCreateUpdateSerializer, CompraSerializer


class CompraViewSet(ModelViewSet):
    serializer_class = CompraSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        usuario = self.request.user
        if usuario.is_superuser or usuario.groups.filter(name='administradores').exists():
            return Compra.objects.all()
        return Compra.objects.filter(usuario=usuario)

    def get_serializer_class(self):
        if self.action in {'create', 'update', 'partial_update'}:
            return CompraCreateUpdateSerializer
        return CompraSerializer

    def perform_destroy(self, instance):
        if instance.status != Compra.StatusCompra.CARRINHO:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('Somente compras no carrinho podem ser excluídas.')
        instance.delete()

    @extend_schema(
        request=None,
        responses={200: dict},
        description='Relatório das compras finalizadas no mês atual.',
        summary='Relatório de vendas do mês',
    )
    @action(detail=False, methods=['get'])
    def relatorio_vendas_mes(self, request):
        hoje = timezone.localdate()
        vendas = Compra.objects.filter(
            status=Compra.StatusCompra.FINALIZADO,
            data_criacao__year=hoje.year,
            data_criacao__month=hoje.month,
        )
        total_vendas = sum((compra.total for compra in vendas), start=0)
        return Response({
            'status': 'Relatório de vendas deste mês',
            'total_vendas': total_vendas,
            'quantidade_vendas': vendas.count(),
        }, status=status.HTTP_200_OK)

    @extend_schema(
        request=None,
        responses={200: dict, 400: dict},
        description='Finaliza o carrinho e baixa os livros do estoque.',
        summary='Finalizar compra',
    )
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def finalizar(self, request, pk=None):
        compra = self.get_object()
        if compra.status != Compra.StatusCompra.CARRINHO:
            return Response(
                {'status': 'Somente compras no carrinho podem ser finalizadas.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        itens = list(compra.itens.all())
        if not itens:
            return Response(
                {'status': 'Não é possível finalizar uma compra sem itens.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Lock dos livros para evitar que duas finalizações concorrentes vendam
        # unidades além do estoque disponível (em bancos que suportam row locks).
        livro_ids = sorted({item.livro_id for item in itens})
        livros = {
            livro.pk: livro
            for livro in Livro.objects.select_for_update().filter(pk__in=livro_ids).order_by('pk')
        }

        for item in itens:
            livro = livros[item.livro_id]
            if item.quantidade > livro.quantidade:
                return Response({
                    'status': 'Quantidade insuficiente',
                    'livro': livro.titulo,
                    'quantidade_disponivel': livro.quantidade,
                }, status=status.HTTP_400_BAD_REQUEST)

        for item in itens:
            livro = livros[item.livro_id]
            livro.quantidade -= item.quantidade
            livro.save(update_fields=['quantidade'])

        compra.status = Compra.StatusCompra.FINALIZADO
        compra.save(update_fields=['status', 'data_atualizacao'])
        return Response({'status': 'Compra finalizada'}, status=status.HTTP_200_OK)
