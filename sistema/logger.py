"""
logger.py
---------
Configuración del registro de eventos y errores (logs) del sistema.

Todos los módulos obtienen el mismo registrador con obtener_logger(), de
modo que cada evento y cada error queda guardado en un único archivo
(logs/software_fj.log) y también se muestra en la consola.
"""

# Módulo estándar de Python para registrar eventos.
import logging
# Módulo estándar para trabajar con rutas de archivos.
import os

# Carpeta donde se guarda el archivo de logs (relativa a la raíz del proyecto).
CARPETA_LOGS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
# Ruta completa del archivo de logs.
ARCHIVO_LOG = os.path.join(CARPETA_LOGS, "software_fj.log")
# Nombre interno del registrador que comparten todos los módulos.
NOMBRE_LOGGER = "software_fj"


def obtener_logger():
    """Devuelve el registrador del sistema, creándolo la primera vez."""
    # Obtiene (o crea) el registrador con el nombre del sistema.
    logger = logging.getLogger(NOMBRE_LOGGER)
    # Si ya tiene manejadores configurados, se devuelve tal cual (evita duplicados).
    if logger.handlers:
        # Devuelve el registrador existente.
        return logger
    # Registra desde el nivel DEBUG en adelante.
    logger.setLevel(logging.DEBUG)
    # try/except/else: crear la carpeta de logs puede fallar (permisos, disco).
    try:
        # Crea la carpeta de logs si no existe.
        os.makedirs(CARPETA_LOGS, exist_ok=True)
        # Crea el manejador que escribe en el archivo, en UTF-8 para las tildes.
        manejador_archivo = logging.FileHandler(ARCHIVO_LOG, encoding="utf-8")
    except OSError as error:
        # Si no se puede escribir en disco, avisa por consola y sigue sin archivo.
        print(f"[AVISO] No se pudo crear el archivo de logs: {error}")
    else:
        # Solo si no hubo error: define el formato de cada línea del archivo.
        manejador_archivo.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(module)-12s | %(message)s",
                "%Y-%m-%d %H:%M:%S",
            )
        )
        # Agrega el manejador de archivo al registrador.
        logger.addHandler(manejador_archivo)
    # Manejador que muestra los mensajes en la consola.
    manejador_consola = logging.StreamHandler()
    # En consola solo se muestran mensajes INFO o superiores.
    manejador_consola.setLevel(logging.INFO)
    # Formato corto para la consola.
    manejador_consola.setFormatter(logging.Formatter("   %(levelname)s: %(message)s"))
    # Agrega el manejador de consola al registrador.
    logger.addHandler(manejador_consola)
    # Evita que los mensajes se dupliquen en el registrador raíz de Python.
    logger.propagate = False
    # Devuelve el registrador ya configurado.
    return logger
