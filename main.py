"""
main.py
-------
Programa principal del Sistema Integral de Gestión de Clientes, Servicios
y Reservas de Software FJ.

Simula 15 operaciones completas, válidas e inválidas, para demostrar que
el sistema sigue funcionando aunque ocurran errores. Cada operación se
ejecuta dentro de ejecutar_operacion(), que captura las excepciones, las
registra en logs/software_fj.log y deja que el programa continúe.

Ejecución:  python main.py
"""

# timedelta permite expresar una duración como "2 horas y 30 minutos".
from datetime import timedelta

# Se importan las clases del paquete sistema.
from sistema import (
    AlquilerEquipo,
    Asesoria,
    GestorSoftwareFJ,
    ReservaSala,
    SoftwareFJError,
    obtener_logger,
)

# Registrador de eventos del sistema.
log = obtener_logger()

# Contadores para el resumen final.
resultados = {"exitosas": 0, "fallidas": 0}


def ejecutar_operacion(numero, descripcion, operacion):
    """
    Ejecuta una operación protegida con try/except/else/finally.
    'operacion' es una función sin argumentos (lambda) con la acción a probar.
    """
    # Muestra en consola qué operación se va a ejecutar.
    print(f"\n[{numero:02d}] {descripcion}")
    # Registra el inicio de la operación en el log.
    log.debug(f"Operación {numero:02d} iniciada: {descripcion}")
    try:
        # Ejecuta la operación.
        resultado = operacion()
    except SoftwareFJError as error:
        # Error previsto del sistema: se registra y el programa continúa.
        log.warning(f"Operación {numero:02d} fallida: {error}")
        # Si el error viene encadenado (raise ... from ...), muestra la causa original.
        if error.__cause__ is not None:
            # Registra la causa original.
            log.warning(f"   causa original: {error.__cause__}")
        # Suma una operación fallida.
        resultados["fallidas"] += 1
    except Exception as error:  # noqa: BLE001
        # Error inesperado: se registra con la traza completa, pero no se detiene el programa.
        log.exception(f"Operación {numero:02d}: error inesperado {type(error).__name__}: {error}")
        # Suma una operación fallida.
        resultados["fallidas"] += 1
    else:
        # Solo si no hubo errores: muestra el resultado.
        if resultado is not None:
            # Imprime la descripción del objeto obtenido.
            print(f"   OK -> {resultado}")
        # Suma una operación exitosa.
        resultados["exitosas"] += 1
    finally:
        # Se ejecuta siempre: marca el fin de la operación en el log.
        log.debug(f"Operación {numero:02d} finalizada")


