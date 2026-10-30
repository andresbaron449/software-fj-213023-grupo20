"""
servicios.py
------------
Clase abstracta Servicio y los tres servicios especializados que ofrece
Software FJ:

    * ReservaSala      -> alquiler de salas de reuniones por horas.
    * AlquilerEquipo   -> alquiler de equipos (portátiles, proyectores...).
    * Asesoria         -> asesorías especializadas con un consultor.

Cada servicio sobrescribe (polimorfismo) los métodos para calcular el costo,
describirse y validar sus parámetros. El cálculo de costos está
"sobrecargado" de dos maneras, porque Python no permite definir dos métodos
con el mismo nombre:

    1. Parámetros opcionales: calcular_costo(duracion),
       calcular_costo(duracion, impuesto), calcular_costo(duracion, impuesto, descuento).
    2. functools.singledispatchmethod: la duración puede llegar como número
       de horas (int/float) o como timedelta, y se elige la variante según el tipo.
"""

# ABC y abstractmethod para declarar la clase y los métodos abstractos.
from abc import abstractmethod
# timedelta representa una duración de tiempo (por ejemplo, 2 horas).
from datetime import timedelta
# singledispatchmethod elige qué versión del método ejecutar según el tipo del argumento.
from functools import singledispatchmethod

# Clase base abstracta común a todas las entidades.
from .entidad import Entidad
# Excepciones personalizadas que pueden lanzar los servicios.
from .excepciones import (
    CalculoInconsistenteError,
    DatoInvalidoError,
    ParametroFaltanteError,
    ServicioNoDisponibleError,
)

# IVA por defecto en Colombia (19 %).
IVA_POR_DEFECTO = 0.19


