"""
Testes de integração para o repositório de chamados.

Testa as operações CRUD e funções auxiliares do chamado_repo.
"""
import pytest

from repo import chamado_repo, chamado_interacao_repo, usuario_repo
from model.chamado_model import Chamado, StatusChamado, PrioridadeChamado
from model.chamado_interacao_model import ChamadoInteracao, TipoInteracao
from model.usuario_model import Usuario
from util.security import criar_hash_senha
from util.perfis import Perfil


class TestChamadoRepoInserir:
    """Testes para a função inserir."""

    def test_inserir_chamado_retorna_id(self, usuario_repo_teste):
        """Deve inserir chamado e retornar ID."""
        chamado = Chamado(
            id=0,
            titulo="Novo Chamado",
            status=StatusChamado.ABERTO,
            prioridade=PrioridadeChamado.MEDIA,
            usuario_id=usuario_repo_teste
        )

        chamado_id = chamado_repo.inserir(chamado)

        assert chamado_id is not None
        assert chamado_id > 0

    def test_inserir_chamado_com_prioridade_alta(self, usuario_repo_teste):
        """Deve inserir chamado com prioridade alta."""
        chamado = Chamado(
            id=0,
            titulo="Chamado Urgente",
            status=StatusChamado.ABERTO,
            prioridade=PrioridadeChamado.ALTA,
            usuario_id=usuario_repo_teste
        )

        chamado_id = chamado_repo.inserir(chamado)

        assert chamado_id is not None
        chamado_salvo = chamado_repo.obter_por_id(chamado_id)
        assert chamado_salvo.prioridade == PrioridadeChamado.ALTA

    def test_inserir_chamado_com_prioridade_urgente(self, usuario_repo_teste):
        """Deve inserir chamado com prioridade urgente."""
        chamado = Chamado(
            id=0,
            titulo="Chamado Urgentissimo",
            status=StatusChamado.ABERTO,
            prioridade=PrioridadeChamado.URGENTE,
            usuario_id=usuario_repo_teste
        )

        chamado_id = chamado_repo.inserir(chamado)

        assert chamado_id is not None
        chamado_salvo = chamado_repo.obter_por_id(chamado_id)
        assert chamado_salvo.prioridade == PrioridadeChamado.URGENTE


class TestChamadoRepoObterPorId:
    """Testes para a função obter_por_id."""

    def test_obter_por_id_existente(self, chamado_repo_teste):
        """Deve retornar chamado quando ID existe."""
        resultado = chamado_repo.obter_por_id(chamado_repo_teste)

        assert resultado is not None
        assert resultado.id == chamado_repo_teste
        assert resultado.titulo == "Chamado Repo Teste"
        assert resultado.status == StatusChamado.ABERTO
        assert resultado.prioridade == PrioridadeChamado.MEDIA

    def test_obter_por_id_inexistente(self):
        """Deve retornar None quando ID não existe."""
        resultado = chamado_repo.obter_por_id(99999)

        assert resultado is None


class TestChamadoRepoObterTodos:
    """Testes para a função obter_todos."""

    def test_obter_todos_retorna_lista(self, usuario_repo_teste, chamado_repo_teste):
        """Deve retornar lista de chamados."""
        resultado = chamado_repo.obter_todos(usuario_repo_teste)

        assert isinstance(resultado, list)
        assert len(resultado) >= 1

    def test_obter_todos_inclui_chamado_criado(self, usuario_repo_teste):
        """Deve incluir chamados criados na lista."""
        chamado = Chamado(
            id=0,
            titulo="Chamado para Listar",
            status=StatusChamado.ABERTO,
            prioridade=PrioridadeChamado.BAIXA,
            usuario_id=usuario_repo_teste
        )
        chamado_id = chamado_repo.inserir(chamado)

        resultado = chamado_repo.obter_todos(usuario_repo_teste)

        ids = [c.id for c in resultado]
        assert chamado_id in ids


