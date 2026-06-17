from typing import Dict, Any, List
import sqlite3
import threading
from repo import configuracao_repo
from util.logger_config import logger


class ConfigCache:
    """
    Cache de configurações do sistema para melhor performance.

    Thread-safe: utiliza RLock para sincronização de acesso ao cache
    em ambientes multi-thread.
    """
    _cache: Dict[str, Any] = {}
    _lock: threading.RLock = threading.RLock()

    @classmethod
    def obter(cls, chave: str, padrao: str = "") -> str:
        """
        Obtém configuração com cache e tratamento de erros.

        Thread-safe: utiliza lock para sincronização.

        Args:
            chave: Chave da configuração
            padrao: Valor padrão se não encontrado

        Returns:
            Valor da configuração ou padrão

        Raises:
            Nenhuma exceção - retorna padrao em caso de erro
        """
        with cls._lock:
            # Retorna do cache se disponível
            if chave in cls._cache:
                return cls._cache[chave]

            # Tenta buscar do banco com error handling
            try:
                config = configuracao_repo.obter_por_chave(chave)
                if config:
                    cls._cache[chave] = config.valor
                    return config.valor
                else:
                    cls._cache[chave] = padrao
                    return padrao

            except sqlite3.Error as e:
                logger.error(f"Erro ao buscar configuração '{chave}' do banco: {e}")
                # Retorna padrão em vez de crashar a aplicação
                return padrao

            except Exception as e:
                logger.critical(f"Erro crítico ao acessar configuração '{chave}': {e}")
                # Ainda retorna padrão, mas loga como crítico
                return padrao

    @classmethod
    def obter_int(cls, chave: str, padrao: int) -> int:
        """
        Obtém configuração como inteiro com cache e tratamento de erros

        Args:
            chave: Chave da configuração
            padrao: Valor padrão se não encontrado

        Returns:
            Valor da configuração convertido para int ou padrão

        Raises:
            Nenhuma exceção - retorna padrao em caso de erro
        """
        try:
            valor_str = cls.obter(chave, str(padrao))
            return int(valor_str)
        except ValueError as e:
            logger.error(f"Erro ao converter configuração '{chave}' para int: {e}")
            return padrao

    @classmethod
    def obter_bool(cls, chave: str, padrao: bool) -> bool:
        """
        Obtém configuração como booleano com cache e tratamento de erros

        Args:
            chave: Chave da configuração
            padrao: Valor padrão se não encontrado

        Returns:
            Valor da configuração convertido para bool ou padrão

        Raises:
            Nenhuma exceção - retorna padrao em caso de erro
        """
        try:
            valor_str = cls.obter(chave, str(padrao)).lower()
            # Aceita "true", "1", "yes", "sim" como verdadeiro
            return valor_str in ("true", "1", "yes", "sim", "verdadeiro")
        except Exception as e:
            logger.error(f"Erro ao converter configuração '{chave}' para bool: {e}")
            return padrao

    @classmethod
    def obter_float(cls, chave: str, padrao: float) -> float:
        """
        Obtém configuração como float com cache e tratamento de erros

        Args:
            chave: Chave da configuração
            padrao: Valor padrão se não encontrado

        Returns:
            Valor da configuração convertido para float ou padrão

        Raises:
            Nenhuma exceção - retorna padrao em caso de erro
        """
        try:
            valor_str = cls.obter(chave, str(padrao))
            return float(valor_str)
        except ValueError as e:
            logger.error(f"Erro ao converter configuração '{chave}' para float: {e}")
            return padrao

    @classmethod
    def obter_multiplos(cls, chaves: List[str], padroes: List[str]) -> Dict[str, str]:
        """
        Obtém múltiplas configurações de uma vez para melhor performance

        Args:
            chaves: Lista de chaves a buscar
            padroes: Lista de valores padrão correspondentes

        Returns:
            Dicionário com as configurações {chave: valor}

        Raises:
            Nenhuma exceção - retorna padroes em caso de erro
        """
        if len(chaves) != len(padroes):
            logger.error("obter_multiplos: número de chaves diferente de padrões")
            return dict(zip(chaves, padroes))

        resultado = {}
        for chave, padrao in zip(chaves, padroes):
            resultado[chave] = cls.obter(chave, padrao)

        return resultado

    @classmethod
    def limpar(cls):
        """
        Limpa todo o cache de configurações.

        Thread-safe: utiliza lock para sincronização.
        """
        with cls._lock:
            cls._cache = {}

    @classmethod
    def limpar_chave(cls, chave: str):
        """
        Limpa cache de uma chave específica.

        Thread-safe: utiliza lock para sincronização.
        """
        with cls._lock:
            if chave in cls._cache:
                del cls._cache[chave]


# Instância global para uso em toda a aplicação
config = ConfigCache()
