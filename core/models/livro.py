from django.db import models

from core.models import Autor
from uploader.models import Image

from .categoria import Categoria
from .editora import Editora


class Livro(models.Model):
    autores = models.ManyToManyField(Autor, related_name='livros')
    titulo = models.CharField(max_length=255)
    isbn = models.CharField(max_length=32, null=True, blank=True)
    capa = models.ForeignKey(Image, on_delete=models.PROTECT, null=True, blank=True)
    quantidade = models.IntegerField(default=0)
    preco = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='livros', null=True, blank=True)

    editora = models.ForeignKey(Editora, on_delete=models.PROTECT, related_name='livros', null=True, blank=True)

    def __str__(self):
        return f'({self.id}) {self.titulo} ({self.quantidade})'
