from dominio.departamento import Departamento
from persistencia.departamento_dao import DepartamentoDAO
from persistencia.empleado_dao import EmpleadoDAO
from servicios.entrada import (
    leer_entero,
    leer_nombre,
    leer_opcion,
    limpiar_consola,
    pausar,
)


def registrar_departamento():
    print("\n--- Registrar Nuevo Departamento ---")
    try:
        nombre = leer_nombre("Nombre del departamento: ")
        departamento = DepartamentoDAO.insertar(Departamento(nombre=nombre))
        print(f"Departamento registrado correctamente con ID: {departamento.id}")
        print("Puede asignar empleados y gerente al editar un empleado.")
    except Exception as error:
        print(f"Error al registrar el departamento: {error}")


def listar_departamentos():
    print("\n--- Lista de Departamentos ---")
    try:
        departamentos = DepartamentoDAO.listar()
        if not departamentos:
            print("No hay departamentos registrados.")
            return
        for departamento in departamentos:
            gerente = (
                f"{departamento.gerente.nombre} (ID {departamento.gerente.id})"
                if departamento.gerente
                else "Sin gerente"
            )
            print(
                f"ID: {departamento.id} | Nombre: {departamento.nombre} "
                f"| Empleados: {departamento.cantidad_empleados()} | Gerente: {gerente}"
            )
    except Exception as error:
        print(f"Error al listar departamentos: {error}")


def buscar_departamento():
    print("\n--- Buscar Departamento ---")
    try:
        id_departamento = leer_entero("Ingrese el ID del departamento: ")
        departamento = DepartamentoDAO.obtenerPorId(id_departamento)
        if not departamento:
            print("No existe un departamento con ese ID.")
            return

        gerente = (
            f"{departamento.gerente.nombre} (ID {departamento.gerente.id})"
            if departamento.gerente
            else "Sin asignar"
        )
        print(
            f"ID: {departamento.id} | Nombre: {departamento.nombre} "
            f"| Gerente: {gerente}"
        )
        for empleado in departamento.empleados:
            print(f"- {empleado.nombre} (ID {empleado.id})")
        if not departamento.empleados:
            print("El departamento no tiene empleados.")
    except Exception as error:
        print(f"Error al buscar el departamento: {error}")


def actualizar_departamento():
    print("\n--- Actualizar Departamento / Asignar Gerente ---")
    try:
        id_departamento = leer_entero("Ingrese el ID del departamento: ")
        departamento = DepartamentoDAO.obtenerPorId(id_departamento)
        if not departamento:
            print("No existe un departamento con ese ID.")
            return

        nuevo_nombre = leer_nombre(
            f"Nombre [{departamento.nombre}] (Enter conserva): ",
            obligatorio=False,
        )
        if nuevo_nombre:
            departamento.nombre = nuevo_nombre

        gerente_actual = departamento.gerente.id if departamento.gerente else None
        gerente_input = input(
            f"ID del gerente [{gerente_actual or 'ninguno'}] "
            "(Enter conserva, 0 quita): "
        ).strip()
        gerente = None
        while gerente_input and gerente_input != "0":
            if not gerente_input.isdecimal() or int(gerente_input) <= 0:
                print("Ingrese un ID entero positivo, 0 o Enter.")
            else:
                gerente = EmpleadoDAO.obtenerPorId(int(gerente_input))
                if gerente:
                    break
                print("No existe un empleado con ese ID.")
            gerente_input = input("ID del gerente: ").strip()
        if gerente_input == "0":
            departamento.quitarGerente()
        elif gerente_input:
            if gerente:
                departamento.asignarGerente(gerente)

        if DepartamentoDAO.actualizar(departamento):
            print("Departamento actualizado correctamente.")
        else:
            print("No se encontró el departamento para actualizar.")
    except ValueError as error:
        print(f"Entrada inválida: {error}")
    except Exception as error:
        print(f"Error al actualizar el departamento: {error}")


def eliminar_departamento():
    print("\n--- Eliminar Departamento ---")
    try:
        id_departamento = leer_entero("Ingrese el ID del departamento: ")
        if DepartamentoDAO.eliminar(id_departamento):
            print("Departamento eliminado. Sus empleados quedan sin asignar.")
        else:
            print("No existe un departamento con ese ID.")
    except Exception as error:
        print(f"No fue posible eliminar el departamento: {error}")


def mostrar_menu_departamento():
    print("\n===== GESTIÓN DE DEPARTAMENTOS =====")
    print("1. Registrar departamento")
    print("2. Listar departamentos")
    print("3. Buscar departamento")
    print("4. Actualizar nombre / gerente")
    print("5. Eliminar departamento")
    print("0. Volver al menú principal")


def menu_departamento():
    while True:
        limpiar_consola()
        mostrar_menu_departamento()
        opcion = leer_opcion("Seleccione una opción: ", {"0", "1", "2", "3", "4", "5"})
        if opcion == "0":
            return
        acciones = {
            "1": registrar_departamento,
            "2": listar_departamentos,
            "3": buscar_departamento,
            "4": actualizar_departamento,
            "5": eliminar_departamento,
        }
        acciones[opcion]()
        pausar()
