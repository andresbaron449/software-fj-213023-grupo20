"""
reserva.py
----------
Clase Reserva: une un cliente, un servicio, una duración y un estado.

Ciclo de vida de una reserva:

    PENDIENTE --confirmar()--> CONFIRMADA --procesar()--> PROCESADA
        |   |                      |
        |   +--(error)--> RECHAZADA
        +-------cancelar()---------+--> CANCELADA

Aquí se usan todas las formas de manejo de excepciones que pide la guía:
try/except, try/except/else, try/except/finally y encadenamiento
(raise ... from ...).
"""

# Clase base abstracta.
from .entidad import Entidad
# Clases de dominio que se validan dentro de la reserva.
from .cliente import Cliente
from .servicios import AlquilerEquipo, Servicio, IVA_POR_DEFECTO
# Excepciones personalizadas.
from .excepciones import (
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    ReservaInvalidaError,
    SoftwareFJError,
)
# Registrador de eventos compartido.
from .logger import obtener_logger

# Registrador del módulo.
log = obtener_logger()


class Reserva(Entidad):
    """Reserva de un servicio por parte de un cliente."""

    # Posibles estados de una reserva.
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    PROCESADA = "PROCESADA"
    RECHAZADA = "RECHAZADA"

    # Constructor: recibe cliente, servicio, duración y parámetros extra.
    def __init__(self, cliente, servicio, duracion, descuento=None, **parametros):
        # Llama al constructor de Entidad con el prefijo "RES".
        super().__init__("RES")
        # Guarda el cliente (atributo privado).
        self.__cliente = cliente
        # Guarda el servicio (atributo privado).
        self.__servicio = servicio
        # Guarda la duración (horas o timedelta).
        self.__duracion = duracion
        # Guarda el descuento opcional.
        self.__descuento = descuento
        # Guarda los parámetros propios del servicio (personas, cantidad...).
        self.__parametros = parametros
        # Toda reserva nueva empieza en estado PENDIENTE.
        self.__estado = Reserva.PENDIENTE
        # El costo se calcula al confirmar.
        self.__costo = None
        # Valida la reserva completa.
        self.validar()

    # ---------------- propiedades de solo lectura ----------------

    # Getter del cliente.
    @property
    def cliente(self):
        # Devuelve el cliente.
        return self.__cliente

    # Getter del servicio.
    @property
    def servicio(self):
        # Devuelve el servicio.
        return self.__servicio

    # Getter del estado.
    @property
    def estado(self):
        # Devuelve el estado actual.
        return self.__estado

    # Getter del costo.
    @property
    def costo(self):
        # Devuelve el costo (None si aún no se confirma).
        return self.__costo

    # ---------------- validación ----------------

    # Implementación del método abstracto validar().
    def validar(self):
        # El cliente es obligatorio.
        if self.__cliente is None:
            # Lanza la excepción de parámetro faltante.
            raise ParametroFaltanteError("cliente")
        # Debe ser un objeto Cliente.
        if not isinstance(self.__cliente, Cliente):
            # Lanza la excepción de reserva inválida.
            raise ReservaInvalidaError("el cliente no es un objeto Cliente válido")
        # El servicio es obligatorio.
        if self.__servicio is None:
            # Lanza la excepción de parámetro faltante.
            raise ParametroFaltanteError("servicio")
        # Debe ser un objeto Servicio (o de una clase hija).
        if not isinstance(self.__servicio, Servicio):
            # Lanza la excepción de reserva inválida.
            raise ReservaInvalidaError("el servicio no es un objeto Servicio válido")
        # La duración es obligatoria.
        if self.__duracion is None:
            # Lanza la excepción de parámetro faltante.
            raise ParametroFaltanteError("duracion")
        # Si todo está bien, devuelve True.
        return True

    # ---------------- operaciones ----------------

    def confirmar(self):
        """Verifica disponibilidad, calcula el costo y confirma la reserva."""
        # Solo se puede confirmar una reserva pendiente.
        if self.__estado != Reserva.PENDIENTE:
            # Lanza la excepción de operación no permitida.
            raise OperacionNoPermitidaError("confirmar", self.__estado)
        # try/except/else/finally: el bloque completo de manejo de errores.
        try:
            # Comprueba que el servicio esté disponible.
            self.__servicio.verificar_disponibilidad()
            # Calcula el costo con IVA y descuento (polimorfismo: cada servicio calcula distinto).
            costo = self.__servicio.calcular_costo(
                self.__duracion, IVA_POR_DEFECTO, self.__descuento, **self.__parametros
            )
        except SoftwareFJError as error:
            # La reserva queda marcada como rechazada.
            self.__estado = Reserva.RECHAZADA
            # Registra el error original en el log.
            log.error(f"{self.id}: no se pudo confirmar -> {error}")
            # Encadenamiento: lanza un error de reserva conservando la causa original.
            raise ReservaInvalidaError(
                f"{self.id} rechazada para {self.__cliente.nombre}"
            ) from error
        else:
            # Solo si no hubo errores: guarda el costo.
            self.__costo = costo
            # Si es un alquiler de equipos, aparta las unidades del inventario.
            if isinstance(self.__servicio, AlquilerEquipo):
                # Descuenta la cantidad pedida.
                self.__servicio.apartar(self.__parametros.get("cantidad", 1))
            # Cambia el estado a CONFIRMADA.
            self.__estado = Reserva.CONFIRMADA
            # Registra el evento en el log.
            log.info(f"{self.id} confirmada | {self.__cliente.nombre} | "
                     f"{self.__servicio.nombre} | ${self.__costo:,.2f}")
        finally:
            # Se ejecuta siempre, haya error o no: deja constancia del intento.
            log.debug(f"{self.id}: intento de confirmación finalizado (estado={self.__estado})")
        # Devuelve el costo calculado.
        return self.__costo

    def cancelar(self, motivo="sin motivo"):
        """Cancela la reserva si todavía no ha sido procesada."""
        # No se puede cancelar una reserva cancelada, procesada o rechazada.
        if self.__estado in (Reserva.CANCELADA, Reserva.PROCESADA, Reserva.RECHAZADA):
            # Lanza la excepción de operación no permitida.
            raise OperacionNoPermitidaError("cancelar", self.__estado)
        # Si estaba confirmada y es un alquiler de equipos, devuelve las unidades.
        if self.__estado == Reserva.CONFIRMADA and isinstance(self.__servicio, AlquilerEquipo):
            # Libera la cantidad que se había apartado.
            self.__servicio.liberar(self.__parametros.get("cantidad", 1))
        # Cambia el estado a CANCELADA.
        self.__estado = Reserva.CANCELADA
        # Registra el evento en el log.
        log.info(f"{self.id} cancelada ({motivo})")

    def procesar(self):
        """Procesa (cobra y cierra) una reserva confirmada."""
        # try/finally: el bloque finally se ejecuta aunque se lance una excepción.
        try:
            # Solo se procesan reservas confirmadas.
            if self.__estado != Reserva.CONFIRMADA:
                # Lanza la excepción de operación no permitida.
                raise OperacionNoPermitidaError("procesar", self.__estado)
            # Cambia el estado a PROCESADA.
            self.__estado = Reserva.PROCESADA
            # Registra el evento en el log.
            log.info(f"{self.id} procesada | cobro de ${self.__costo:,.2f}")
        finally:
            # Se ejecuta siempre: deja constancia en el log.
            log.debug(f"{self.id}: intento de procesamiento finalizado (estado={self.__estado})")
        # Devuelve la propia reserva para poder mostrarla.
        return self

    # Implementación del método abstracto describir().
    def describir(self):
        # Formatea el costo o indica que está pendiente.
        costo = f"${self.__costo:,.2f}" if self.__costo is not None else "por calcular"
        # Devuelve la descripción de la reserva.
        return (f"{self.id} | {self.__cliente.nombre} | {self.__servicio.nombre} | "
                f"{self.__estado} | {costo}")
