from decimal import Decimal

from django.test import TestCase

from core.models import Compra, ItensCompra, Livro, User


class LivroModelTests(TestCase):
    def test_livro_tem_preco_e_quantidade_padrao(self):
        livro = Livro.objects.create(titulo='Livro de teste')

        assert livro.preco == Decimal('0.00')
        assert livro.quantidade == 0

    def test_str_do_livro_inclui_titulo_e_quantidade(self):
        livro = Livro.objects.create(
            titulo='Livro de teste',
            quantidade=4,
        )

        assert 'Livro de teste' in str(livro)
        assert '(4)' in str(livro)


class CompraModelTests(TestCase):
    def setUp(self):
        # Ajuste os campos se o modelo User do projeto exigir outros dados.
        self.usuario = User.objects.create_user(
            email='teste@example.com',
            password='Senha-teste-123',
        )
        self.livro = Livro.objects.create(
            titulo='Livro de teste',
            preco=Decimal('25.50'),
            quantidade=10,
        )

    def test_compra_inicia_com_status_carrinho(self):
        compra = Compra.objects.create(usuario=self.usuario)

        assert compra.status == Compra.StatusCompra.CARRINHO

    def test_total_do_item_e_calculado_pelo_preco_e_quantidade(self):
        compra = Compra.objects.create(usuario=self.usuario)
        item = ItensCompra.objects.create(
            compra=compra,
            livro=self.livro,
            quantidade=3,
        )

        assert item.total == Decimal('76.50')
