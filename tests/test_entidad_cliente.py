"""
tests/test_entidad_cliente.py
-----------------------------
Pruebas unitarias de la clase abstracta Entidad y de la clase Cliente.

Verifican abstracción, herencia, encapsulación y validaciones sin
modificar el código del sistema. Cliente se prueba a través de
GestorSoftwareFJ.registrar_cliente(nombre, documento, correo, telefono=None).

Ejecución (desde la raíz del proyecto):
    python -m unittest tests.test_entidad_cliente -v
"""

import inspect
import unittest

from sistema import GestorSoftwareFJ, SoftwareFJError
from sistema.cliente import Cliente
from sistema.entidad import Entidad


class TestEntidadAbstracta(unittest.TestCase):
    """Comprueba que Entidad cumple su rol de clase abstracta."""

    def test_entidad_es_abstracta(self):
        self.assertTrue(inspect.isabstract(Entidad))

    def test_declara_metodos_abstractos_requeridos(self):
        self.assertTrue({"validar", "describir"} <= set(Entidad.__abstractmethods__))

    def test_no_se_puede_instanciar(self):
        with self.assertRaises(TypeError):
            Entidad()

    def test_subclase_incompleta_no_se_puede_instanciar(self):
        class Incompleta(Entidad):
            def describir(self):  # falta validar()
                return "incompleta"

        with self.assertRaises(TypeError):
            Incompleta()

    def test_cliente_hereda_de_entidad(self):
        self.assertTrue(issubclass(Cliente, Entidad))
        self.assertFalse(inspect.isabstract(Cliente))


class TestClienteValido(unittest.TestCase):
    """Registros correctos de clientes."""

    def setUp(self):
        self.gestor = GestorSoftwareFJ()

    def test_registro_valido_devuelve_cliente(self):
        cliente = self.gestor.registrar_cliente(
            "Laura Gómez", "1012345678", "laura.gomez@correo.com", "3001234567"
        )
        self.assertIsInstance(cliente, Cliente)
        self.assertIsInstance(cliente, Entidad)  # polimorfismo

    def test_telefono_es_opcional(self):
        cliente = self.gestor.registrar_cliente(
            "Carlos Ruiz", "79888777", "carlos.ruiz@empresa.co"
        )
        self.assertIsInstance(cliente, Cliente)

    def test_describir_devuelve_texto_no_vacio(self):
        cliente = self.gestor.registrar_cliente(
            "Laura Gómez", "1012345678", "laura.gomez@correo.com"
        )
        descripcion = cliente.describir()
        self.assertIsInstance(descripcion, str)
        self.assertTrue(descripcion.strip())

    def test_cliente_queda_en_la_lista_del_gestor(self):
        self.gestor.registrar_cliente("Ana Torres", "52111222", "ana@correo.com")
        self.assertEqual(len(self.gestor.listar_clientes()), 1)


class TestClienteInvalido(unittest.TestCase):
    """Cada dato inválido debe lanzar una excepción propia del sistema."""

    def setUp(self):
        self.gestor = GestorSoftwareFJ()

    def test_nombre_vacio(self):
        with self.assertRaises(SoftwareFJError):
            self.gestor.registrar_cliente("", "1033444555", "a@correo.com")

    def test_nombre_solo_espacios(self):
        with self.assertRaises(SoftwareFJError):
            self.gestor.registrar_cliente("     ", "1033444555", "a@correo.com")

    def test_correo_sin_dominio(self):
        with self.assertRaises(SoftwareFJError):
            self.gestor.registrar_cliente("Ana Torres", "52111222", "ana.torres@")

    def test_correo_sin_arroba(self):
        with self.assertRaises(SoftwareFJError):
            self.gestor.registrar_cliente("Ana Torres", "52111222", "ana.correo.com")

    def test_documento_vacio(self):
        with self.assertRaises(SoftwareFJError):
            self.gestor.registrar_cliente("Ana Torres", "", "ana@correo.com")

    def test_telefono_con_letras(self):
        with self.assertRaises(SoftwareFJError):
            self.gestor.registrar_cliente(
                "Ana Torres", "52111222", "ana@correo.com", "abc123"
            )

    def test_documento_duplicado(self):
        self.gestor.registrar_cliente("Laura Gómez", "1012345678", "l@correo.com")
        with self.assertRaises(SoftwareFJError):
            self.gestor.registrar_cliente("Otra Persona", "1012345678", "o@correo.com")

    def test_registro_fallido_no_deja_cliente_a_medias(self):
        with self.assertRaises(SoftwareFJError):
            self.gestor.registrar_cliente("Ana Torres", "52111222", "ana.torres@")
        self.assertEqual(len(self.gestor.listar_clientes()), 0)


class TestEncapsulacionCliente(unittest.TestCase):
    """Los atributos son privados y las propiedades validan al modificarse."""

    def setUp(self):
        self.gestor = GestorSoftwareFJ()
        self.cliente = self.gestor.registrar_cliente(
            "Laura Gómez", "1012345678", "laura.gomez@correo.com", "3001234567"
        )

    def test_atributo_privado_no_es_accesible_directamente(self):
        with self.assertRaises(AttributeError):
            _ = self.cliente.__nombre  # noqa: B018

    def test_atributo_privado_existe_con_name_mangling(self):
        self.assertTrue(hasattr(self.cliente, "_Cliente__nombre"))
        self.assertTrue(hasattr(self.cliente, "_Cliente__documento"))

    def test_propiedad_rechaza_correo_invalido(self):
        with self.assertRaises(SoftwareFJError):
            self.cliente.correo = "correo-malo"

    def test_propiedad_rechaza_nombre_vacio(self):
        with self.assertRaises(SoftwareFJError):
            self.cliente.nombre = ""

    def test_valor_no_cambia_tras_asignacion_invalida(self):
        correo_original = self.cliente.correo
        with self.assertRaises(SoftwareFJError):
            self.cliente.correo = "correo-malo"
        self.assertEqual(self.cliente.correo, correo_original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
