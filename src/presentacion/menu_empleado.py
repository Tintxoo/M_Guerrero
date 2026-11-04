from dominio.empleado import Empleado
from persistencia.departamento_dao import DepartamentoDAO
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.proyecto_dao import ProyectoDAO
from servicios.entrada import (
    leer_correo,
    leer_correo_opcional,
    leer_decimal,
    leer_decimal_opcional,
    leer_entidad_existente,
    leer_entero,
    leer_entero_opcional,
    leer_fecha,
    leer_id_opcional,
    leer_nombre,
    leer_opcion,
    leer_telefono,
    leer_telefono_opcional,
    leer_texto,
    limpiar_consola,
    pausar,
)


def registrar_empleado():
    print("\n--- Registrar Nuevo Empleado ---")
    try:
        nombre = leer_nombre("Nombre completo: ")
        direccion = leer_texto("Dirección: ", maximo=200)
        telefono = leer_telefono("Teléfono: ")
        email = leer_correo("Correo electrónico: ")
        fecha_contrato = leer_fecha("Fecha de contrato (AAAA-MM-DD): ")
        salario = leer_decimal("Salario (mayor o igual a 0): ")

        while True:
            departamento_id = leer_id_opcional(
                "ID de departamento (Enter para dejar sin asignar): "
            )
            if departamento_id is None or DepartamentoDAO.obtenerPorId(departamento_id):
                break
            print("No existe un departamento con ese ID.")

        empleado = Empleado(
            nombre,
            direccion,
            telefono,
            email,
            fecha_contrato,
            salario,
            departamento_id,
        )
        empleado = EmpleadoDAO.insertar(empleado)
        print(f"Empleado registrado correctamente con el ID: {empleado.id}")
    except ValueError as error:
        print(f"Entrada inválida: {error}")
    except Exception as error:
        print(f"No fue posible registrar el empleado: {error}")


def listar_empleados():
    print("\n--- Lista de Empleados ---")
    try:
        empleados = EmpleadoDAO.listar()
        if not empleados:
            print("No hay empleados registrados.")
            return
        for empleado in empleados:
            print(
                f"ID: {empleado.id} | {empleado.mostrar_datos()} "
                f"| Departamento: {empleado.departamento_id or 'Sin asignar'} "
                f"| Registros de tiempo: {len(empleado.registrosTiempo)}"
            )
    except Exception as error:
        print(f"Error al listar empleados: {error}")


def buscar_empleado():
    print("\n--- Buscar Empleado ---")
    try:
        id_empleado = leer_entero("Ingrese el ID del empleado: ")
        empleado = EmpleadoDAO.obtenerPorId(id_empleado)
        if empleado:
            print(f"ID: {empleado.id} | {empleado.mostrar_datos()}")
            print(f"Dirección: {empleado.direccion}")
            print(f"Fecha de contrato: {empleado.fechaInicioContrato}")
            print(f"Departamento: {empleado.departamento_id or 'Sin asignar'}")
            print(f"Registros de tiempo: {len(empleado.registrosTiempo)}")
        else:
            print("No existe un empleado con ese ID.")
    except Exception as error:
        print(f"Error al buscar el empleado: {error}")


