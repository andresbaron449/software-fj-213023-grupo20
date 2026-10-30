"""
cliente.py
----------
Clase Cliente: guarda los datos personales de un cliente de Software FJ.

Los datos están encapsulados (atributos privados con doble guion bajo) y
solo se modifican a través de propiedades que validan cada valor. Si un
dato es inválido se lanza DatoInvalidoError o ParametroFaltanteError.
"""

# re permite validar formatos con expresiones regulares (correo, teléfono).
import re

# Clase base abstracta de la que hereda Cliente.
from .entidad import Entidad
# Excepciones personalizadas que usa la validación.
from .excepciones import DatoInvalidoError, ParametroFaltanteError

# Patrón para validar correos: texto@texto.dominio
PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
# Patrón para validar teléfonos: 7 a 10 dígitos.
PATRON_TELEFONO = re.compile(r"^\d{7,10}$")
# Patrón para validar documentos: 6 a 12 dígitos.
PATRON_DOCUMENTO = re.compile(r"^\d{6,12}$")


class Cliente(Entidad):
    """Cliente de Software FJ con datos personales validados y encapsulados."""

    # Constructor: recibe los datos del cliente y los valida uno por uno.
    def __init__(self, nombre, documento, correo, telefono=None):
        # Llama al constructor de Entidad con el prefijo "CLI".
        super().__init__("CLI")
        # Asigna el nombre a través de su propiedad (que valida).
        self.nombre = nombre
        # Asigna el documento a través de su propiedad (que valida).
        self.documento = documento
        # Asigna el correo a través de su propiedad (que valida).
        self.correo = correo
        # Asigna el teléfono (opcional) a través de su propiedad.
        self.telefono = telefono
        # Valida el objeto completo al terminar de construirlo.
        self.validar()

    # ---------------- nombre ----------------

    # Getter del nombre.
    @property
    def nombre(self):
        # Devuelve el nombre guardado en el atributo privado.
        return self.__nombre

    # Setter del nombre: valida antes de guardar.
    @nombre.setter
    def nombre(self, valor):
        # Si el valor es None o vacío, falta el parámetro.
        if valor is None or str(valor).strip() == "":
            # Lanza la excepción de parámetro faltante.
            raise ParametroFaltanteError("nombre")
        # Quita espacios sobrantes al inicio y al final.
        valor = str(valor).strip()
        # El nombre solo puede tener letras (con tildes) y espacios.
        if not all(c.isalpha() or c.isspace() for c in valor):
            # Lanza la excepción de dato inválido.
            raise DatoInvalidoError("nombre", "solo puede contener letras y espacios")
        # El nombre debe tener al menos 3 caracteres.
        if len(valor) < 3:
            # Lanza la excepción de dato inválido.
            raise DatoInvalidoError("nombre", "debe tener al menos 3 caracteres")
        # Guarda el nombre con la primera letra de cada palabra en mayúscula.
        self.__nombre = valor.title()

    # ---------------- documento ----------------

    # Getter del documento.
    @property
    def documento(self):
        # Devuelve el documento guardado.
        return self.__documento

    # Setter del documento: valida el formato.
    @documento.setter
    def documento(self, valor):
        # Si no se envió documento, falta el parámetro.
        if valor is None or str(valor).strip() == "":
            # Lanza la excepción de parámetro faltante.
            raise ParametroFaltanteError("documento")
        # Convierte a texto y quita espacios.
        valor = str(valor).strip()
        # Comprueba que tenga entre 6 y 12 dígitos.
        if not PATRON_DOCUMENTO.match(valor):
            # Lanza la excepción de dato inválido.
            raise DatoInvalidoError("documento", "debe tener entre 6 y 12 dígitos")
        # Guarda el documento.
        self.__documento = valor

    # ---------------- correo ----------------

    # Getter del correo.
    @property
    def correo(self):
        # Devuelve el correo guardado.
        return self.__correo

    # Setter del correo: valida el formato.
    @correo.setter
    def correo(self, valor):
        # Si no se envió correo, falta el parámetro.
        if valor is None or str(valor).strip() == "":
            # Lanza la excepción de parámetro faltante.
            raise ParametroFaltanteError("correo")
        # Convierte a minúsculas y quita espacios.
        valor = str(valor).strip().lower()
        # Comprueba el formato usuario@dominio.ext
        if not PATRON_CORREO.match(valor):
            # Lanza la excepción de dato inválido.
            raise DatoInvalidoError("correo", f"'{valor}' no tiene un formato válido")
        # Guarda el correo.
        self.__correo = valor

    # ---------------- teléfono ----------------

    # Getter del teléfono.
    @property
    def telefono(self):
        # Devuelve el teléfono guardado (puede ser None).
        return self.__telefono

    # Setter del teléfono: es opcional, pero si se envía debe ser válido.
    @telefono.setter
    def telefono(self, valor):
        # Si no se envía teléfono, se guarda None (es opcional).
        if valor is None:
            # Guarda None.
            self.__telefono = None
            # Termina el método.
            return
        # Convierte a texto y quita espacios.
        valor = str(valor).strip()
        # Comprueba que tenga entre 7 y 10 dígitos.
        if not PATRON_TELEFONO.match(valor):
            # Lanza la excepción de dato inválido.
            raise DatoInvalidoError("telefono", "debe tener entre 7 y 10 dígitos")
        # Guarda el teléfono.
        self.__telefono = valor

    # ---------------- métodos de Entidad ----------------

    # Implementación del método abstracto validar().
    def validar(self):
        # Comprueba que los datos obligatorios estén presentes.
        for campo in ("nombre", "documento", "correo"):
            # getattr obtiene el valor de la propiedad por su nombre.
            if not getattr(self, campo, None):
                # Lanza la excepción si alguno falta.
                raise ParametroFaltanteError(campo)
        # Si todo está bien, devuelve True.
        return True

    # Implementación del método abstracto describir().
    def describir(self):
        # Muestra el teléfono o "sin teléfono" si no tiene.
        tel = self.telefono or "sin teléfono"
        # Devuelve el texto con los datos del cliente.
        return f"{self.id} | {self.nombre} | Doc. {self.documento} | {self.correo} | {tel}"