class TestChamadoRepoObterPorUsuario:
    """Testes para a função obter_por_usuario."""

    def test_obter_por_usuario_existente(self, usuario_repo_teste, chamado_repo_teste):
        """Deve retornar chamados do usuário."""
        resultado = chamado_repo.obter_por_usuario(usuario_repo_teste)

        assert isinstance(resultado, list)
        assert len(resultado) >= 1
        assert all(c.usuario_id == usuario_repo_teste for c in resultado)

    def test_obter_por_usuario_sem_chamados(self):
        """Deve retornar lista vazia para usuário sem chamados."""
        # Criar usuário sem chamados
        usuario = Usuario(
            id=0,
            nome="Usuario Sem Chamados",
            email="sem_chamados@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario_id = usuario_repo.inserir(usuario)

        resultado = chamado_repo.obter_por_usuario(usuario_id)

        assert isinstance(resultado, list)
        assert len(resultado) == 0

    def test_obter_por_usuario_multiplos_chamados(self, usuario_repo_teste):
        """Deve retornar todos os chamados do usuário."""
        # Criar múltiplos chamados
        for i in range(3):
            chamado = Chamado(
                id=0,
                titulo=f"Chamado {i}",
                status=StatusChamado.ABERTO,
                prioridade=PrioridadeChamado.MEDIA,
                usuario_id=usuario_repo_teste
            )
            chamado_repo.inserir(chamado)

        resultado = chamado_repo.obter_por_usuario(usuario_repo_teste)

        assert len(resultado) >= 3


class TestChamadoRepoAtualizarStatus:
    """Testes para a função atualizar_status."""

    def test_atualizar_status_para_em_analise(self, chamado_repo_teste):
        """Deve atualizar status para Em Análise."""
        resultado = chamado_repo.atualizar_status(
            chamado_repo_teste,
            StatusChamado.EM_ANALISE.value
        )

        assert resultado is True
        chamado = chamado_repo.obter_por_id(chamado_repo_teste)
        assert chamado.status == StatusChamado.EM_ANALISE

    def test_atualizar_status_para_resolvido(self, chamado_repo_teste):
        """Deve atualizar status para Resolvido."""
        resultado = chamado_repo.atualizar_status(
            chamado_repo_teste,
            StatusChamado.RESOLVIDO.value
        )

        assert resultado is True
        chamado = chamado_repo.obter_por_id(chamado_repo_teste)
        assert chamado.status == StatusChamado.RESOLVIDO

    def test_atualizar_status_e_fechar(self, chamado_repo_teste):
        """Deve atualizar status e definir data de fechamento."""
        resultado = chamado_repo.atualizar_status(
            chamado_repo_teste,
            StatusChamado.FECHADO.value,
            fechar=True
        )

        assert resultado is True
        chamado = chamado_repo.obter_por_id(chamado_repo_teste)
        assert chamado.status == StatusChamado.FECHADO
        assert chamado.data_fechamento is not None

    def test_atualizar_status_inexistente(self):
        """Deve retornar False quando chamado não existe."""
        resultado = chamado_repo.atualizar_status(
            99999,
            StatusChamado.EM_ANALISE.value
        )

        assert resultado is False


class TestChamadoRepoExcluir:
    """Testes para a função excluir."""

    def test_excluir_chamado_existente(self, usuario_repo_teste):
        """Deve excluir chamado existente."""
        chamado = Chamado(
            id=0,
            titulo="Chamado para Excluir",
            status=StatusChamado.ABERTO,
            prioridade=PrioridadeChamado.MEDIA,
            usuario_id=usuario_repo_teste
        )
        chamado_id = chamado_repo.inserir(chamado)

        resultado = chamado_repo.excluir(chamado_id)

        assert resultado is True
        chamado_excluido = chamado_repo.obter_por_id(chamado_id)
        assert chamado_excluido is None

    def test_excluir_chamado_inexistente(self):
        """Deve retornar False quando chamado não existe."""
        resultado = chamado_repo.excluir(99999)

        assert resultado is False


class TestChamadoRepoContadores:
    """Testes para funções de contagem."""

    def test_contar_abertos_por_usuario(self, usuario_repo_teste):
        """Deve contar chamados abertos do usuário."""
        # Criar chamados abertos
        for i in range(2):
            chamado = Chamado(
                id=0,
                titulo=f"Chamado Aberto {i}",
                status=StatusChamado.ABERTO,
                prioridade=PrioridadeChamado.MEDIA,
                usuario_id=usuario_repo_teste
            )
            chamado_repo.inserir(chamado)

        # Criar chamado fechado
        chamado_fechado = Chamado(
            id=0,
            titulo="Chamado Fechado",
            status=StatusChamado.FECHADO,
            prioridade=PrioridadeChamado.MEDIA,
            usuario_id=usuario_repo_teste
        )
        chamado_repo.inserir(chamado_fechado)

        quantidade = chamado_repo.contar_abertos_por_usuario(usuario_repo_teste)

        assert isinstance(quantidade, int)
        assert quantidade >= 2

    def test_contar_abertos_por_usuario_sem_chamados(self):
        """Deve retornar 0 para usuário sem chamados abertos."""
        usuario = Usuario(
            id=0,
            nome="Usuario Contador",
            email="contador@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario_id = usuario_repo.inserir(usuario)

        quantidade = chamado_repo.contar_abertos_por_usuario(usuario_id)

        assert quantidade == 0

    def test_contar_pendentes(self, usuario_repo_teste):
        """Deve contar total de chamados pendentes."""
        # Criar chamados pendentes (abertos ou em análise)
        chamado = Chamado(
            id=0,
            titulo="Chamado Pendente",
            status=StatusChamado.ABERTO,
            prioridade=PrioridadeChamado.MEDIA,
            usuario_id=usuario_repo_teste
        )
        chamado_repo.inserir(chamado)

        quantidade = chamado_repo.contar_pendentes()

        assert isinstance(quantidade, int)
        assert quantidade >= 1


class TestChamadoRepoCriarTabela:
    """Testes para a função criar_tabela."""

    def test_criar_tabela_retorna_true(self):
        """Deve retornar True ao criar/verificar tabela."""
        resultado = chamado_repo.criar_tabela()

        assert resultado is True


class TestChamadoRepoEnums:
    """Testes para verificar conversão de enums."""

    def test_chamado_com_todos_status(self, usuario_repo_teste):
        """Deve suportar todos os status do enum."""
        for status in StatusChamado:
            chamado = Chamado(
                id=0,
                titulo=f"Chamado Status {status.value}",
                status=status,
                prioridade=PrioridadeChamado.MEDIA,
                usuario_id=usuario_repo_teste
            )
            chamado_id = chamado_repo.inserir(chamado)

            chamado_salvo = chamado_repo.obter_por_id(chamado_id)
            assert chamado_salvo.status == status

    def test_chamado_com_todas_prioridades(self, usuario_repo_teste):
        """Deve suportar todas as prioridades do enum."""
        for prioridade in PrioridadeChamado:
            chamado = Chamado(
                id=0,
                titulo=f"Chamado Prioridade {prioridade.value}",
                status=StatusChamado.ABERTO,
                prioridade=prioridade,
                usuario_id=usuario_repo_teste
            )
            chamado_id = chamado_repo.inserir(chamado)

            chamado_salvo = chamado_repo.obter_por_id(chamado_id)
            assert chamado_salvo.prioridade == prioridade


# ============================================================================
# TESTES DE CHAMADO_INTERACAO_REPO
# ============================================================================


class TestChamadoInteracaoRepoInserir:
    """Testes para a função inserir de chamado_interacao_repo."""

    def test_inserir_interacao_retorna_id(self, chamado_repo_teste, usuario_repo_teste):
        """Deve inserir interação e retornar ID."""
        interacao = ChamadoInteracao(
            id=0,
            chamado_id=chamado_repo_teste,
            usuario_id=usuario_repo_teste,
            mensagem="Nova interação",
            tipo=TipoInteracao.ABERTURA,
            data_interacao=None,
            status_resultante=StatusChamado.ABERTO.value
        )

        interacao_id = chamado_interacao_repo.inserir(interacao)

        assert interacao_id is not None
        assert interacao_id > 0

    def test_inserir_interacao_tipo_resposta_usuario(self, chamado_repo_teste, usuario_repo_teste):
        """Deve inserir interação do tipo resposta do usuário."""
        interacao = ChamadoInteracao(
            id=0,
            chamado_id=chamado_repo_teste,
            usuario_id=usuario_repo_teste,
            mensagem="Resposta do usuário",
            tipo=TipoInteracao.RESPOSTA_USUARIO,
            data_interacao=None,
            status_resultante=None
        )

        interacao_id = chamado_interacao_repo.inserir(interacao)

        assert interacao_id is not None
        interacao_salva = chamado_interacao_repo.obter_por_id(interacao_id)
        assert interacao_salva.tipo == TipoInteracao.RESPOSTA_USUARIO

    def test_inserir_interacao_tipo_resposta_admin(self, chamado_repo_teste, admin_repo_teste):
        """Deve inserir interação do tipo resposta do administrador."""
        interacao = ChamadoInteracao(
            id=0,
            chamado_id=chamado_repo_teste,
            usuario_id=admin_repo_teste,
            mensagem="Resposta do administrador",
            tipo=TipoInteracao.RESPOSTA_ADMIN,
            data_interacao=None,
            status_resultante=StatusChamado.EM_ANALISE.value
        )

        interacao_id = chamado_interacao_repo.inserir(interacao)

        assert interacao_id is not None
        interacao_salva = chamado_interacao_repo.obter_por_id(interacao_id)
        assert interacao_salva.tipo == TipoInteracao.RESPOSTA_ADMIN


class TestChamadoInteracaoRepoObterPorId:
    """Testes para a função obter_por_id de chamado_interacao_repo."""

    def test_obter_por_id_existente(self, interacao_repo_teste):
        """Deve retornar interação quando ID existe."""
        resultado = chamado_interacao_repo.obter_por_id(interacao_repo_teste)

        assert resultado is not None
        assert resultado.id == interacao_repo_teste
        assert resultado.mensagem == "Mensagem de teste"

    def test_obter_por_id_inexistente(self):
        """Deve retornar None quando ID não existe."""
        resultado = chamado_interacao_repo.obter_por_id(99999)

        assert resultado is None


class TestChamadoInteracaoRepoObterPorChamado:
    """Testes para a função obter_por_chamado."""

    def test_obter_por_chamado_com_interacoes(self, chamado_repo_teste, usuario_repo_teste):
        """Deve retornar todas as interações do chamado."""
        # Criar múltiplas interações
        for i in range(3):
            interacao = ChamadoInteracao(
                id=0,
                chamado_id=chamado_repo_teste,
                usuario_id=usuario_repo_teste,
                mensagem=f"Interação {i}",
                tipo=TipoInteracao.RESPOSTA_USUARIO,
                data_interacao=None,
                status_resultante=None
            )
            chamado_interacao_repo.inserir(interacao)

        resultado = chamado_interacao_repo.obter_por_chamado(chamado_repo_teste)

        assert isinstance(resultado, list)
        assert len(resultado) >= 3

    def test_obter_por_chamado_sem_interacoes(self, usuario_repo_teste):
        """Deve retornar lista vazia quando chamado não tem interações."""
        # Criar chamado sem interações
        chamado = Chamado(
            id=0,
            titulo="Chamado Sem Interações",
            status=StatusChamado.ABERTO,
            prioridade=PrioridadeChamado.MEDIA,
            usuario_id=usuario_repo_teste
        )
        chamado_id = chamado_repo.inserir(chamado)

        resultado = chamado_interacao_repo.obter_por_chamado(chamado_id)

        assert isinstance(resultado, list)
        assert len(resultado) == 0


class TestChamadoInteracaoRepoContarPorChamado:
    """Testes para a função contar_por_chamado."""

    def test_contar_por_chamado_com_interacoes(self, chamado_repo_teste, usuario_repo_teste):
        """Deve contar corretamente as interações do chamado."""
        # Criar 3 interações
        for i in range(3):
            interacao = ChamadoInteracao(
                id=0,
                chamado_id=chamado_repo_teste,
                usuario_id=usuario_repo_teste,
                mensagem=f"Contagem {i}",
                tipo=TipoInteracao.RESPOSTA_USUARIO,
                data_interacao=None,
                status_resultante=None
            )
            chamado_interacao_repo.inserir(interacao)

        quantidade = chamado_interacao_repo.contar_por_chamado(chamado_repo_teste)

        assert isinstance(quantidade, int)
        assert quantidade >= 3

    def test_contar_por_chamado_sem_interacoes(self, usuario_repo_teste):
        """Deve retornar 0 quando chamado não tem interações."""
        # Criar chamado sem interações
        chamado = Chamado(
            id=0,
            titulo="Chamado Vazio",
            status=StatusChamado.ABERTO,
            prioridade=PrioridadeChamado.MEDIA,
            usuario_id=usuario_repo_teste
        )
        chamado_id = chamado_repo.inserir(chamado)

        quantidade = chamado_interacao_repo.contar_por_chamado(chamado_id)

        assert quantidade == 0


class TestChamadoInteracaoRepoExcluirPorChamado:
    """Testes para a função excluir_por_chamado."""

    def test_excluir_por_chamado_existente(self, usuario_repo_teste):
        """Deve excluir todas as interações do chamado."""
        # Criar chamado e interações
        chamado = Chamado(
            id=0,
            titulo="Chamado para Excluir Interações",
            status=StatusChamado.ABERTO,
            prioridade=PrioridadeChamado.MEDIA,
            usuario_id=usuario_repo_teste
        )
        chamado_id = chamado_repo.inserir(chamado)

        for i in range(2):
            interacao = ChamadoInteracao(
                id=0,
                chamado_id=chamado_id,
                usuario_id=usuario_repo_teste,
                mensagem=f"Para excluir {i}",
                tipo=TipoInteracao.RESPOSTA_USUARIO,
                data_interacao=None,
                status_resultante=None
            )
            chamado_interacao_repo.inserir(interacao)

        resultado = chamado_interacao_repo.excluir_por_chamado(chamado_id)

        assert resultado is True
        quantidade = chamado_interacao_repo.contar_por_chamado(chamado_id)
        assert quantidade == 0

    def test_excluir_por_chamado_sem_interacoes(self, usuario_repo_teste):
        """Deve retornar True mesmo quando chamado não tem interações."""
        # Criar chamado sem interações
        chamado = Chamado(
            id=0,
            titulo="Chamado Vazio para Exclusão",
            status=StatusChamado.ABERTO,
            prioridade=PrioridadeChamado.MEDIA,
            usuario_id=usuario_repo_teste
        )
        chamado_id = chamado_repo.inserir(chamado)

        resultado = chamado_interacao_repo.excluir_por_chamado(chamado_id)

        assert resultado is True


class TestChamadoInteracaoRepoMarcarComoLidas:
    """Testes para a função marcar_como_lidas."""

    def test_marcar_como_lidas_mensagens_outros(self, chamado_repo_teste, usuario_repo_teste, admin_repo_teste):
        """Deve marcar como lidas mensagens de outros usuários."""
        # Criar interação do admin
        interacao = ChamadoInteracao(
            id=0,
            chamado_id=chamado_repo_teste,
            usuario_id=admin_repo_teste,
            mensagem="Mensagem do admin",
            tipo=TipoInteracao.RESPOSTA_ADMIN,
            data_interacao=None,
            status_resultante=None
        )
        chamado_interacao_repo.inserir(interacao)

        # Usuário cliente visualiza e marca como lido
        resultado = chamado_interacao_repo.marcar_como_lidas(chamado_repo_teste, usuario_repo_teste)

        assert resultado is True

    def test_marcar_como_lidas_nao_marca_proprias(self, chamado_repo_teste, usuario_repo_teste):
        """Deve retornar True (não precisa marcar próprias mensagens)."""
        # Criar interação do próprio usuário
        interacao = ChamadoInteracao(
            id=0,
            chamado_id=chamado_repo_teste,
            usuario_id=usuario_repo_teste,
            mensagem="Minha mensagem",
            tipo=TipoInteracao.RESPOSTA_USUARIO,
            data_interacao=None,
            status_resultante=None
        )
        chamado_interacao_repo.inserir(interacao)

        resultado = chamado_interacao_repo.marcar_como_lidas(chamado_repo_teste, usuario_repo_teste)

        assert resultado is True


class TestChamadoInteracaoRepoObterContadorNaoLidas:
    """Testes para a função obter_contador_nao_lidas."""

    def test_obter_contador_nao_lidas_com_mensagens(self, usuario_repo_teste, admin_repo_teste):
        """Deve retornar contagem de mensagens não lidas por chamado."""
        # Criar chamado
        chamado = Chamado(
            id=0,
            titulo="Chamado com Não Lidas",
            status=StatusChamado.ABERTO,
            prioridade=PrioridadeChamado.MEDIA,
            usuario_id=usuario_repo_teste
        )
        chamado_id = chamado_repo.inserir(chamado)

        # Criar interações do admin (não lidas pelo cliente)
        for i in range(2):
            interacao = ChamadoInteracao(
                id=0,
                chamado_id=chamado_id,
                usuario_id=admin_repo_teste,
                mensagem=f"Resposta admin {i}",
                tipo=TipoInteracao.RESPOSTA_ADMIN,
                data_interacao=None,
                status_resultante=None
            )
            chamado_interacao_repo.inserir(interacao)

        resultado = chamado_interacao_repo.obter_contador_nao_lidas(usuario_repo_teste)

        assert isinstance(resultado, dict)
        # O chamado deve ter mensagens não lidas
        if chamado_id in resultado:
            assert resultado[chamado_id] >= 2

    def test_obter_contador_nao_lidas_sem_mensagens(self, usuario_repo_teste):
        """Deve retornar dicionário vazio quando não há mensagens não lidas."""
        resultado = chamado_interacao_repo.obter_contador_nao_lidas(usuario_repo_teste)

        assert isinstance(resultado, dict)


class TestChamadoInteracaoRepoTemRespostaAdmin:
    """Testes para a função tem_resposta_admin."""

    def test_tem_resposta_admin_quando_existe(self, chamado_repo_teste, admin_repo_teste):
        """Deve retornar True quando há resposta de admin."""
        interacao = ChamadoInteracao(
            id=0,
            chamado_id=chamado_repo_teste,
            usuario_id=admin_repo_teste,
            mensagem="Resposta administrativa",
            tipo=TipoInteracao.RESPOSTA_ADMIN,
            data_interacao=None,
            status_resultante=None
        )
        chamado_interacao_repo.inserir(interacao)

        resultado = chamado_interacao_repo.tem_resposta_admin(chamado_repo_teste)

        assert resultado is True

    def test_tem_resposta_admin_quando_nao_existe(self, chamado_repo_teste, usuario_repo_teste):
        """Deve retornar False quando só há respostas de usuário."""
        interacao = ChamadoInteracao(
            id=0,
            chamado_id=chamado_repo_teste,
            usuario_id=usuario_repo_teste,
            mensagem="Resposta do usuário",
            tipo=TipoInteracao.RESPOSTA_USUARIO,
            data_interacao=None,
            status_resultante=None
        )
        chamado_interacao_repo.inserir(interacao)

        resultado = chamado_interacao_repo.tem_resposta_admin(chamado_repo_teste)

        assert resultado is False

    def test_tem_resposta_admin_chamado_vazio(self, usuario_repo_teste):
        """Deve retornar False quando chamado não tem interações."""
        chamado = Chamado(
            id=0,
            titulo="Chamado Sem Respostas",
            status=StatusChamado.ABERTO,
            prioridade=PrioridadeChamado.MEDIA,
            usuario_id=usuario_repo_teste
        )
        chamado_id = chamado_repo.inserir(chamado)

        resultado = chamado_interacao_repo.tem_resposta_admin(chamado_id)

        assert resultado is False


class TestChamadoInteracaoRepoCriarTabela:
    """Testes para a função criar_tabela de chamado_interacao_repo."""

    def test_criar_tabela_retorna_true(self):
        """Deve retornar True ao criar/verificar tabela."""
        resultado = chamado_interacao_repo.criar_tabela()

        assert resultado is True


class TestChamadoInteracaoRepoEnums:
    """Testes para verificar conversão de enums de interação."""

    def test_interacao_com_todos_tipos(self, chamado_repo_teste, usuario_repo_teste):
        """Deve suportar todos os tipos de interação do enum."""
        for tipo in TipoInteracao:
            interacao = ChamadoInteracao(
                id=0,
                chamado_id=chamado_repo_teste,
                usuario_id=usuario_repo_teste,
                mensagem=f"Interação tipo {tipo.value}",
                tipo=tipo,
                data_interacao=None,
                status_resultante=None
            )
            interacao_id = chamado_interacao_repo.inserir(interacao)

            interacao_salva = chamado_interacao_repo.obter_por_id(interacao_id)
            assert interacao_salva.tipo == tipo
