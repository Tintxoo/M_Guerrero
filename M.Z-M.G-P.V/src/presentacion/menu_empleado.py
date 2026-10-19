from dominio.empleado import Empleado
from persistencia.departamento_dao import DepartamentoDAO
from persistencia.empleado_dao import EmpleadoDAO
from presentacion.entrada import (
    leer_correo,
    leer_correo_opcional,
    leer_decimal,
    leer_decimal_opcional,
    leer_entero,
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

        departamento_input = input(
            f"ID del departamento [{empleado.departamento_id or 'ninguno'}] "
            "(Enter conserva, 0 quita): "
        ).strip()
        departamento = None
        while departamento_input and departamento_input != "0":
            if not departamento_input.isdecimal() or int(departamento_input) <= 0:
                print("Ingrese un ID entero positivo, 0 o Enter.")
            else:
                departamento = DepartamentoDAO.obtenerPorId(int(departamento_input))
                if departamento:
                    break
                print("No existe un departamento con ese ID.")
            departamento_input = input("ID del departamento: ").strip()
        if departamento_input == "0":
            empleado.asignarDepartamento(None)
        elif departamento_input:
            if departamento:
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


def mostrar_menu_empleado():
    print("\n===== GESTIÓN DE EMPLEADOS =====")
    print("1. Registrar empleado")
    print("2. Listar empleados")
    print("3. Buscar empleado")
    print("4. Actualizar empleado / departamento")
    print("5. Eliminar empleado")
    print("0. Volver al menú principal")


def menu_empleado():
    while True:
        limpiar_consola()
        mostrar_menu_empleado()
        opcion = leer_opcion("Seleccione una opción: ", {"0", "1", "2", "3", "4", "5"})
        if opcion == "0":
            return
        acciones = {
            "1": registrar_empleado,
            "2": listar_empleados,
            "3": buscar_empleado,
            "4": actualizar_empleado,
            "5": eliminar_empleado,
        }
        acciones[opcion]()
        pausar()
