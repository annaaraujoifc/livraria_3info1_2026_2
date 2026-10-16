from datetime import datetime

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import Compra
from core.serializers import CompraCreateUpdateSerializer, CompraSerializer


class CompraViewSet(ModelViewSet):
    serializer_class = CompraSerializer

    def get_queryset(self):
        usuario = self.request.user
        if usuario.is_superuser or usuario.groups.filter(name='administradores').exists():
            return Compra.objects.all()
        return Compra.objects.filter(usuario=usuario)

    def get_serializer_class(self):
        if self.action in {'create', 'update', 'partial_update'}:
            return CompraCreateUpdateSerializer
        return CompraSerializer

    @action(detail=False, methods=['get'])
    def relatorio_vendas_mes(self, request):
        hoje = timezone.localdate()
        vendas = Compra.objects.filter(
            status=Compra.StatusCompra.FINALIZADO,
            data__year=hoje.year,
            data__month=hoje.month,
        )
        total_vendas = sum(compra.total for compra in vendas)
        return Response({
            'status': 'Relatório de vendas deste mês',
            'total_vendas': total_vendas,
            'quantidade_vendas': vendas.count(),
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def finalizar(self, request, pk=None):
        compra = self.get_object()
        if compra.status == Compra.StatusCompra.FINALIZADO:
            return Response({'status': 'Compra já finalizada'}, status=status.HTTP_400_BAD_REQUEST)

        itens = list(compra.itens.select_related('livro').all())
        for item in itens:
            if item.quantidade > item.livro.quantidade:
                return Response({
                    'status': 'Quantidade insuficiente',
                    'livro': item.livro.titulo,
                    'quantidade_disponivel': item.livro.quantidade,
                }, status=status.HTTP_400_BAD_REQUEST)

        for item in itens:
            item.livro.quantidade -= item.quantidade
            item.livro.save(update_fields=['quantidade'])

        compra.status = Compra.StatusCompra.FINALIZADO
        compra.save(update_fields=['status'])
        return Response({'status': 'Compra finalizada'}, status=status.HTTP_200_OK)
