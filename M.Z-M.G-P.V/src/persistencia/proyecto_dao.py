from dominio.proyecto import Proyecto
from persistencia.conexion import conexion_segura, marcador_sql, normalizar_fecha


class ProyectoDAO:
    @staticmethod
    def insertar(proyecto: Proyecto) -> Proyecto:
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"""
                INSERT INTO proyecto (nombre, descripcion, fecha_inicio)
                VALUES ({marca}, {marca}, {marca})
                """,
                (
                    proyecto.nombre,
                    proyecto.descripcion,
                    normalizar_fecha(proyecto.fechaInicio),
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
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"SELECT 1 FROM proyecto WHERE id = {marca}",
                (proyecto.id,),
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
                    proyecto.nombre,
                    proyecto.descripcion,
                    normalizar_fecha(proyecto.fechaInicio),
                    proyecto.id,
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
