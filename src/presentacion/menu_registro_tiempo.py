from dominio.registro_tiempo import RegistroTiempo
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.proyecto_dao import ProyectoDAO
from persistencia.registro_tiempo_dao import RegistroTiempoDAO
from servicios.entrada import (
    convertir_decimal,
    leer_decimal,
    leer_entero,
    leer_entidad_existente,
    leer_fecha,
    leer_opcion,
    leer_texto,
    limpiar_consola,
    pausar,
)


def registrar_tiempo():
    print("\n--- Registrar Tiempo Trabajado ---")
    try:
        empleado = leer_entidad_existente(
            "ID del empleado: ", EmpleadoDAO.obtenerPorId, "un empleado"
        )
        proyecto = leer_entidad_existente(
            "ID del proyecto: ", ProyectoDAO.obtenerPorId, "un proyecto"
        )

        fecha = leer_fecha("Fecha del registro (AAAA-MM-DD): ")
        horas = leer_decimal("Horas trabajadas: ", minimo=0, estrictamente_mayor=True)
        descripcion = leer_texto("Descripción de las tareas: ", maximo=1000)

        registro = RegistroTiempo(
            fecha=fecha,
            horas=horas,
            descripcion=descripcion,
            empleado_id=empleado.id,
            proyecto_id=proyecto.id,
            empleado=empleado,
            proyecto=proyecto,
        )
        registro = RegistroTiempoDAO.insertar(registro)
        print(f"Registro guardado correctamente con ID: {registro.id}")
    except Exception as error:
        print(f"No fue posible guardar el registro: {error}")


def listar_registros():
    print("\n--- Lista de Registros de Tiempo ---")
    try:
        registros = RegistroTiempoDAO.listar()
        if not registros:
            print("No hay registros de tiempo.")
            return
        for registro in registros:
            print(
                f"ID: {registro.id} | Fecha: {registro.fecha} "
                f"| Horas: {registro.horas:g} "
                f"| Empleado: {registro.empleado.nombre} "
                f"| Proyecto: {registro.proyecto.nombre} "
                f"| Descripción: {registro.descripcion}"
            )
    except Exception as error:
        print(f"Error al listar registros: {error}")


def buscar_registro():
    print("\n--- Buscar Registro de Tiempo ---")
    try:
        id_registro = leer_entero("Ingrese el ID del registro: ")
        registro = RegistroTiempoDAO.obtenerPorId(id_registro)
        if registro:
            print(f"ID: {registro.id} | Fecha: {registro.fecha}")
            print(f"Horas: {registro.horas:g}")
            print(f"Empleado: {registro.empleado.nombre} (ID {registro.empleado_id})")
            print(f"Proyecto: {registro.proyecto.nombre} (ID {registro.proyecto_id})")
            print(f"Descripción: {registro.descripcion}")
        else:
            print("No existe un registro con ese ID.")
    except Exception as error:
        print(f"Error al buscar el registro: {error}")


def actualizar_registro():
    print("\n--- Actualizar Registro de Tiempo ---")
    try:
        id_registro = leer_entero("Ingrese el ID del registro: ")
        registro = RegistroTiempoDAO.obtenerPorId(id_registro)
        if not registro:
            print("No existe un registro con ese ID.")
            return

        horas_input = input(f"Horas [{registro.horas:g}] (Enter conserva): ").strip()
        if horas_input:
            while True:
                try:
                    horas = convertir_decimal(
                        horas_input,
                        minimo=0,
                        estrictamente_mayor=True,
                    )
                    break
                except ValueError as error:
                    print(error)
                    horas_input = input("Ingrese nuevamente las horas: ").strip()
        else:
            horas = registro.horas
        descripcion = leer_texto(
            f"Descripción [{registro.descripcion}] (Enter conserva): ",
            obligatorio=False,
            maximo=1000,
        )

        if horas_input or descripcion:
            registro.modificarRegistro(horas, descripcion or registro.descripcion)
            if RegistroTiempoDAO.actualizar(registro):
                print("Registro actualizado correctamente.")
            else:
                print("No se encontró el registro para actualizar.")
        else:
            print("No se realizaron cambios.")
    except Exception as error:
        print(f"Error al actualizar el registro: {error}")

def eliminar_registro():
    print("\n--- Eliminar Registro de Tiempo ---")
    try:
        id_registro = leer_entero("Ingrese el ID del registro: ")
        if RegistroTiempoDAO.eliminar(id_registro):
            print("Registro eliminado correctamente.")
        else:
            print("No existe un registro con ese ID.")
    except Exception as error:
        print(f"No fue posible eliminar el registro: {error}")


def mostrar_menu_registro():
    print("\n===== GESTIÓN DE TIEMPO =====")
    print("1. Registrar tiempo trabajado")
    print("2. Listar registros")
    print("3. Buscar registro")
    print("4. Actualizar registro")
    print("5. Eliminar registro")
    print("0. Volver al menú principal")


def menu_registro_tiempo():
    while True:
        limpiar_consola()
        mostrar_menu_registro()
        opcion = leer_opcion("Seleccione una opción: ", {"0", "1", "2", "3", "4", "5"})
        if opcion == "0":
            return
        acciones = {
            "1": registrar_tiempo,
            "2": listar_registros,
            "3": buscar_registro,
            "4": actualizar_registro,
            "5": eliminar_registro,
        }
        acciones[opcion]()
        pausar()
