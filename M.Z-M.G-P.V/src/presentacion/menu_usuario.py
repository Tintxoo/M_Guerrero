import hashlib

from dominio.usuario import Usuario
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.usuario_dao import UsuarioDAO
from presentacion.entrada import leer_entero, leer_opcion, limpiar_consola, pausar


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def registrar_usuario():
    print("\n--- Registrar Usuario ---")
    try:
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

        password = input("Contraseña: ").strip()
        if len(password) < Usuario.MIN_CLAVE:
            raise ValueError(f"La contraseña debe tener al menos {Usuario.MIN_CLAVE} caracteres.")

        usuario = Usuario(nombre_usuario, _hash_password(password), id_empleado)
        usuario = UsuarioDAO.insertar(usuario)
        print(f"Usuario registrado correctamente con el ID: {usuario.id}")
    except ValueError as error:
        print(f"Entrada inválida: {error}")
    except Exception as error:
        print(f"No fue posible registrar el usuario: {error}")


def iniciar_sesion() -> bool:
    print("\n--- Iniciar Sesión ---")
    try:
        nombre_usuario = input("Nombre de usuario: ").strip()
        password = input("Contraseña: ").strip()

        if not nombre_usuario or not password:
            print("Debe ingresar nombre de usuario y contraseña.")
            return False

        usuario = UsuarioDAO.buscar_por_nombre(nombre_usuario)
        if usuario is None:
            print("Nombre de usuario o contraseña incorrectos.")
            return False

        if usuario.password_hash != _hash_password(password):
            print("Nombre de usuario o contraseña incorrectos.")
            return False

        print(f"Bienvenido/a, {usuario.nombre_usuario}.")
        return True
    except Exception as error:
        print(f"No fue posible iniciar sesión: {error}")
        return False


def mostrar_menu_usuario():
    print("\n===== ACCESO AL SISTEMA =====")
    print("1. Registrar usuario")
    print("2. Iniciar sesión")
    print("0. Salir")


def menu_usuario() -> bool:
    while True:
        limpiar_consola()
        mostrar_menu_usuario()
        opcion = leer_opcion("Seleccione una opción: ", {"0", "1", "2"})

        if opcion == "0":
            print("Saliendo del sistema.")
            return False

        if opcion == "1":
            registrar_usuario()
            pausar()
            continue

        if opcion == "2":
            if iniciar_sesion():
                return True
            pausar()
            continue
