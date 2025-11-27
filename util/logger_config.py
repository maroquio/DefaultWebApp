"""
Módulo de configuração do sistema de logging.

Implementa rotação diária de logs com retenção configurável via .env.
"""

import logging
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path
import time

from util.config import LOG_LEVEL, LOG_RETENTION_DAYS
from util.datetime_util import agora


class DailyRotatingFileHandler(TimedRotatingFileHandler):
    """
    Handler customizado que cria arquivos com data no nome desde o início.

    Cria logs no formato: app.YYYY.MM.DD.log
    """

    def __init__(
        self, log_dir: str = 'logs', when: str = 'midnight',
        interval: int = 1, backupCount: int = LOG_RETENTION_DAYS
    ):
        self.log_dir = log_dir
        Path(log_dir).mkdir(exist_ok=True)

        # Nome do arquivo com data de hoje
        filename = self._get_filename_for_date(agora())

        super().__init__(
            filename=filename,
            when=when,
            interval=interval,
            backupCount=backupCount
        )

    def _get_filename_for_date(self, dt):
        """Gera nome do arquivo no formato app.YYYY.MM.DD.log"""
        return os.path.join(
            self.log_dir,
            f"app.{dt.strftime('%Y.%m.%d')}.log"
        )

    def doRollover(self):
        """Override do rollover para criar novo arquivo com nome correto"""
        if self.stream:
            self.stream.close()
            self.stream = None

        # Novo arquivo com data atual (após meia-noite)
        self.baseFilename = self._get_filename_for_date(agora())

        # Deletar arquivos antigos além do backupCount
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)

        # Atualizar próximo rollover
        currentTime = int(time.time())
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        self.rolloverAt = newRolloverAt

        # Abrir novo arquivo
        if not self.delay:
            self.stream = self._open()


def configurar_logger() -> logging.Logger:
    """
    Configura sistema de logging profissional com rotação diária.

    Configurações:
    - Rotação à meia-noite
    - Retenção de logs configurável via LOG_RETENTION_DAYS (padrão: 30 dias)
    - Formato padronizado com timestamp
    - Nível de log configurável via LOG_LEVEL

    Returns:
        Logger configurado e pronto para uso
    """
    # Configurar formato
    formato = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler customizado que cria arquivos com data desde o início
    file_handler = DailyRotatingFileHandler(
        log_dir='logs',
        when='midnight',
        interval=1,
        backupCount=LOG_RETENTION_DAYS
    )
    file_handler.setFormatter(formato)

    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formato)

    # Configurar logger raiz
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Logger global para importação
logger = configurar_logger()
