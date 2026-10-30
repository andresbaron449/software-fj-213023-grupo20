"""
gestor.py
---------
Clase GestorSoftwareFJ: administra las listas internas de clientes,
servicios y reservas (no se usa ninguna base de datos).

Es la "fachada" del sistema: el programa principal solo habla con el
gestor, y el gestor se encarga de buscar, validar y registrar en el log.
"""

# Clases del dominio.
from .cliente import Cliente
from .reserva import Reserva
from .servicios import Servicio
# Excepciones personalizadas.
from .excepciones import (
    ClienteDuplicadoError,
    ClienteNoEncontradoError,
    ServicioNoEncontradoError,
)
# Registrador de eventos compartido.
from .logger import obtener_logger

# Registrador del módulo.
log = obtener_logger()


class GestorSoftwareFJ:
    """Administra clientes, servicios y reservas en listas internas."""

    # Constructor: crea las tres listas vacías.
    def __init__(self):
        # Lista privada de clientes registrados.
        self.__clientes = []
        # Lista privada de servicios ofrecidos.
        self.__servicios = []
        # Lista privada de reservas creadas.
        self.__reservas = []
        # Registra el inicio del sistema.
        log.info("Gestor Software FJ iniciado")

    # ---------------- clientes ----------------

    def registrar_cliente(self, nombre, documento, correo, telefono=None):
        """Crea un cliente, verifica que no esté repetido y lo guarda."""
        # Busca si ya existe un cliente con ese documento.
        if any(c.documento == str(documento).strip() for c in self.__clientes):
            # Lanza la excepción de cliente duplicado.
            raise ClienteDuplicadoError(documento)
        # Crea el cliente (el constructor valida y puede lanzar excepciones).
        cliente = Cliente(nombre, documento, correo, telefono)
        # Agrega el cliente a la lista.
        self.__clientes.append(cliente)
        # Registra el evento en el log.
        log.info(f"Cliente registrado: {cliente.describir()}")
        # Devuelve el cliente creado.
        return cliente

    def buscar_cliente(self, documento):
        """Devuelve el cliente con ese documento o lanza una excepción."""
        # Recorre la lista de clientes.
        for cliente in self.__clientes:
            # Compara el documento.
            if cliente.documento == str(documento):
                # Devuelve el cliente encontrado.
                return cliente
        # Si no lo encontró, lanza la excepción.
        raise ClienteNoEncontradoError(documento)

    # ---------------- servicios ----------------

    def agregar_servicio(self, servicio):
        """Agrega un servicio ya creado al catálogo."""
        # Solo se aceptan objetos de tipo Servicio.
        if not isinstance(servicio, Servicio):
            # Lanza un TypeError (error de programación, no de datos).
            raise TypeError("solo se pueden agregar objetos Servicio")
        # Valida el servicio.
        servicio.validar()
        # Agrega el servicio a la lista.
        self.__servicios.append(servicio)
        # Registra el evento en el log.
        log.info(f"Servicio agregado: {servicio.describir()}")
        # Devuelve el servicio.
        return servicio

    def buscar_servicio(self, id_servicio):
        """Devuelve el servicio con ese identificador o lanza una excepción."""
        # Recorre la lista de servicios.
        for servicio in self.__servicios:
            # Compara el identificador.
            if servicio.id == id_servicio:
                # Devuelve el servicio encontrado.
                return servicio
        # Si no lo encontró, lanza la excepción.
        raise ServicioNoEncontradoError(id_servicio)

    # ---------------- reservas ----------------

    def crear_reserva(self, documento, id_servicio, duracion, descuento=None, **parametros):
        """Busca cliente y servicio, crea la reserva y la confirma."""
        # Busca el cliente (puede lanzar ClienteNoEncontradoError).
        cliente = self.buscar_cliente(documento)
        # Busca el servicio (puede lanzar ServicioNoEncontradoError).
        servicio = self.buscar_servicio(id_servicio)
        # Crea la reserva (valida sus datos).
        reserva = Reserva(cliente, servicio, duracion, descuento, **parametros)
        # Guarda la reserva en la lista aunque luego falle la confirmación,
        # para dejar registro de todos los intentos.
        self.__reservas.append(reserva)
        # Confirma la reserva (puede lanzar ReservaInvalidaError encadenada).
        reserva.confirmar()
        # Devuelve la reserva confirmada.
        return reserva

    def buscar_reserva(self, id_reserva):
        """Devuelve la reserva con ese identificador o None."""
        # next() devuelve la primera coincidencia o None si no hay.
        return next((r for r in self.__reservas if r.id == id_reserva), None)

    # ---------------- consultas ----------------

    # Devuelve una copia de la lista de clientes (para no exponer la original).
    def listar_clientes(self):
        # list() crea una copia.
        return list(self.__clientes)

    # Devuelve una copia de la lista de servicios.
    def listar_servicios(self):
        # list() crea una copia.
        return list(self.__servicios)

    # Devuelve una copia de la lista de reservas.
    def listar_reservas(self):
        # list() crea una copia.
        return list(self.__reservas)

    def total_facturado(self):
        """Suma el costo de las reservas procesadas."""
        # Suma solo las reservas en estado PROCESADA.
        return sum(r.costo for r in self.__reservas if r.estado == Reserva.PROCESADA)
