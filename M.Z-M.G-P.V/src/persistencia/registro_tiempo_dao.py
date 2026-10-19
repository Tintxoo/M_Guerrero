from dominio.empleado import Empleado
from dominio.proyecto import Proyecto
from dominio.registro_tiempo import RegistroTiempo
from persistencia.conexion import conexion_segura, marcador_sql, normalizar_fecha


class RegistroTiempoDAO:
    _select_registros = """
        SELECT r.id, r.fecha, r.horas, r.descripcion, r.empleado_id, r.proyecto_id,
               e.nombre, e.direccion, e.telefono, e.email, e.fechaInicioContrato,
               e.salario, e.departamento_id,
               p.nombre, p.descripcion, p.fecha_inicio
        FROM registro_tiempo r
        JOIN empleado e ON e.id = r.empleado_id
        JOIN proyecto p ON p.id = r.proyecto_id
    """

    @staticmethod
    def insertar(registro: RegistroTiempo) -> RegistroTiempo:
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"""
                INSERT INTO registro_tiempo (fecha, horas, descripcion, empleado_id, proyecto_id)
                VALUES ({marca}, {marca}, {marca}, {marca}, {marca})
                """,
                (
                    normalizar_fecha(registro.fecha),
                    registro.horas,
                    registro.descripcion,
                    registro.empleado_id,
                    registro.proyecto_id,
                ),
            )
            registro.id = cursor.lastrowid
            conexion.commit()
        if registro.empleado is not None:
            registro.empleado.agregarRegistroTiempo(registro)
        if registro.proyecto is not None:
            registro.proyecto.agregarRegistro(registro)
        return registro

    @staticmethod
    def eliminar(id_registro: int) -> bool:
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(f"DELETE FROM registro_tiempo WHERE id = {marca}", (id_registro,))
            conexion.commit()
            return cursor.rowcount > 0

    @staticmethod
    def obtenerPorId(id_registro: int):
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                RegistroTiempoDAO._select_registros
                + f" WHERE r.id = {marca}",
                (id_registro,),
            )
            fila = cursor.fetchone()
        return RegistroTiempoDAO._fila_a_registro(fila) if fila else None

    @staticmethod
    def actualizar(registro: RegistroTiempo) -> bool:
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"SELECT 1 FROM registro_tiempo WHERE id = {marca}",
                (registro.id,),
            )
            if cursor.fetchone() is None:
                return False
            cursor.execute(
                f"""
                UPDATE registro_tiempo
                SET fecha = {marca}, horas = {marca}, descripcion = {marca},
                    empleado_id = {marca}, proyecto_id = {marca}
                WHERE id = {marca}
                """,
                (
                    normalizar_fecha(registro.fecha),
                    registro.horas,
                    registro.descripcion,
                    registro.empleado_id,
                    registro.proyecto_id,
                    registro.id,
                ),
            )
            conexion.commit()
            return True

    @staticmethod
    def listar() -> list[RegistroTiempo]:
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(RegistroTiempoDAO._select_registros + " ORDER BY r.id")
            filas = cursor.fetchall()
        return [RegistroTiempoDAO._fila_a_registro(fila) for fila in filas]

    @staticmethod
    def listarPorEmpleado(id_empleado: int) -> list[RegistroTiempo]:
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                RegistroTiempoDAO._select_registros
                + f" WHERE r.empleado_id = {marca} ORDER BY r.id",
                (id_empleado,),
            )
            filas = cursor.fetchall()
        return [RegistroTiempoDAO._fila_a_registro(fila) for fila in filas]

    @staticmethod
    def listarPorProyecto(id_proyecto: int) -> list[RegistroTiempo]:
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                RegistroTiempoDAO._select_registros
                + f" WHERE r.proyecto_id = {marca} ORDER BY r.id",
                (id_proyecto,),
            )
            filas = cursor.fetchall()
        return [RegistroTiempoDAO._fila_a_registro(fila) for fila in filas]

    @staticmethod
    def _fila_a_registro(fila) -> RegistroTiempo:
        empleado = Empleado(
            id=fila[4],
            nombre=fila[6],
            direccion=fila[7],
            telefono=fila[8],
            email=fila[9],
            fechaInicioContrato=fila[10],
            salario=fila[11],
            departamento_id=fila[12],
        )
        proyecto = Proyecto(
            id=fila[5],
            nombre=fila[13],
            descripcion=fila[14],
            fechaInicio=fila[15],
        )
        registro = RegistroTiempo(
            id=fila[0],
            fecha=fila[1],
            horas=fila[2],
            descripcion=fila[3],
            empleado_id=fila[4],
            proyecto_id=fila[5],
            empleado=empleado,
            proyecto=proyecto,
        )
        empleado.agregarRegistroTiempo(registro)
        proyecto.agregarRegistro(registro)
        return registro
