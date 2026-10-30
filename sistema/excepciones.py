"""
excepciones.py
--------------
Excepciones personalizadas del sistema Software FJ.

Todas heredan de una excepción base (SoftwareFJError) para que el programa
principal pueda capturar cualquier error propio del sistema con un solo
bloque except, sin atrapar por accidente errores de Python que indiquen
un fallo de programación.
"""


# Excepción base de la que heredan todas las demás excepciones del sistema.
class SoftwareFJError(Exception):
    """Error general del sistema Software FJ."""

    # Constructor: recibe el mensaje y, opcionalmente, un código de error.
    def __init__(self, mensaje, codigo="FJ-000"):
        # Llama al constructor de Exception para guardar el mensaje.
        super().__init__(mensaje)
        # Guarda el mensaje como atributo para usarlo en los logs.
        self.mensaje = mensaje
        # Guarda el código para identificar el tipo de error en los logs.
        self.codigo = codigo

    # Representación en texto: "[código] mensaje".
    def __str__(self):
        # Devuelve el código seguido del mensaje.
        return f"[{self.codigo}] {self.mensaje}"


# ---------------------------------------------------------------------------
# Errores de validación de datos
# ---------------------------------------------------------------------------

# Se lanza cuando un dato tiene un formato o valor inválido.
class DatoInvalidoError(SoftwareFJError):
    """Un dato no cumple las reglas de validación (formato, rango, tipo)."""

    # Constructor: indica el campo que falló y el motivo.
    def __init__(self, campo, motivo):
        # Guarda el nombre del campo para poder consultarlo después.
        self.campo = campo
        # Construye el mensaje y asigna el código FJ-100.
        super().__init__(f"Dato inválido en '{campo}': {motivo}", "FJ-100")


# Se lanza cuando falta un parámetro obligatorio.
class ParametroFaltanteError(SoftwareFJError):
    """Falta un parámetro obligatorio para completar una operación."""

    # Constructor: recibe el nombre del parámetro que falta.
    def __init__(self, parametro):
        # Guarda el nombre del parámetro.
        self.parametro = parametro
        # Construye el mensaje y asigna el código FJ-101.
        super().__init__(f"Falta el parámetro obligatorio '{parametro}'", "FJ-101")


# ---------------------------------------------------------------------------
# Errores de clientes
# ---------------------------------------------------------------------------

# Se lanza cuando se intenta registrar un cliente que ya existe.
class ClienteDuplicadoError(SoftwareFJError):
    """Ya existe un cliente registrado con el mismo documento."""

    # Constructor: recibe el documento repetido.
    def __init__(self, documento):
        # Construye el mensaje y asigna el código FJ-200.
        super().__init__(f"Ya existe un cliente con documento {documento}", "FJ-200")


# Se lanza cuando se busca un cliente que no está registrado.
class ClienteNoEncontradoError(SoftwareFJError):
    """No existe un cliente con el documento indicado."""

    # Constructor: recibe el documento buscado.
    def __init__(self, documento):
        # Construye el mensaje y asigna el código FJ-201.
        super().__init__(f"No existe un cliente con documento {documento}", "FJ-201")


# ---------------------------------------------------------------------------
# Errores de servicios
# ---------------------------------------------------------------------------

# Se lanza cuando un servicio no está disponible para reservarse.
class ServicioNoDisponibleError(SoftwareFJError):
    """El servicio existe pero no se puede reservar en este momento."""

    # Constructor: recibe el nombre del servicio y el motivo.
    def __init__(self, servicio, motivo="no está disponible"):
        # Construye el mensaje y asigna el código FJ-300.
        super().__init__(f"El servicio '{servicio}' {motivo}", "FJ-300")


# Se lanza cuando se busca un servicio que no existe.
class ServicioNoEncontradoError(SoftwareFJError):
    """No existe un servicio con el código indicado."""

    # Constructor: recibe el código buscado.
    def __init__(self, codigo_servicio):
        # Construye el mensaje y asigna el código FJ-301.
        super().__init__(f"No existe un servicio con código {codigo_servicio}", "FJ-301")


# ---------------------------------------------------------------------------
# Errores de reservas y cálculos
# ---------------------------------------------------------------------------

# Se lanza cuando una reserva no cumple las condiciones necesarias.
class ReservaInvalidaError(SoftwareFJError):
    """La reserva no puede crearse o procesarse con los datos dados."""

    # Constructor: recibe el motivo del rechazo.
    def __init__(self, motivo):
        # Construye el mensaje y asigna el código FJ-400.
        super().__init__(f"Reserva inválida: {motivo}", "FJ-400")


# Se lanza cuando se intenta una operación que el estado actual no permite.
class OperacionNoPermitidaError(SoftwareFJError):
    """La operación no está permitida en el estado actual del objeto."""

    # Constructor: recibe la operación y el estado actual.
    def __init__(self, operacion, estado):
        # Construye el mensaje y asigna el código FJ-401.
        super().__init__(
            f"No se puede '{operacion}' una reserva en estado '{estado}'", "FJ-401"
        )


# Se lanza cuando un cálculo produce un resultado incoherente.
class CalculoInconsistenteError(SoftwareFJError):
    """El resultado de un cálculo no es coherente (por ejemplo, costo negativo)."""

    # Constructor: recibe la descripción del problema.
    def __init__(self, detalle):
        # Construye el mensaje y asigna el código FJ-500.
        super().__init__(f"Cálculo inconsistente: {detalle}", "FJ-500")
