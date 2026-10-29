from persistencia.conexion import conexion_segura, obtener_motor


def crear_tablas():
    if obtener_motor() == "sqlite":
        sql_departamento = """
            CREATE TABLE IF NOT EXISTS departamento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                gerente_id INTEGER
            )
        """
        sql_proyecto = """
            CREATE TABLE IF NOT EXISTS proyecto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                fecha_inicio DATE NOT NULL
            )
        """
        sql_empleado = """
            CREATE TABLE IF NOT EXISTS empleado (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                direccion TEXT NOT NULL,
                telefono TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                fechaInicioContrato DATE NOT NULL,
                salario REAL NOT NULL CHECK (salario >= 0),
                departamento_id INTEGER,
                FOREIGN KEY (departamento_id) REFERENCES departamento(id)
                    ON DELETE SET NULL
            )
        """
        sql_registro_tiempo = """
            CREATE TABLE IF NOT EXISTS registro_tiempo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE NOT NULL,
                horas REAL NOT NULL CHECK (horas > 0),
                descripcion TEXT NOT NULL,
                empleado_id INTEGER NOT NULL,
                proyecto_id INTEGER NOT NULL,
                FOREIGN KEY (empleado_id) REFERENCES empleado(id)
                    ON DELETE RESTRICT,
                FOREIGN KEY (proyecto_id) REFERENCES proyecto(id)
                    ON DELETE RESTRICT
            )
        """
        sql_usuario = """
            CREATE TABLE IF NOT EXISTS usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_usuario TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                empleado_id INTEGER NOT NULL UNIQUE,
                rol TEXT NOT NULL DEFAULT 'empleado'
                    CHECK (rol IN ('administrador', 'empleado')),
                FOREIGN KEY (empleado_id) REFERENCES empleado(id)
                    ON DELETE CASCADE
            )
        """
    else:
        sql_departamento = """
            CREATE TABLE IF NOT EXISTS departamento (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(100) NOT NULL,
                gerente_id INT
            )
        """
        sql_proyecto = """
            CREATE TABLE IF NOT EXISTS proyecto (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT,
                fecha_inicio DATE NOT NULL
            )
        """
        sql_empleado = """
            CREATE TABLE IF NOT EXISTS empleado (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(100) NOT NULL,
                direccion VARCHAR(200) NOT NULL,
                telefono VARCHAR(20) NOT NULL,
                email VARCHAR(150) NOT NULL UNIQUE,
                fechaInicioContrato DATE NOT NULL,
                salario FLOAT NOT NULL,
                departamento_id INT,
                FOREIGN KEY (departamento_id) REFERENCES departamento(id)
                    ON DELETE SET NULL
            )
        """
        sql_registro_tiempo = """
            CREATE TABLE IF NOT EXISTS registro_tiempo (
                id INT PRIMARY KEY AUTO_INCREMENT,
                fecha DATE NOT NULL,
                horas FLOAT NOT NULL,
                descripcion TEXT NOT NULL,
                empleado_id INT NOT NULL,
                proyecto_id INT NOT NULL,
                FOREIGN KEY (empleado_id) REFERENCES empleado(id)
                    ON DELETE RESTRICT,
                FOREIGN KEY (proyecto_id) REFERENCES proyecto(id)
                    ON DELETE RESTRICT
            )
        """
        sql_usuario = """
            CREATE TABLE IF NOT EXISTS usuario (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nombre_usuario VARCHAR(40) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                empleado_id INT NOT NULL UNIQUE,
                rol VARCHAR(20) NOT NULL DEFAULT 'empleado',
                FOREIGN KEY (empleado_id) REFERENCES empleado(id)
                    ON DELETE CASCADE
            )
        """

    with conexion_segura() as conexion:
        cursor = conexion.cursor()
        for sql in (sql_departamento, sql_proyecto, sql_empleado, sql_registro_tiempo, sql_usuario):
            cursor.execute(sql)
        if obtener_motor() == "sqlite":
            cursor.execute("PRAGMA table_info(usuario)")
            columnas_usuario = {fila[1] for fila in cursor.fetchall()}
        else:
            cursor.execute("SHOW COLUMNS FROM usuario")
            columnas_usuario = {fila[0] for fila in cursor.fetchall()}

        if "rol" not in columnas_usuario:
            if obtener_motor() == "sqlite":
                cursor.execute(
                    """
                    ALTER TABLE usuario
                    ADD COLUMN rol TEXT NOT NULL DEFAULT 'empleado'
                    CHECK (rol IN ('administrador', 'empleado'))
                    """
                )
            else:
                cursor.execute(
                    """
                    ALTER TABLE usuario
                    ADD COLUMN rol VARCHAR(20) NOT NULL DEFAULT 'empleado'
                    """
                )
            marca = "?" if obtener_motor() == "sqlite" else "%s"
            cursor.execute(
                f"UPDATE usuario SET rol = 'administrador' "
                f"WHERE LOWER(nombre_usuario) = {marca}",
                ("ana.torres",),
            )
        conexion.commit()
