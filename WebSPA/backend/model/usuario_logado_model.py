from dataclasses import dataclass, asdict
from typing import Optional, TYPE_CHECKING

from util.perfis import Perfil

if TYPE_CHECKING:
    from model.usuario_model import Usuario


@dataclass(frozen=True)
class UsuarioLogado:
    id: int
    nome: str
    email: str
    perfil: str

    def is_admin(self) -> bool:
        """Verifica se o usuário é administrador."""
        return self.perfil == Perfil.ADMIN.value

    def is_cliente(self) -> bool:
        """Verifica se o usuário é cliente."""
        return self.perfil == Perfil.CLIENTE.value

    def is_vendedor(self) -> bool:
        """Verifica se o usuário é vendedor."""
        return self.perfil == Perfil.VENDEDOR.value

    def tem_perfil(self, *perfis: str) -> bool:
        """
        Verifica se o usuário tem um dos perfis especificados.

        Args:
            *perfis: Valores de perfil para verificar (use Perfil.XXX.value)

        Returns:
            True se o usuário tem um dos perfis, False caso contrário

        Exemplo:
            if usuario.tem_perfil(Perfil.ADMIN.value, Perfil.VENDEDOR.value):
                # lógica para admin ou vendedor
        """
        return self.perfil in perfis

    def to_dict(self) -> dict:
        """
        Converte para dicionário (para armazenamento na sessão).

        Returns:
            Dict com os campos do usuário logado
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> Optional["UsuarioLogado"]:
        """
        Cria instância a partir de um dicionário.

        Args:
            data: Dicionário com os campos (pode ser None)

        Returns:
            Instância de UsuarioLogado ou None se data for None/inválido

        Raises:
            ValueError: Se data estiver incompleto (faltando campos obrigatórios)
        """
        if data is None:
            return None

        campos_obrigatorios = {"id", "nome", "email", "perfil"}
        campos_faltantes = campos_obrigatorios - set(data.keys())
        if campos_faltantes:
            raise ValueError(
                f"Campos obrigatórios ausentes em usuario_logado: {campos_faltantes}"
            )

        return cls(
            id=data["id"],
            nome=data["nome"],
            email=data["email"],
            perfil=data["perfil"],
        )

    @classmethod
    def from_usuario(cls, usuario: "Usuario") -> "UsuarioLogado":
        """
        Cria instância a partir de um objeto Usuario (model).

        Args:
            usuario: Instância de Usuario do banco de dados

        Returns:
            Instância de UsuarioLogado
        """
        return cls(
            id=usuario.id,
            nome=usuario.nome,
            email=usuario.email,
            perfil=usuario.perfil,
        )
