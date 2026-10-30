"""
entidad.py
----------
Clase abstracta Entidad: representa cualquier elemento general del sistema
(clientes, servicios, reservas). Define lo que todos tienen en común:
un identificador único, una fecha de creación y la obligación de saber
validarse y describirse.
"""

# ABC y abstractmethod permiten declarar clases y métodos abstractos.
from abc import ABC, abstractmethod
# datetime se usa para guardar la fecha y hora de creación.
from datetime import datetime
class Entidad(ABC):
    """Clase base abstracta para todas las entidades del sistema."""

    # Diccionario de contadores: uno por prefijo (CLI, SRV, RES).
    _contadores = {}

    # Constructor común a todas las entidades.
    def __init__(self, prefijo):
        # Suma 1 al contador de este prefijo (empieza en 0 si es el primero).
        Entidad._contadores[prefijo] = Entidad._contadores.get(prefijo, 0) + 1
        # Identificador único, por ejemplo "CLI-0001" o "RES-0003" (atributo protegido).
        self._id = f"{prefijo}-{Entidad._contadores[prefijo]:04d}"
        # Fecha y hora en que se creó el objeto.
        self._fecha_creacion = datetime.now()

    # Propiedad de solo lectura para el identificador.
    @property
    def id(self):
        # Devuelve el identificador; no hay setter, así que no se puede cambiar.
        return self._id

    # Propiedad de solo lectura para la fecha de creación.
    @property
    def fecha_creacion(self):
        # Devuelve la fecha de creación.
        return self._fecha_creacion

    # Método abstracto: cada clase hija debe definir cómo se valida.
    @abstractmethod
    def validar(self):
        """Comprueba que el objeto sea coherente; lanza una excepción si no."""

    # Método abstracto: cada clase hija debe definir cómo se describe.
    @abstractmethod
    def describir(self):
        """Devuelve un texto legible con la información del objeto."""

    # Representación en texto: reutiliza el método describir().
    def __str__(self):
        # Delega en describir(), que implementa cada clase hija.
        return self.describir()