class Servicio(Entidad):
    """Servicio genérico de Software FJ (clase abstracta)."""

    # Constructor común a todos los servicios.
    def __init__(self, nombre, tarifa_hora, disponible=True):
        # Llama al constructor de Entidad con el prefijo "SRV".
        super().__init__("SRV")
        # Si no se envía nombre, falta un parámetro obligatorio.
        if not nombre:
            # Lanza la excepción de parámetro faltante.
            raise ParametroFaltanteError("nombre del servicio")
        # Guarda el nombre (atributo protegido).
        self._nombre = str(nombre).strip()
        # Guarda la tarifa por hora usando el setter que la valida.
        self.tarifa_hora = tarifa_hora
        # Indica si el servicio se puede reservar (atributo protegido).
        self._disponible = bool(disponible)

    # Getter del nombre.
    @property
    def nombre(self):
        # Devuelve el nombre del servicio.
        return self._nombre

    # Getter de la tarifa por hora.
    @property
    def tarifa_hora(self):
        # Devuelve la tarifa.
        return self._tarifa_hora

    # Setter de la tarifa: debe ser un número positivo.
    @tarifa_hora.setter
    def tarifa_hora(self, valor):
        # Comprueba que sea un número (int o float, pero no bool).
        if not isinstance(valor, (int, float)) or isinstance(valor, bool):
            # Lanza la excepción si no es un número.
            raise DatoInvalidoError("tarifa_hora", "debe ser un número")
        # Comprueba que sea mayor que cero.
        if valor <= 0:
            # Lanza la excepción si es cero o negativa.
            raise DatoInvalidoError("tarifa_hora", "debe ser mayor que cero")
        # Guarda la tarifa.
        self._tarifa_hora = float(valor)

    # Getter de la disponibilidad.
    @property
    def disponible(self):
        # Devuelve True si el servicio se puede reservar.
        return self._disponible

    # Marca el servicio como no disponible (por ejemplo, en mantenimiento).
    def deshabilitar(self):
        # Cambia el estado a no disponible.
        self._disponible = False

    # Marca el servicio como disponible otra vez.
    def habilitar(self):
        # Cambia el estado a disponible.
        self._disponible = True

    # Comprueba la disponibilidad y lanza una excepción si no lo está.
    def verificar_disponibilidad(self):
        # Si no está disponible, no se puede reservar.
        if not self._disponible:
            # Lanza la excepción de servicio no disponible.
            raise ServicioNoDisponibleError(self.nombre)

    # ------------------------------------------------------------------
    # Conversión de la duración: método "sobrecargado" por tipo de dato
    # ------------------------------------------------------------------

    # Versión general: se ejecuta si el tipo no tiene una variante registrada.
    @singledispatchmethod
    def a_horas(self, duracion):
        # Ningún otro tipo es válido como duración.
        raise DatoInvalidoError(
            "duracion", f"tipo no soportado ({type(duracion).__name__})"
        )

    # Variante para números enteros: ya son horas.
    @a_horas.register
    def _(self, duracion: int):
        # Convierte a float para operar de forma uniforme.
        return float(duracion)

    # Variante para números decimales: ya son horas.
    @a_horas.register
    def _(self, duracion: float):
        # Devuelve el mismo valor.
        return duracion

    # Variante para timedelta: convierte segundos a horas.
    @a_horas.register
    def _(self, duracion: timedelta):
        # total_seconds() / 3600 da el número de horas.
        return duracion.total_seconds() / 3600

    # ------------------------------------------------------------------
    # Cálculo de costos con parámetros opcionales (sobrecarga simulada)
    # ------------------------------------------------------------------

    def calcular_costo(self, duracion, impuesto=None, descuento=None, **parametros):
        """
        Variantes de uso:
            calcular_costo(2)                 -> costo sin impuesto ni descuento
            calcular_costo(2, 0.19)           -> costo con impuesto del 19 %
            calcular_costo(2, 0.19, 0.10)     -> con impuesto y 10 % de descuento
            calcular_costo(timedelta(hours=2), descuento=0.05)
        Los **parametros extra dependen de cada servicio (personas, cantidad...).
        """
        # Convierte la duración a horas (usa la variante según el tipo).
        horas = self.a_horas(duracion)
        # Valida los parámetros propios de cada servicio (polimorfismo).
        self.validar_parametros(horas, **parametros)
        # Calcula el costo base, que define cada clase hija (polimorfismo).
        subtotal = self._costo_base(horas, **parametros)
        # Si hay descuento, debe estar entre 0 y 0.5 (máximo 50 %).
        if descuento is not None:
            # Valida el rango del descuento.
            if not 0 <= descuento <= 0.5:
                # Lanza la excepción si el descuento está fuera de rango.
                raise DatoInvalidoError("descuento", "debe estar entre 0 y 0.5")
            # Aplica el descuento al subtotal.
            subtotal *= 1 - descuento
        # Si hay impuesto, debe estar entre 0 y 1.
        if impuesto is not None:
            # Valida el rango del impuesto.
            if not 0 <= impuesto <= 1:
                # Lanza la excepción si el impuesto está fuera de rango.
                raise DatoInvalidoError("impuesto", "debe estar entre 0 y 1")
            # Suma el impuesto al subtotal.
            subtotal *= 1 + impuesto
        # Un costo negativo o cero indica un error de cálculo.
        if subtotal <= 0:
            # Lanza la excepción de cálculo inconsistente.
            raise CalculoInconsistenteError(f"costo resultante {subtotal:.2f}")
        # Devuelve el costo redondeado a dos decimales.
        return round(subtotal, 2)

    # ------------------------------------------------------------------
    # Métodos que cada servicio debe sobrescribir
    # ------------------------------------------------------------------

    # Costo antes de impuestos y descuentos.
    @abstractmethod
    def _costo_base(self, horas, **parametros):
        """Costo del servicio antes de impuestos y descuentos."""

    # Validación de los parámetros propios del servicio.
    @abstractmethod
    def validar_parametros(self, horas, **parametros):
        """Lanza una excepción si los parámetros no son válidos."""

    # Validación general del servicio (implementa el método de Entidad).
    def validar(self):
        # La tarifa debe ser positiva.
        if self._tarifa_hora <= 0:
            # Lanza la excepción si no lo es.
            raise DatoInvalidoError("tarifa_hora", "debe ser mayor que cero")
        # Si todo está bien, devuelve True.
        return True

    # Validación común de la duración, la usan todas las clases hijas.
    def _validar_horas(self, horas, minimo, maximo):
        # La duración debe estar dentro del rango permitido.
        if not minimo <= horas <= maximo:
            # Lanza la excepción con el rango permitido.
            raise DatoInvalidoError(
                "duracion", f"debe estar entre {minimo} y {maximo} horas (recibido {horas})"
            )


