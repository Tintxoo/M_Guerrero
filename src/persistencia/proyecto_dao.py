from dominio.proyecto import Proyecto
from dominio.empleado import Empleado
from persistencia.conexion import conexion_segura, marcador_sql, normalizar_fecha


class ProyectoDAO:
    @staticmethod
    def insertar(proyecto: Proyecto) -> Proyecto:
        proyecto_validado = Proyecto(
            nombre=proyecto.nombre,
            descripcion=proyecto.descripcion,
            fechaInicio=proyecto.fechaInicio,
        )
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"""
                INSERT INTO proyecto (nombre, descripcion, fecha_inicio)
                VALUES ({marca}, {marca}, {marca})
                """,
                (
                    proyecto_validado.nombre,
                    proyecto_validado.descripcion,
                    normalizar_fecha(proyecto_validado.fechaInicio),
                ),
            )
            proyecto.id = cursor.lastrowid
            conexion.commit()
        return proyecto

    @staticmethod
    def eliminar(id_proyecto: int) -> bool:
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(f"DELETE FROM proyecto WHERE id = {marca}", (id_proyecto,))
            conexion.commit()
            return cursor.rowcount > 0

    @staticmethod
    def obtenerPorId(id_proyecto: int):
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"""
                SELECT id, nombre, descripcion, fecha_inicio
                FROM proyecto
                WHERE id = {marca}
                """,
                (id_proyecto,),
            )
            fila = cursor.fetchone()
        if fila is None:
            return None
        proyecto = ProyectoDAO._fila_a_proyecto(fila)
        ProyectoDAO._cargar_registros(proyecto)
        return proyecto

    @staticmethod
    def actualizar(proyecto: Proyecto) -> bool:
        proyecto_validado = Proyecto(
            id=proyecto.id,
            nombre=proyecto.nombre,
            descripcion=proyecto.descripcion,
            fechaInicio=proyecto.fechaInicio,
        )
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"SELECT 1 FROM proyecto WHERE id = {marca}",
                (proyecto_validado.id,),
            )
            if cursor.fetchone() is None:
                return False
            cursor.execute(
                f"""
                UPDATE proyecto
                SET nombre = {marca}, descripcion = {marca}, fecha_inicio = {marca}
                WHERE id = {marca}
                """,
                (
                    proyecto_validado.nombre,
                    proyecto_validado.descripcion,
                    normalizar_fecha(proyecto_validado.fechaInicio),
                    proyecto_validado.id,
                ),
            )
            conexion.commit()
            return True

    @staticmethod
    def listar() -> list[Proyecto]:
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT id, nombre, descripcion, fecha_inicio FROM proyecto ORDER BY id"
            )
            filas = cursor.fetchall()
        proyectos = [ProyectoDAO._fila_a_proyecto(fila) for fila in filas]
        for proyecto in proyectos:
            ProyectoDAO._cargar_registros(proyecto)
        return proyectos

    @staticmethod
    def listarPorEmpleado(id_empleado: int) -> list[Proyecto]:
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"""
                SELECT p.id, p.nombre, p.descripcion, p.fecha_inicio
                FROM proyecto p
                JOIN asignacion_proyecto a ON a.proyecto_id = p.id
                WHERE a.empleado_id = {marca}
                ORDER BY p.id
                """,
                (id_empleado,),
            )
            filas = cursor.fetchall()
        return [ProyectoDAO._fila_a_proyecto(fila) for fila in filas]

    @staticmethod
    def listarEmpleadosAsignados(id_proyecto: int) -> list[Empleado]:
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"""
                SELECT e.id, e.nombre, e.direccion, e.telefono, e.email,
                       e.fechaInicioContrato, e.salario, e.departamento_id
                FROM empleado e
                JOIN asignacion_proyecto a ON a.empleado_id = e.id
                WHERE a.proyecto_id = {marca}
                ORDER BY e.id
                """,
                (id_proyecto,),
            )
            filas = cursor.fetchall()
        return [
            Empleado(
                id=fila[0],
                nombre=fila[1],
                direccion=fila[2],
                telefono=fila[3],
                email=fila[4],
                fechaInicioContrato=fila[5],
                salario=fila[6],
                departamento_id=fila[7],
            )
            for fila in filas
        ]

    @staticmethod
    def asignarEmpleado(id_proyecto: int, id_empleado: int) -> bool:
        if id_proyecto <= 0 or id_empleado <= 0:
            raise ValueError("El empleado y el proyecto deben tener IDs válidos.")

        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"""
                SELECT 1 FROM asignacion_proyecto
                WHERE proyecto_id = {marca} AND empleado_id = {marca}
                """,
                (id_proyecto, id_empleado),
            )
            if cursor.fetchone() is not None:
                return False
            cursor.execute(
                f"""
                INSERT INTO asignacion_proyecto (proyecto_id, empleado_id)
                VALUES ({marca}, {marca})
                """,
                (id_proyecto, id_empleado),
            )
            conexion.commit()
            return cursor.rowcount > 0

    @staticmethod
    def quitarAsignacion(id_proyecto: int, id_empleado: int) -> bool:
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"""
                DELETE FROM asignacion_proyecto
                WHERE proyecto_id = {marca} AND empleado_id = {marca}
                """,
                (id_proyecto, id_empleado),
            )
            conexion.commit()
            return cursor.rowcount > 0

    @staticmethod
    def _cargar_registros(proyecto: Proyecto):
        from persistencia.registro_tiempo_dao import RegistroTiempoDAO

        for registro in RegistroTiempoDAO.listarPorProyecto(proyecto.id):
            registro.proyecto = proyecto
            proyecto.agregarRegistro(registro)

    @staticmethod
    def _fila_a_proyecto(fila) -> Proyecto:
        return Proyecto(
            id=fila[0],
            nombre=fila[1],
            descripcion=fila[2],
            fechaInicio=fila[3],
        )
