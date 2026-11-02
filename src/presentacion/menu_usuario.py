from getpass import getpass

from dominio.usuario import Usuario
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.usuario_dao import UsuarioDAO
from servicios.entrada import leer_entero, leer_opcion, limpiar_consola, pausar
from servicios.permisos import exigir_administrador
from servicios.seguridad import hash_password, needs_rehash, verify_password


def registrar_usuario(usuario_actual: Usuario):
    print("\n--- Registrar Usuario ---")
    try:
        exigir_administrador(usuario_actual)

        nombre_usuario = input("Nombre de usuario: ").strip()
        if not nombre_usuario:
            print("El nombre de usuario no puede estar vacío.")
            return

        if UsuarioDAO.buscar_por_nombre(nombre_usuario) is not None:
            print("Ya existe un usuario con ese nombre.")
            return

        id_empleado = leer_entero("ID del empleado: ")
        empleado = EmpleadoDAO.obtenerPorId(id_empleado)
        if empleado is None:
            print("No existe un empleado con ese ID.")
            return

        if UsuarioDAO.buscar_por_empleado(id_empleado) is not None:
            print("Ese empleado ya tiene un usuario registrado.")
            return

        password = getpass("Contraseña inicial: ").strip()
        if len(password) < Usuario.MIN_CLAVE:
            raise ValueError(f"La contraseña debe tener al menos {Usuario.MIN_CLAVE} caracteres.")

        usuario = Usuario(
            nombre_usuario,
            hash_password(password),
            id_empleado,
            rol=Usuario.ROL_EMPLEADO,
        )
        usuario = UsuarioDAO.insertar(usuario)
        print(f"Usuario registrado correctamente con el ID: {usuario.id}")
    except ValueError as error:
        print(f"Entrada inválida: {error}")
    except PermissionError as error:
        print(f"Acceso denegado: {error}")
    except Exception as error:
        print(f"No fue posible registrar el usuario: {error}")


def iniciar_sesion() -> Usuario | None:
    print("\n--- Iniciar Sesión ---")
    try:
        nombre_usuario = input("Nombre de usuario: ").strip()
        password = getpass("Contraseña: ").strip()

        if not nombre_usuario or not password:
            print("Debe ingresar nombre de usuario y contraseña.")
            return None

        usuario = UsuarioDAO.buscar_por_nombre(nombre_usuario)
        if usuario is None:
            print("Nombre de usuario o contraseña incorrectos.")
            return None

        if not verify_password(password, usuario.password_hash):
            print("Nombre de usuario o contraseña incorrectos.")
            return None

        if needs_rehash(usuario.password_hash):
            usuario.password_hash = hash_password(password)
            if not UsuarioDAO.actualizar(usuario):
                raise RuntimeError("No fue posible actualizar el hash de la contraseña.")

        print(f"Bienvenido/a, {usuario.nombre_usuario}.")
        return usuario
    except Exception as error:
        print(f"No fue posible iniciar sesión: {error}")
        return None


def mostrar_menu_usuario():
    print("\n===== ACCESO AL SISTEMA =====")
    print("1. Iniciar sesión")
    print("0. Salir")


def menu_usuario() -> Usuario | None:
    while True:
        limpiar_consola()
        mostrar_menu_usuario()
        opcion = leer_opcion("Seleccione una opción: ", {"0", "1"})

        if opcion == "0":
            print("Saliendo del sistema.")
            return None

        usuario = iniciar_sesion()
        if usuario is not None:
            return usuario
        pausar()