# ======================================================================
# Servicio 1: Reserva de salas
# ======================================================================

class ReservaSala(Servicio):
    """Alquiler de salas de reuniones por horas."""

    # Constructor: añade la capacidad máxima de la sala.
    def __init__(self, nombre, tarifa_hora, capacidad, disponible=True):
        # Inicializa la parte común con el constructor de Servicio.
        super().__init__(nombre, tarifa_hora, disponible)
        # La capacidad debe ser un entero positivo.
        if not isinstance(capacidad, int) or capacidad <= 0:
            # Lanza la excepción si no es válida.
            raise DatoInvalidoError("capacidad", "debe ser un entero mayor que cero")
        # Guarda la capacidad (atributo protegido).
        self._capacidad = capacidad

    # Sobrescribe la validación de parámetros.
    def validar_parametros(self, horas, personas=None, **_):
        # Una sala se reserva entre 1 y 12 horas.
        self._validar_horas(horas, 1, 12)
        # Es obligatorio indicar el número de personas.
        if personas is None:
            # Lanza la excepción de parámetro faltante.
            raise ParametroFaltanteError("personas")
        # El número de personas debe estar entre 1 y la capacidad.
        if not 1 <= personas <= self._capacidad:
            # Lanza la excepción indicando la capacidad.
            raise DatoInvalidoError(
                "personas", f"la sala admite de 1 a {self._capacidad} personas (recibido {personas})"
            )

    # Sobrescribe el cálculo del costo base.
    def _costo_base(self, horas, personas=1, **_):
        # Costo por horas.
        costo = self.tarifa_hora * horas
        # Si la sala se usa a más del 80 % de capacidad, se cobra 10 % de aseo.
        if personas > self._capacidad * 0.8:
            # Suma el recargo.
            costo *= 1.10
        # Devuelve el costo base.
        return costo

    # Sobrescribe la descripción.
    def describir(self):
        # Texto que indica el estado del servicio.
        estado = "Disponible" if self.disponible else "No disponible"
        # Devuelve la descripción de la sala.
        return (f"{self.id} | Sala '{self.nombre}' | capacidad {self._capacidad} personas | "
                f"${self.tarifa_hora:,.0f}/hora | {estado}")


# ======================================================================
# Servicio 2: Alquiler de equipos
# ======================================================================

