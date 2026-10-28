class Usuario:
    MIN_USUARIO = 3
    MAX_USUARIO = 40
    MIN_CLAVE = 6

    def __init__(
        self,
        nombre_usuario: str,
        password_hash: str,
        empleado_id: int,
        id: int | None = None,
    ):
        if type(empleado_id) is not int or empleado_id <= 0:
            raise ValueError("El ID del empleado debe ser positivo.")

        self.id = id
        self.empleado_id = empleado_id
        self.nombre_usuario = self.normalizar_usuario(nombre_usuario)
        self.password_hash = self.validar_password_hash(password_hash)

    @classmethod
    def normalizar_usuario(cls, nombre_usuario: str) -> str:
        if not isinstance(nombre_usuario, str):
            raise ValueError("El nombre de usuario debe ser texto.")

        nombre_usuario = nombre_usuario.strip().lower()

        if len(nombre_usuario) < cls.MIN_USUARIO or len(nombre_usuario) > cls.MAX_USUARIO:
            raise ValueError(
                f"El nombre de usuario debe tener entre {cls.MIN_USUARIO} y {cls.MAX_USUARIO} caracteres."
            )

        return nombre_usuario

    @staticmethod
    def validar_password_hash(password_hash: str) -> str:
        if not isinstance(password_hash, str):
            raise ValueError("El hash de la contraseña debe ser texto.")

        if len(password_hash) < Usuario.MIN_CLAVE:
            raise ValueError(
                f"La contraseña debe tener al menos {Usuario.MIN_CLAVE} caracteres."
            )

        return password_hash