def main():
    """Crea el gestor, carga el catálogo y ejecuta las simulaciones."""
    # Encabezado de la ejecución.
    print("=" * 70)
    print(" SOFTWARE FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas")
    print("=" * 70)

    # Crea el gestor con sus listas vacías.
    gestor = GestorSoftwareFJ()

    # ------------------------------------------------------------------
    # Catálogo inicial de servicios (uno de cada tipo y uno deshabilitado)
    # ------------------------------------------------------------------
    sala = gestor.agregar_servicio(ReservaSala("Sala Andes", 50000, capacidad=10))
    portatiles = gestor.agregar_servicio(AlquilerEquipo("Portátiles Lenovo", 8000, unidades=5))
    asesoria = gestor.agregar_servicio(
        Asesoria("Asesoría en ciberseguridad", 120000, "Seguridad informática", nivel="senior")
    )
    proyector = gestor.agregar_servicio(AlquilerEquipo("Proyector Epson", 15000, unidades=2))
    # El proyector entra a mantenimiento: queda no disponible.
    proyector.deshabilitar()

    # ------------------------------------------------------------------
    # Simulación de operaciones
    # ------------------------------------------------------------------

    # 1. Registro válido de un cliente.
    ejecutar_operacion(1, "Registrar cliente válido (Laura Gómez)",
                       lambda: gestor.registrar_cliente("laura gómez", "1012345678",
                                                        "laura.gomez@correo.com", "3001234567"))
    # 2. Registro válido de otro cliente, sin teléfono (es opcional).
    ejecutar_operacion(2, "Registrar cliente válido sin teléfono (Carlos Ruiz)",
                       lambda: gestor.registrar_cliente("Carlos Ruiz", "79888777",
                                                        "carlos.ruiz@empresa.co"))
    # 3. Registro inválido: correo con formato incorrecto.
    ejecutar_operacion(3, "Registrar cliente con correo inválido",
                       lambda: gestor.registrar_cliente("Ana Torres", "52111222", "ana.torres@"))
    # 4. Registro inválido: documento duplicado.
    ejecutar_operacion(4, "Registrar cliente con documento repetido",
                       lambda: gestor.registrar_cliente("Laura Gómez B", "1012345678",
                                                        "otra@correo.com"))
    # 5. Registro inválido: falta el nombre.
    ejecutar_operacion(5, "Registrar cliente sin nombre",
                       lambda: gestor.registrar_cliente("", "1033444555", "sin.nombre@correo.com"))
    # 6. Creación inválida de un servicio: tarifa negativa.
    ejecutar_operacion(6, "Crear servicio con tarifa negativa",
                       lambda: ReservaSala("Sala Pacífico", -20000, capacidad=8))
    # 7. Creación inválida de un servicio: nivel de asesoría inexistente.
    ejecutar_operacion(7, "Crear asesoría con nivel inexistente",
                       lambda: Asesoria("Asesoría en datos", 90000, "Ciencia de datos", nivel="master"))
    # 8. Creación válida de un servicio nuevo durante la ejecución.
    ejecutar_operacion(8, "Crear y agregar asesoría válida (nivel experto)",
                       lambda: gestor.agregar_servicio(
                           Asesoria("Asesoría en Python", 100000, "Desarrollo de software", "experto")))
    # 9. Reserva exitosa de la sala con descuento del 10 %.
    ejecutar_operacion(9, "Reservar sala 3 h para 6 personas con 10 % de descuento",
                       lambda: gestor.crear_reserva("1012345678", sala.id, 3, descuento=0.10, personas=6))
    # 10. Reserva exitosa de portátiles usando timedelta (otra variante del cálculo).
    ejecutar_operacion(10, "Alquilar 3 portátiles por 2 h 30 min (duración como timedelta)",
                       lambda: gestor.crear_reserva("79888777", portatiles.id,
                                                    timedelta(hours=2, minutes=30), cantidad=3))
    # 11. Reserva fallida: la sala no admite 15 personas.
    ejecutar_operacion(11, "Reservar sala para 15 personas (supera la capacidad)",
                       lambda: gestor.crear_reserva("79888777", sala.id, 2, personas=15))
    # 12. Reserva fallida: el proyector está en mantenimiento.
    ejecutar_operacion(12, "Alquilar proyector en mantenimiento",
                       lambda: gestor.crear_reserva("1012345678", proyector.id, 4, cantidad=1))
    # 13. Reserva fallida: solo quedan 2 portátiles y se piden 4.
    ejecutar_operacion(13, "Alquilar 4 portátiles cuando solo quedan 2",
                       lambda: gestor.crear_reserva("1012345678", portatiles.id, 5, cantidad=4))
    # 14. Reserva fallida: cliente que no existe.
    ejecutar_operacion(14, "Reservar con un cliente no registrado",
                       lambda: gestor.crear_reserva("99999999", asesoria.id, 2))
    # 15. Reserva fallida: asesoría de 10 horas (máximo 8).
    ejecutar_operacion(15, "Reservar asesoría de 10 horas (máximo 8)",
                       lambda: gestor.crear_reserva("79888777", asesoria.id, 10))
    # 16. Reserva fallida: falta el parámetro 'personas' en la sala.
    ejecutar_operacion(16, "Reservar sala sin indicar número de personas",
                       lambda: gestor.crear_reserva("79888777", sala.id, 2))
    # 17. Reserva exitosa de asesoría y luego se procesa (cobro).
    def reservar_y_procesar_asesoria():
        # Crea y confirma la reserva de la asesoría.
        reserva = gestor.crear_reserva("1012345678", asesoria.id, 2)
        # Procesa la reserva (pasa a PROCESADA).
        reserva.procesar()
        # Devuelve la reserva para mostrarla.
        return reserva
    ejecutar_operacion(17, "Reservar asesoría 2 h y procesar el cobro", reservar_y_procesar_asesoria)
    # 18. Cancelar la reserva de portátiles (devuelve las unidades al inventario).
    def cancelar_portatiles():
        # Toma la reserva de portátiles, que fue la segunda creada.
        reserva = next(r for r in gestor.listar_reservas() if r.servicio is portatiles)
        # La cancela.
        reserva.cancelar("el cliente cambió de fecha")
        # Devuelve el inventario actualizado del servicio.
        return portatiles
    ejecutar_operacion(18, "Cancelar el alquiler de portátiles", cancelar_portatiles)
    # 19. Operación no permitida: procesar una reserva cancelada.
    ejecutar_operacion(19, "Intentar procesar la reserva cancelada",
                       lambda: next(r for r in gestor.listar_reservas()
                                    if r.estado == "CANCELADA").procesar())
    # 20. Operación no permitida: cancelar una reserva ya procesada.
    ejecutar_operacion(20, "Intentar cancelar la reserva ya procesada",
                       lambda: next(r for r in gestor.listar_reservas()
                                    if r.estado == "PROCESADA").cancelar())
    # 21. Procesar la reserva de la sala (confirmada en la operación 9).
    ejecutar_operacion(21, "Procesar el cobro de la reserva de la sala",
                       lambda: next(r for r in gestor.listar_reservas()
                                    if r.servicio is sala and r.estado == "CONFIRMADA").procesar())
    # 22. Cálculo con descuento fuera de rango (sobrecarga con 3 parámetros).
    ejecutar_operacion(22, "Calcular costo de sala con descuento del 80 % (máximo 50 %)",
                       lambda: sala.calcular_costo(2, 0.19, 0.80, personas=4))
    # 23. Duración con un tipo no soportado (texto en lugar de número).
    ejecutar_operacion(23, "Calcular costo con duración en texto ('dos horas')",
                       lambda: asesoria.calcular_costo("dos horas"))

    # ------------------------------------------------------------------
    # Resumen final
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print(" RESUMEN")
    print("=" * 70)
    # Lista los clientes registrados.
    print("\nClientes registrados:")
    for cliente in gestor.listar_clientes():
        print(f"  - {cliente}")
    # Lista los servicios del catálogo.
    print("\nServicios:")
    for servicio in gestor.listar_servicios():
        print(f"  - {servicio}")
    # Lista todas las reservas con su estado.
    print("\nReservas:")
    for reserva in gestor.listar_reservas():
        print(f"  - {reserva}")
    # Muestra los totales.
    total = resultados["exitosas"] + resultados["fallidas"]
    print(f"\nOperaciones simuladas: {total} "
          f"({resultados['exitosas']} exitosas, {resultados['fallidas']} con error controlado)")
    print(f"Total facturado: ${gestor.total_facturado():,.2f}")
    print("Log de eventos y errores: logs/software_fj.log")
    # Registra el fin de la ejecución.
    log.info("Ejecución finalizada sin interrupciones")


# Punto de entrada: solo se ejecuta main() si se corre este archivo directamente.
if __name__ == "__main__":
    # Llama a la función principal.
    main()