class AlquilerEquipo(Servicio):
    """Alquiler de equipos tecnológicos (portátiles, proyectores, etc.)."""

    # Valor fijo del depósito de garantía por cada unidad.
    DEPOSITO_POR_UNIDAD = 20000

    # Constructor: añade el tipo de equipo y las unidades disponibles.
    def __init__(self, nombre, tarifa_hora, unidades, disponible=True):
        # Inicializa la parte común con el constructor de Servicio.
        super().__init__(nombre, tarifa_hora, disponible)
        # Las unidades deben ser un entero no negativo.
        if not isinstance(unidades, int) or unidades < 0:
            # Lanza la excepción si no es válido.
            raise DatoInvalidoError("unidades", "debe ser un entero mayor o igual a cero")
        # Guarda las unidades en inventario (atributo protegido).
        self._unidades = unidades

    # Getter de las unidades disponibles.
    @property
    def unidades(self):
        # Devuelve el inventario actual.
        return self._unidades

    # Sobrescribe la validación de parámetros.
    def validar_parametros(self, horas, cantidad=None, **_):
        # Un equipo se alquila entre 1 y 72 horas.
        self._validar_horas(horas, 1, 72)
        # Es obligatorio indicar la cantidad de equipos.
        if cantidad is None:
            # Lanza la excepción de parámetro faltante.
            raise ParametroFaltanteError("cantidad")
        # La cantidad debe ser al menos 1.
        if cantidad < 1:
            # Lanza la excepción si es menor que 1.
            raise DatoInvalidoError("cantidad", "debe ser al menos 1")
        # No se pueden alquilar más unidades de las que hay.
        if cantidad > self._unidades:
            # Lanza la excepción de servicio no disponible.
            raise ServicioNoDisponibleError(
                self.nombre, f"solo tiene {self._unidades} unidades (se pidieron {cantidad})"
            )

    # Sobrescribe el cálculo del costo base.
    def _costo_base(self, horas, cantidad=1, **_):
        # Costo = tarifa x horas x cantidad + depósito por unidad.
        return self.tarifa_hora * horas * cantidad + self.DEPOSITO_POR_UNIDAD * cantidad

    # Descuenta unidades del inventario al confirmar una reserva.
    def apartar(self, cantidad):
        # Vuelve a comprobar que haya suficientes unidades.
        if cantidad > self._unidades:
            # Lanza la excepción si no alcanzan.
            raise ServicioNoDisponibleError(self.nombre, "no tiene unidades suficientes")
        # Resta las unidades apartadas.
        self._unidades -= cantidad

    # Devuelve unidades al inventario al cancelar una reserva.
    def liberar(self, cantidad):
        # Suma las unidades devueltas.
        self._unidades += cantidad

    # Sobrescribe la descripción.
    def describir(self):
        # Texto que indica el estado del servicio.
        estado = "Disponible" if self.disponible else "No disponible"
        # Devuelve la descripción del equipo.
        return (f"{self.id} | Equipo '{self.nombre}' | {self._unidades} unidades | "
                f"${self.tarifa_hora:,.0f}/hora + depósito | {estado}")


# ======================================================================
# Servicio 3: Asesorías especializadas
# ======================================================================

class Asesoria(Servicio):
    """Asesoría especializada con un consultor de Software FJ."""

    # Multiplicador de la tarifa según el nivel del consultor.
    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    # Constructor: añade la especialidad y el nivel del consultor.
    def __init__(self, nombre, tarifa_hora, especialidad, nivel="junior", disponible=True):
        # Inicializa la parte común con el constructor de Servicio.
        super().__init__(nombre, tarifa_hora, disponible)
        # La especialidad es obligatoria.
        if not especialidad:
            # Lanza la excepción de parámetro faltante.
            raise ParametroFaltanteError("especialidad")
        # El nivel debe ser uno de los definidos en NIVELES.
        if nivel not in self.NIVELES:
            # Lanza la excepción mostrando los niveles válidos.
            raise DatoInvalidoError("nivel", f"debe ser uno de {list(self.NIVELES)}")
        # Guarda la especialidad (atributo protegido).
        self._especialidad = especialidad
        # Guarda el nivel (atributo protegido).
        self._nivel = nivel

    # Sobrescribe la validación de parámetros.
    def validar_parametros(self, horas, **_):
        # Una asesoría dura entre 1 y 8 horas.
        self._validar_horas(horas, 1, 8)

    # Sobrescribe el cálculo del costo base.
    def _costo_base(self, horas, **_):
        # Costo = tarifa x horas x multiplicador del nivel.
        return self.tarifa_hora * horas * self.NIVELES[self._nivel]

    # Sobrescribe la descripción.
    def describir(self):
        # Texto que indica el estado del servicio.
        estado = "Disponible" if self.disponible else "No disponible"
        # Devuelve la descripción de la asesoría.
        return (f"{self.id} | Asesoría '{self.nombre}' | {self._especialidad} | nivel {self._nivel} | "
                f"${self.tarifa_hora:,.0f}/hora | {estado}")