def actualizar_empleado():
    print("\n--- Actualizar Empleado ---")
    try:
        id_empleado = leer_entero("Ingrese el ID del empleado: ")
        empleado = EmpleadoDAO.obtenerPorId(id_empleado)
        if not empleado:
            print("No existe un empleado con ese ID.")
            return

        nombre = leer_nombre(
            f"Nombre [{empleado.nombre}] (Enter conserva): ",
            obligatorio=False,
        )
        direccion = leer_texto(
            f"Dirección [{empleado.direccion}] (Enter conserva): ",
            obligatorio=False,
            maximo=200,
        )
        telefono = leer_telefono_opcional(
            f"Teléfono [{empleado.telefono}] (Enter conserva): "
        )
        email = leer_correo_opcional(
            f"Correo [{empleado.email}] (Enter conserva): "
        )
        salario = leer_decimal_opcional(
            f"Salario [{empleado.salario:g}] (Enter conserva): "
        )
        fecha_contrato = leer_fecha(
            f"Fecha [{empleado.fechaInicioContrato}] (Enter conserva): ",
            obligatorio=False,
        )
        empleado.actualizarDatos(
            nombre=nombre or None,
            direccion=direccion or None,
            telefono=telefono,
            email=email,
            salario=salario,
            fechaInicioContrato=fecha_contrato,
        )

        departamento_id = None
        departamento = None
        while True:
            departamento_id = leer_entero_opcional(
                f"ID del departamento [{empleado.departamento_id or 'ninguno'}] "
                "(Enter conserva, 0 quita): ",
                permitir_cero=True,
            )
            if departamento_id is None or departamento_id == 0:
                break
            departamento = DepartamentoDAO.obtenerPorId(departamento_id)
            if departamento:
                break
            print("No existe un departamento con ese ID.")
        if departamento_id == 0:
            empleado.asignarDepartamento(None)
        elif departamento_id is not None and departamento is not None:
            departamento.agregarEmpleado(empleado)

        if EmpleadoDAO.actualizar(empleado):
            print("Empleado actualizado correctamente.")
        else:
            print("No se encontró el empleado para actualizar.")
    except ValueError as error:
        print(f"Entrada inválida: {error}")
    except Exception as error:
        print(f"Error al actualizar el empleado: {error}")

def eliminar_empleado():
    print("\n--- Eliminar Empleado ---")
    try:
        id_empleado = leer_entero("Ingrese el ID del empleado: ")
        if EmpleadoDAO.eliminar(id_empleado):
            print("Empleado eliminado correctamente.")
        else:
            print("No existe un empleado con ese ID.")
    except Exception as error:
        print(f"No fue posible eliminar el empleado: {error}")


def asignar_proyecto():
    print("\n--- Asignar Proyecto a Empleado ---")
    try:
        empleado = leer_entidad_existente(
            "ID del empleado: ", EmpleadoDAO.obtenerPorId, "un empleado"
        )
        proyecto = leer_entidad_existente(
            "ID del proyecto: ", ProyectoDAO.obtenerPorId, "un proyecto"
        )
        if ProyectoDAO.asignarEmpleado(proyecto.id, empleado.id):
            print("Proyecto asignado correctamente.")
        else:
            print("El proyecto ya estaba asignado a ese empleado.")
    except Exception as error:
        print(f"No fue posible asignar el proyecto: {error}")


def quitar_asignacion_proyecto():
    print("\n--- Quitar Asignación de Proyecto ---")
    try:
        empleado = leer_entidad_existente(
            "ID del empleado: ", EmpleadoDAO.obtenerPorId, "un empleado"
        )
        proyecto = leer_entidad_existente(
            "ID del proyecto: ", ProyectoDAO.obtenerPorId, "un proyecto"
        )
        if ProyectoDAO.quitarAsignacion(proyecto.id, empleado.id):
            print("Asignación de proyecto eliminada correctamente.")
        else:
            print("Ese proyecto no estaba asignado al empleado.")
    except Exception as error:
        print(f"No fue posible quitar la asignación: {error}")


def mostrar_menu_empleado():
    print("\n===== GESTIÓN DE EMPLEADOS =====")
    print("1. Registrar empleado")
    print("2. Listar empleados")
    print("3. Buscar empleado")
    print("4. Actualizar empleado / departamento")
    print("5. Eliminar empleado")
    print("6. Asignar proyecto a empleado")
    print("7. Quitar proyecto de empleado")
    print("0. Volver al menú principal")


def menu_empleado():
    while True:
        limpiar_consola()
        mostrar_menu_empleado()
        opcion = leer_opcion(
            "Seleccione una opción: ", {"0", "1", "2", "3", "4", "5", "6", "7"}
        )
        if opcion == "0":
            return
        acciones = {
            "1": registrar_empleado,
            "2": listar_empleados,
            "3": buscar_empleado,
            "4": actualizar_empleado,
            "5": eliminar_empleado,
            "6": asignar_proyecto,
            "7": quitar_asignacion_proyecto,
        }
        acciones[opcion]()
        pausar()
