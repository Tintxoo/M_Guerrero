from getpass import getpass

from dominio.registro_tiempo import RegistroTiempo
from dominio.usuario import Usuario
from presentacion.menu_cambio import menu_cambio
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.proyecto_dao import ProyectoDAO
from persistencia.registro_tiempo_dao import RegistroTiempoDAO
from persistencia.usuario_dao import UsuarioDAO
from servicios.entrada import (
    leer_correo_opcional,
    leer_decimal,
    leer_entero,
    leer_fecha,
    leer_nombre,
    leer_opcion,
    leer_telefono_opcional,
    leer_texto,
    limpiar_consola,
    pausar,
)
from servicios.permisos import exigir_empleado
from servicios.seguridad import hash_password, verify_password


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


def consultar_mis_proyectos(usuario: Usuario) -> None:
    exigir_empleado(usuario)
    proyectos = ProyectoDAO.listarPorEmpleado(usuario.empleado_id)
    print("\n--- Mis proyectos asignados ---")
    if not proyectos:
        print("No tienes proyectos asignados.")
        return

    for proyecto in proyectos:
        print(
            f"ID: {proyecto.id} | Nombre: {proyecto.nombre} "
            f"| Inicio: {proyecto.fechaInicio} "
            f"| Descripción: {proyecto.descripcion or 'Sin descripción'}"
        )


def registrar_mi_tiempo(usuario: Usuario) -> None:
    exigir_empleado(usuario)
    proyectos = ProyectoDAO.listarPorEmpleado(usuario.empleado_id)
    if not proyectos:
        print("No tienes proyectos asignados donde registrar tiempo.")
        return

    print("Proyectos disponibles:")
    proyectos_por_id = {proyecto.id: proyecto for proyecto in proyectos}
    for proyecto in proyectos:
        print(f"{proyecto.id}. {proyecto.nombre}")
    while True:
        id_proyecto = leer_entero("ID del proyecto: ")
        proyecto = proyectos_por_id.get(id_proyecto)
        if proyecto is not None:
            break
        print("El proyecto no está asignado a tu cuenta.")

    registro = RegistroTiempo(
        fecha=leer_fecha("Fecha del registro (AAAA-MM-DD): "),
        horas=leer_decimal("Horas trabajadas: ", minimo=0, estrictamente_mayor=True),
        descripcion=leer_texto("Descripción de las tareas: ", maximo=1000),
        empleado_id=usuario.empleado_id,
        proyecto_id=proyecto.id,
        proyecto=proyecto,
    )
    registro = RegistroTiempoDAO.insertar(registro)
    print(f"Registro guardado correctamente con ID: {registro.id}")


def modificar_mi_perfil(usuario: Usuario) -> None:
    empleado = EmpleadoDAO.obtenerPorId(usuario.empleado_id)
    if empleado is None:
        raise RuntimeError("No se encontró la ficha asociada a la cuenta.")

    print("\n--- Modificar mi ficha ---")
    nombre = leer_nombre(
        f"Nombre [{empleado.nombre}] (Enter conserva): ",
        obligatorio=False,
    )
    email = leer_correo_opcional(
        f"Correo [{empleado.email}] (Enter conserva): "
    )
    direccion = leer_texto(
        f"Dirección [{empleado.direccion}] (Enter conserva): ",
        obligatorio=False,
        maximo=200,
    )
    telefono = leer_telefono_opcional(
        f"Teléfono [{empleado.telefono}] (Enter conserva): "
    )
    nuevo_nombre = nombre or empleado.nombre
    nuevo_email = email or empleado.email
    nueva_direccion = direccion or empleado.direccion
    nuevo_telefono = telefono or empleado.telefono
    if (
        nuevo_nombre == empleado.nombre
        and nuevo_email == empleado.email
        and nueva_direccion == empleado.direccion
        and nuevo_telefono == empleado.telefono
    ):
        print("No se realizaron cambios.")
        return

    if not EmpleadoDAO.actualizar_perfil(
        empleado.id,
        nuevo_nombre,
        nuevo_email,
        nueva_direccion,
        nuevo_telefono,
    ):
        raise RuntimeError("No fue posible actualizar la ficha.")
    print("Tu ficha fue actualizada correctamente.")


def cambiar_credenciales(usuario: Usuario) -> None:
    exigir_empleado(usuario)
    print("\n--- Cambiar usuario y contraseña ---")
    nombre_ingresado = input(
        f"Nombre de usuario [{usuario.nombre_usuario}] (Enter conserva): "
    ).strip()
    nuevo_nombre = (
        Usuario.normalizar_usuario(nombre_ingresado)
        if nombre_ingresado
        else usuario.nombre_usuario
    )

    password = getpass("Nueva contraseña (Enter conserva): ")
    nuevo_hash = usuario.password_hash
    if password:
        if len(password) < Usuario.MIN_CLAVE:
            raise ValueError(
                f"La contraseña debe tener al menos {Usuario.MIN_CLAVE} caracteres."
            )
        if len(password) > Usuario.MAX_CLAVE:
            raise ValueError(
                f"La contraseña no puede superar {Usuario.MAX_CLAVE} caracteres."
            )
        confirmacion = getpass("Confirme la nueva contraseña: ")
        if password != confirmacion:
            raise ValueError("Las contraseñas no coinciden.")
        if verify_password(password, usuario.password_hash):
            password = ""
        else:
            nuevo_hash = hash_password(password)

    if (
        nuevo_nombre == usuario.nombre_usuario
        and nuevo_hash == usuario.password_hash
    ):
        print("No se realizaron cambios.")
        return

    nombre_anterior = usuario.nombre_usuario
    hash_anterior = usuario.password_hash
    usuario.nombre_usuario = nuevo_nombre
    usuario.password_hash = nuevo_hash
    try:
        if not UsuarioDAO.actualizar(usuario):
            raise RuntimeError("No fue posible actualizar los datos de acceso.")
    except Exception:
        usuario.nombre_usuario = nombre_anterior
        usuario.password_hash = hash_anterior
        raise
    print("Los datos de acceso se actualizaron correctamente.")


def menu_autoservicio_empleado(usuario: Usuario) -> None:
    exigir_empleado(usuario)

    acciones = {
        "1": lambda: consultar_ficha(usuario),
        "2": lambda: consultar_mis_registros(usuario),
        "3": lambda: modificar_mi_perfil(usuario),
        "4": lambda: registrar_mi_tiempo(usuario),
        "5": lambda: consultar_mis_proyectos(usuario),
        "6": lambda: cambiar_credenciales(usuario),
        "7": menu_cambio,
    }

    while True:
        limpiar_consola()
        print("\n===== PORTAL DEL EMPLEADO =====")
        print("1. Consultar mi ficha")
        print("2. Consultar mis registros de tiempo")
        print("3. Modificar mi ficha")
        print("4. Registrar tiempo trabajado")
        print("5. Consultar mis proyectos asignados")
        print("6. Cambiar mi usuario y contraseña")
        print("7. Consultar cambio del dólar e historial")
        print("0. Cerrar sesión")
        opcion = leer_opcion(
            "Seleccione una opción: ", {"0", "1", "2", "3", "4", "5", "6", "7"}
        )
        if opcion == "0":
            return

        try:
            acciones[opcion]()
        except Exception as error:
            print(f"No fue posible completar la operación: {error}")
        pausar()
