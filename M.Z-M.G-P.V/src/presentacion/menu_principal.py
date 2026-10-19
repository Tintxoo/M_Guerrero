from presentacion.entrada import leer_opcion, limpiar_consola, pausar
from presentacion.menu_departamento import menu_departamento
from presentacion.menu_empleado import menu_empleado
from presentacion.menu_proyecto import menu_proyecto
from presentacion.menu_registro_tiempo import menu_registro_tiempo


def mostrar_opciones_principales():
    print("\n===== SISTEMA ECOTECH =====")
    print("1. Gestión de Departamentos")
    print("2. Gestión de Empleados")
    print("3. Gestión de Proyectos")
    print("4. Gestión de Registros de Tiempo")
    print("0. Salir")


def iniciar_menu_principal():
    acciones = {
        "1": menu_departamento,
        "2": menu_empleado,
        "3": menu_proyecto,
        "4": menu_registro_tiempo,
    }
    while True:
        limpiar_consola()
        mostrar_opciones_principales()
        opcion = leer_opcion("Seleccione una opción: ", {"0", "1", "2", "3", "4"})
        if opcion == "0":
            print("Cerrando sistema. ¡Hasta luego!")
            return
        try:
            acciones[opcion]()
        except Exception as error:
            print(f"Se produjo un error inesperado en el menú: {error}")
            pausar()
