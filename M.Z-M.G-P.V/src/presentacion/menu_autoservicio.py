from dominio.usuario import Usuario
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.registro_tiempo_dao import RegistroTiempoDAO
from servicios.entrada import (
    leer_correo_opcional,
    leer_nombre,
    leer_opcion,
    limpiar_consola,
    pausar,
)
from servicios.permisos import exigir_empleado


def consultar_ficha(usuario: Usuario) -> None:
    empleado = EmpleadoDAO.obtenerPorId(usuario.empleado_id)
    if empleado is None:
        raise RuntimeError("No se encontró la ficha asociada a la cuenta.")

    print("\n--- Mi ficha ---")
    print(f"ID: {empleado.id}")
    print(f"Nombre: {empleado.nombre}")
    print(f"Correo: {empleado.email}")
    print(f"Dirección: {empleado.direccion}")
    print(f"Teléfono: {empleado.telefono}")
    print(f"Fecha de contrato: {empleado.fechaInicioContrato}")
    print(f"Salario: {empleado.salario:g}")
    print(f"Departamento: {empleado.departamento_id or 'Sin asignar'}")


def consultar_mis_registros(usuario: Usuario) -> None:
    registros = RegistroTiempoDAO.listarPorEmpleado(usuario.empleado_id)
    print("\n--- Mis registros de tiempo ---")
    if not registros:
        print("No tienes registros de tiempo.")
        return

    for registro in registros:
        print(
            f"ID: {registro.id} | Fecha: {registro.fecha} "
            f"| Horas: {registro.horas:g} | Proyecto: {registro.proyecto.nombre} "
            f"| Descripción: {registro.descripcion}"
        )


def modificar_mi_perfil(usuario: Usuario) -> None:
    empleado = EmpleadoDAO.obtenerPorId(usuario.empleado_id)
    if empleado is None:
        raise RuntimeError("No se encontró la ficha asociada a la cuenta.")

    print("\n--- Modificar mi nombre y correo ---")
    nombre = leer_nombre(
        f"Nombre [{empleado.nombre}] (Enter conserva): ",
        obligatorio=False,
    )
    email = leer_correo_opcional(
        f"Correo [{empleado.email}] (Enter conserva): "
    )
    nuevo_nombre = nombre or empleado.nombre
    nuevo_email = email or empleado.email
    if nuevo_nombre == empleado.nombre and nuevo_email == empleado.email:
        print("No se realizaron cambios.")
        return

    if not EmpleadoDAO.actualizar_perfil(
        empleado.id,
        nuevo_nombre,
        nuevo_email,
    ):
        raise RuntimeError("No fue posible actualizar la ficha.")
    print("Tu ficha fue actualizada correctamente.")


def menu_autoservicio_empleado(usuario: Usuario) -> None:
    exigir_empleado(usuario)

    acciones = {
        "1": lambda: consultar_ficha(usuario),
        "2": lambda: consultar_mis_registros(usuario),
        "3": lambda: modificar_mi_perfil(usuario),
    }

    while True:
        limpiar_consola()
        print("\n===== PORTAL DEL EMPLEADO =====")
        print("1. Consultar mi ficha")
        print("2. Consultar mis registros de tiempo")
        print("3. Modificar mi nombre y correo")
        print("0. Cerrar sesión")
        opcion = leer_opcion("Seleccione una opción: ", {"0", "1", "2", "3"})
        if opcion == "0":
            return

        try:
            acciones[opcion]()
        except Exception as error:
            print(f"No fue posible completar la operación: {error}")
        pausar()
