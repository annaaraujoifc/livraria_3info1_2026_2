from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Autor, Compra, ItensCompra, Livro


User = get_user_model()


class CompraTutorialAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='cliente@example.com', password='SenhaSegura123')
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        autor = Autor.objects.create(nome='Autora Teste')
        self.livro = Livro.objects.create(titulo='Livro teste', quantidade=8, preco=Decimal('12.50'))
        self.livro.autores.add(autor)

    def criar_compra(self, itens):
        response = self.client.post('/api/compras/', {'itens': itens}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        return Compra.objects.get(pk=response.data['id'])

    def test_compra_usa_usuario_autenticado_e_preco_historico(self):
        compra = self.criar_compra([{'livro': self.livro.pk, 'quantidade': 2}])
        item = compra.itens.get()
        self.assertEqual(compra.usuario, self.user)
        self.assertEqual(item.preco, Decimal('12.50'))
        self.assertEqual(compra.total, Decimal('25.00'))

        self.livro.preco = Decimal('19.99')
        self.livro.save(update_fields=['preco'])
        item.refresh_from_db()
        self.assertEqual(item.preco, Decimal('12.50'))
        self.assertEqual(compra.total, Decimal('25.00'))

    def test_rejeita_quantidade_zero_e_maior_que_estoque(self):
        for qtd in (0, -1, 9):
            response = self.client.post(
                '/api/compras/',
                {'itens': [{'livro': self.livro.pk, 'quantidade': qtd}]},
                format='json',
            )
            self.assertEqual(response.status_code, 400)

    def test_finalizar_baixa_estoque_e_nao_pode_repetir(self):
        compra = self.criar_compra([{'livro': self.livro.pk, 'quantidade': 3}])
        response = self.client.post(f'/api/compras/{compra.pk}/finalizar/', {}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.livro.refresh_from_db()
        self.assertEqual(self.livro.quantidade, 5)

        response = self.client.post(f'/api/compras/{compra.pk}/finalizar/', {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.livro.refresh_from_db()
        self.assertEqual(self.livro.quantidade, 5)

    def test_finalizacao_nao_vende_estoque_insuficiente(self):
        compra = self.criar_compra([{'livro': self.livro.pk, 'quantidade': 4}])
        self.livro.quantidade = 2
        self.livro.save(update_fields=['quantidade'])

        response = self.client.post(f'/api/compras/{compra.pk}/finalizar/', {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.livro.refresh_from_db()
        compra.refresh_from_db()
        self.assertEqual(self.livro.quantidade, 2)
        self.assertEqual(compra.status, Compra.StatusCompra.CARRINHO)

    def test_usuario_nao_consulta_compra_de_outro(self):
        compra = self.criar_compra([{'livro': self.livro.pk, 'quantidade': 1}])
        outro = User.objects.create_user(email='outro@example.com', password='SenhaSegura123')
        self.client.force_authenticate(outro)
        response = self.client.get(f'/api/compras/{compra.pk}/')
        self.assertEqual(response.status_code, 404)
