# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto colaborativo de la **Fase 4 – Componente práctico – Prácticas simuladas** del curso
**Programación (213023)** de la Universidad Nacional Abierta y a Distancia (UNAD), ECBTI.
Grupo **213023_20**.

Sistema orientado a objetos, **sin base de datos**, que gestiona los clientes, servicios y reservas
de la empresa ficticia *Software FJ*. Implementa abstracción, herencia, polimorfismo,
encapsulación y manejo avanzado de excepciones, de modo que la aplicación **sigue funcionando
aunque se presenten errores** durante su ejecución.

## Ejecución

Requiere Python 3.8 o superior. No usa librerías externas.

```bash
python main.py
```

El programa simula **23 operaciones** (válidas e inválidas) y registra todos los eventos y errores en
`logs/software_fj.log`.

## Estructura

```
software_fj/
├── main.py               # Programa principal: simulación de 23 operaciones
├── sistema/
│   ├── __init__.py       # Exporta las clases del paquete
│   ├── excepciones.py    # Excepciones personalizadas (SoftwareFJError y derivadas)
│   ├── logger.py         # Configuración del archivo de logs
│   ├── entidad.py        # Clase abstracta Entidad
│   ├── cliente.py        # Clase Cliente (validaciones y encapsulación)
│   ├── servicios.py      # Clase abstracta Servicio + ReservaSala, AlquilerEquipo, Asesoria
│   ├── reserva.py        # Clase Reserva (confirmar, cancelar, procesar)
│   └── gestor.py         # GestorSoftwareFJ: listas internas de clientes, servicios y reservas
└── logs/
    └── software_fj.log   # Registro de eventos y errores
```

## Requisitos del Anexo 3 y dónde se cumplen

| Requisito | Implementación |
|---|---|
| Clase abstracta para entidades generales | `Entidad` (`entidad.py`) con `validar()` y `describir()` abstractos |
| Cliente con validaciones y encapsulación | `Cliente`: atributos privados (`__nombre`, `__documento`...) y propiedades que validan |
| Servicio abstracto + 3 servicios especializados | `Servicio` → `ReservaSala`, `AlquilerEquipo`, `Asesoria` |
| Polimorfismo y métodos sobrescritos | `_costo_base()`, `validar_parametros()` y `describir()` en cada servicio |
| Reserva con confirmación, cancelación y procesamiento | `Reserva.confirmar()`, `cancelar()`, `procesar()` |
| Métodos sobrecargados | `calcular_costo(duracion[, impuesto[, descuento]])` y `a_horas()` con `singledispatchmethod` (int, float o `timedelta`) |
| Excepciones personalizadas | 10 clases en `excepciones.py` con código de error (FJ-100 a FJ-500) |
| `try/except` | `main.py → ejecutar_operacion()` |
| `try/except/else` | `logger.py → obtener_logger()`, `Reserva.confirmar()` |
| `try/except/finally` | `Reserva.confirmar()`, `main.py → ejecutar_operacion()` |
| `try/finally` | `Reserva.procesar()` |
| Encadenamiento de excepciones | `Reserva.confirmar()`: `raise ReservaInvalidaError(...) from error` |
| Archivo de logs | `logs/software_fj.log` (eventos INFO, errores ERROR/WARNING, trazas DEBUG) |
| Mínimo 10 operaciones simuladas | 23 operaciones en `main.py` (8 exitosas, 15 con error controlado) |

## Estados de una reserva

```
PENDIENTE --confirmar()--> CONFIRMADA --procesar()--> PROCESADA
    |   |                      |
    |   +--(error)--> RECHAZADA
    +-------cancelar()---------+--> CANCELADA
```

## Trabajo colaborativo

Cada integrante trabaja en su propia rama y entrega sus cambios mediante *pull request* a `main`.

| Integrante | Rama | Responsabilidad |
|---|---|---|
| Andrés David Barón Romero | `andres-baron` | Estructura base del proyecto, excepciones y logs |
| Integrante 2 | `integrante-2` | Clase abstracta Entidad y Cliente |
| Integrante 3 | `integrante-3` | Servicios especializados |
| Integrante 4 | `integrante-4` | Reservas |
| Integrante 5 | `integrante-5` | Simulaciones y documento final |

Flujo sugerido:

```bash
git clone <enlace-del-repositorio>
cd <carpeta>
git checkout -b nombre-apellido
# ...cambios...
git add .
git commit -m "Descripción clara del cambio"
git push origin nombre-apellido
# Luego abrir un Pull Request en GitHub hacia main
```

## Referencias

- Van Rossum, G., & Drake Jr, F. L. (2024). *El tutorial de Python*. Python Software Foundation. https://docs.python.org/es/3/tutorial/
- Cuevas Álvarez, A. (2016). *Python 3: curso práctico*. RA-MA Editorial.
- Romano, F., Baka, B., & Phillips, D. (2019). *Getting Started with Python*. Packt Publishing.
