from .autor import AutorSerializer
from .categoria import CategoriaSerializer
from .editora import EditoraSerializer
from .livro import (
    LivroSerializer,
    LivroAlterarPrecoSerializer,
    LivroMaisVendidoSerializer,
    LivroAjustarEstoqueSerializer,
)
from .user import UserRegistrationSerializer, UserSerializer
from .compra import (
    CompraCreateUpdateSerializer,
    CompraSerializer,
    ItensCompraCreateUpdateSerializer,
    ItensCompraSerializer,
)