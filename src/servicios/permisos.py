from dominio.usuario import Usuario


def exigir_rol(usuario: Usuario, rol_requerido: str) -> None:
    if rol_requerido not in Usuario.ROLES_VALIDOS:
        raise ValueError(f"Rol no reconocido: {rol_requerido}")
    if usuario.rol != rol_requerido:
        raise PermissionError(
            f"Se requiere el rol '{rol_requerido}' para realizar esta acción."
        )


def exigir_administrador(usuario: Usuario) -> None:
    exigir_rol(usuario, Usuario.ROL_ADMINISTRADOR)


def exigir_empleado(usuario: Usuario) -> None:
    exigir_rol(usuario, Usuario.ROL_EMPLEADO)