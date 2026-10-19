from dominio.empleado import Empleado
from persistencia.conexion import conexion_segura, marcador_sql, normalizar_fecha


class EmpleadoDAO:
    @staticmethod
    def insertar(empleado: Empleado) -> Empleado:
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"""
                INSERT INTO empleado (
                    nombre, direccion, telefono, email, fechaInicioContrato, salario, departamento_id
                ) VALUES ({marca}, {marca}, {marca}, {marca}, {marca}, {marca}, {marca})
                """,
                (
                    empleado.nombre,
                    empleado.direccion,
                    empleado.telefono,
                    empleado.email,
                    normalizar_fecha(empleado.fechaInicioContrato),
                    empleado.salario,
                    empleado.departamento_id,
                ),
            )
            empleado.id = cursor.lastrowid
            conexion.commit()
        return empleado

    @staticmethod
    def eliminar(id_empleado: int) -> bool:
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"UPDATE departamento SET gerente_id = NULL WHERE gerente_id = {marca}",
                (id_empleado,),
            )
            cursor.execute(f"DELETE FROM empleado WHERE id = {marca}", (id_empleado,))
            conexion.commit()
            return cursor.rowcount > 0

    @staticmethod
    def obtenerPorId(id_empleado: int):
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"""
                SELECT id, nombre, direccion, telefono, email, fechaInicioContrato,
                       salario, departamento_id
                FROM empleado
                WHERE id = {marca}
                """,
                (id_empleado,),
            )
            fila = cursor.fetchone()
        if fila is None:
            return None
        empleado = EmpleadoDAO._fila_a_empleado(fila)
        EmpleadoDAO._cargar_registros(empleado)
        return empleado

    @staticmethod
    def actualizar(empleado: Empleado) -> bool:
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"SELECT departamento_id FROM empleado WHERE id = {marca}",
                (empleado.id,),
            )
            fila_actual = cursor.fetchone()
            if fila_actual is None:
                return False
            if fila_actual[0] != empleado.departamento_id:
                cursor.execute(
                    f"UPDATE departamento SET gerente_id = NULL WHERE gerente_id = {marca}",
                    (empleado.id,),
                )
            cursor.execute(
                f"""
                UPDATE empleado
                SET nombre = {marca}, direccion = {marca}, telefono = {marca},
                    email = {marca}, fechaInicioContrato = {marca}, salario = {marca},
                    departamento_id = {marca}
                WHERE id = {marca}
                """,
                (
                    empleado.nombre,
                    empleado.direccion,
                    empleado.telefono,
                    empleado.email,
                    normalizar_fecha(empleado.fechaInicioContrato),
                    empleado.salario,
                    empleado.departamento_id,
                    empleado.id,
                ),
            )
            conexion.commit()
            return True

    @staticmethod
    def listar() -> list[Empleado]:
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                """
                SELECT id, nombre, direccion, telefono, email, fechaInicioContrato,
                       salario, departamento_id
                FROM empleado
                ORDER BY id
                """
            )
            filas = cursor.fetchall()
        empleados = [EmpleadoDAO._fila_a_empleado(fila) for fila in filas]
        for empleado in empleados:
            EmpleadoDAO._cargar_registros(empleado)
        return empleados

    @staticmethod
    def _cargar_registros(empleado: Empleado):
        from persistencia.registro_tiempo_dao import RegistroTiempoDAO

        for registro in RegistroTiempoDAO.listarPorEmpleado(empleado.id):
            registro.empleado = empleado
            empleado.agregarRegistroTiempo(registro)

    @staticmethod
    def _fila_a_empleado(fila) -> Empleado:
        return Empleado(
            id=fila[0],
            nombre=fila[1],
            direccion=fila[2],
            telefono=fila[3],
            email=fila[4],
            fechaInicioContrato=fila[5],
            salario=fila[6],
            departamento_id=fila[7],
        )
