from .autor import AutorSerializer
from .categoria import CategoriaSerializer
from .editora import EditoraSerializer
from .livro import (\n    LivroSerializer,\n    LivroAlterarPrecoSerializer,\n    LivroMaisVendidoSerializer,\n    LivroAjustarEstoqueSerializer,\n)
from .user import UserRegistrationSerializer, UserSerializer
from .compra import (
    CompraCreateUpdateSerializer,
    CompraSerializer,
    ItensCompraCreateUpdateSerializer,
    ItensCompraSerializer,
)