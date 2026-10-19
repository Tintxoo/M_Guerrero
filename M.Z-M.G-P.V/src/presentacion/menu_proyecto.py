from dominio.proyecto import Proyecto
from persistencia.proyecto_dao import ProyectoDAO
from presentacion.entrada import (
    leer_entero,
    leer_fecha,
    leer_opcion,
    leer_texto,
    limpiar_consola,
    pausar,
)


def registrar_proyecto():
    print("\n--- Registrar Nuevo Proyecto ---")
    try:
        nombre = leer_texto("Nombre del proyecto: ", maximo=100)
        descripcion = leer_texto("Descripción: ", maximo=1000)
        fecha_inicio = leer_fecha("Fecha de inicio (AAAA-MM-DD): ")
        proyecto = Proyecto(nombre, descripcion, fecha_inicio)
        proyecto = ProyectoDAO.insertar(proyecto)
        print(f"Proyecto registrado correctamente con el ID: {proyecto.id}")
    except Exception as error:
        print(f"No fue posible registrar el proyecto: {error}")


def listar_proyectos():
    print("\n--- Lista de Proyectos ---")
    try:
        proyectos = ProyectoDAO.listar()
        if not proyectos:
            print("No hay proyectos registrados.")
            return
        for proyecto in proyectos:
            print(
                f"ID: {proyecto.id} | Nombre: {proyecto.nombre} "
                f"| Inicio: {proyecto.fechaInicio} "
                f"| Horas: {proyecto.calcularHorasTotales():g}"
            )
    except Exception as error:
        print(f"Error al listar proyectos: {error}")


def buscar_proyecto():
    print("\n--- Buscar Proyecto ---")
    try:
        id_proyecto = leer_entero("Ingrese el ID del proyecto: ")
        proyecto = ProyectoDAO.obtenerPorId(id_proyecto)
        if proyecto:
            print(f"ID: {proyecto.id} | Nombre: {proyecto.nombre}")
            print(f"Descripción: {proyecto.descripcion}")
            print(f"Fecha de inicio: {proyecto.fechaInicio}")
            print(f"Horas totales: {proyecto.calcularHorasTotales():g}")
        else:
            print("No existe un proyecto con ese ID.")
    except Exception as error:
        print(f"Error al buscar el proyecto: {error}")


def actualizar_proyecto():
    print("\n--- Actualizar Proyecto ---")
    try:
        id_proyecto = leer_entero("Ingrese el ID del proyecto: ")
        proyecto = ProyectoDAO.obtenerPorId(id_proyecto)
        if not proyecto:
            print("No existe un proyecto con ese ID.")
            return

        nombre = leer_texto(
            f"Nuevo nombre [{proyecto.nombre}] (Enter conserva): ",
            obligatorio=False,
            maximo=100,
        )
        descripcion = leer_texto(
            f"Nueva descripción [{proyecto.descripcion}] (Enter conserva): ",
            obligatorio=False,
            maximo=1000,
        )
        fecha_inicio = leer_fecha(
            f"Nueva fecha [{proyecto.fechaInicio}] (Enter conserva): ",
            obligatorio=False,
        )
        if nombre:
            proyecto.nombre = nombre
        if descripcion:
            proyecto.descripcion = descripcion
        if fecha_inicio is not None:
            proyecto.fechaInicio = fecha_inicio

        if ProyectoDAO.actualizar(proyecto):
            print("Proyecto actualizado correctamente.")
        else:
            print("No se encontró el proyecto para actualizar.")
    except Exception as error:
        print(f"Error al actualizar el proyecto: {error}")


def eliminar_proyecto():
    print("\n--- Eliminar Proyecto ---")
    try:
        id_proyecto = leer_entero("Ingrese el ID del proyecto: ")
        if ProyectoDAO.eliminar(id_proyecto):
            print("Proyecto eliminado correctamente.")
        else:
            print("No existe un proyecto con ese ID.")
    except Exception as error:
        print(f"No fue posible eliminar el proyecto: {error}")


def mostrar_menu_proyecto():
    print("\n===== GESTIÓN DE PROYECTOS =====")
    print("1. Registrar proyecto")
    print("2. Listar proyectos")
    print("3. Buscar proyecto")
    print("4. Actualizar proyecto")
    print("5. Eliminar proyecto")
    print("0. Volver al menú principal")


def menu_proyecto():
    while True:
        limpiar_consola()
        mostrar_menu_proyecto()
        opcion = leer_opcion("Seleccione una opción: ", {"0", "1", "2", "3", "4", "5"})
        if opcion == "0":
            return
        acciones = {
            "1": registrar_proyecto,
            "2": listar_proyectos,
            "3": buscar_proyecto,
            "4": actualizar_proyecto,
            "5": eliminar_proyecto,
        }
        acciones[opcion]()
        pausar()
