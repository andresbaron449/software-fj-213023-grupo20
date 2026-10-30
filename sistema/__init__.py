"""
Paquete 'sistema' de Software FJ.

Reúne las clases del sistema integral de gestión de clientes, servicios y
reservas para que se puedan importar desde un solo lugar.
"""

# Excepciones personalizadas.
from .excepciones import *  # noqa: F401,F403
# Clase abstracta base.
from .entidad import Entidad  # noqa: F401
# Clase Cliente.
from .cliente import Cliente  # noqa: F401
# Servicio abstracto y servicios especializados.
from .servicios import Servicio, ReservaSala, AlquilerEquipo, Asesoria  # noqa: F401
# Clase Reserva.
from .reserva import Reserva  # noqa: F401
# Gestor con las listas internas.
from .gestor import GestorSoftwareFJ  # noqa: F401
# Registrador de eventos.
from .logger import obtener_logger, ARCHIVO_LOG  # noqa: F401
