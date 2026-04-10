"""Configuração de logging para o app Tá Pago?.

Importar no topo de Painel.py (entry point do Streamlit) para garantir
que os handlers sejam registrados antes de qualquer outro módulo logar.
"""
import logging
import sys


def setup_logging() -> None:
    """Configura o handler padrão se ainda não foi configurado."""
    root = logging.getLogger()
    if root.handlers:
        return  # já configurado (evita duplicatas em reruns do Streamlit)

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    # Reduzir verbosidade de bibliotecas ruidosas
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
