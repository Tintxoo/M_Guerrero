from dominio.departamento import Departamento
from persistencia.conexion import conexion_segura, marcador_sql


class DepartamentoDAO:
    @staticmethod
    def insertar(departamento: Departamento) -> Departamento:
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"INSERT INTO departamento (nombre, gerente_id) VALUES ({marca}, NULL)",
                (departamento.nombre,),
            )
            departamento.id = cursor.lastrowid
            if departamento.gerente_id is not None:
                DepartamentoDAO._guardar_gerente(conexion, departamento)
            conexion.commit()
        return departamento

    @staticmethod
    def eliminar(id_departamento: int) -> bool:
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"UPDATE empleado SET departamento_id = NULL WHERE departamento_id = {marca}",
                (id_departamento,),
            )
            cursor.execute(f"DELETE FROM departamento WHERE id = {marca}", (id_departamento,))
            conexion.commit()
            return cursor.rowcount > 0

    @staticmethod
    def obtenerPorId(id_departamento: int):
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"SELECT id, nombre, gerente_id FROM departamento WHERE id = {marca}",
                (id_departamento,),
            )
            fila = cursor.fetchone()
        return DepartamentoDAO._fila_a_departamento(fila) if fila else None

    @staticmethod
    def actualizar(departamento: Departamento) -> bool:
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"SELECT 1 FROM departamento WHERE id = {marca}",
                (departamento.id,),
            )
            if cursor.fetchone() is None:
                return False
            cursor.execute(
                f"UPDATE departamento SET nombre = {marca}, gerente_id = NULL WHERE id = {marca}",
                (departamento.nombre, departamento.id),
            )
            if departamento.gerente_id is not None:
                DepartamentoDAO._guardar_gerente(conexion, departamento)
            conexion.commit()
            return True

    @staticmethod
    def listar() -> list[Departamento]:
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT id, nombre, gerente_id FROM departamento")
            filas = cursor.fetchall()
        return [DepartamentoDAO._fila_a_departamento(fila) for fila in filas]

    @staticmethod
    def _guardar_gerente(conexion, departamento: Departamento):
        marca = marcador_sql()
        if departamento.id is None:
            raise ValueError("Guarde el departamento antes de asignar su gerente.")
        cursor = conexion.cursor()
        cursor.execute(
            f"SELECT departamento_id FROM empleado WHERE id = {marca}",
            (departamento.gerente_id,),
        )
        fila = cursor.fetchone()
        if fila is None:
            raise ValueError("No existe el empleado seleccionado como gerente.")
        if fila[0] != departamento.id:
            raise ValueError("El gerente debe pertenecer al departamento.")
        cursor.execute(
            f"UPDATE departamento SET gerente_id = {marca} WHERE id = {marca}",
            (departamento.gerente_id, departamento.id),
        )

    @staticmethod
    def _fila_a_departamento(fila) -> Departamento:
        departamento = Departamento(nombre=fila[1], id=fila[0], gerente_id=fila[2])
        from persistencia.empleado_dao import EmpleadoDAO

        for empleado in EmpleadoDAO.listar():
            if empleado.departamento_id == departamento.id:
                departamento.agregarEmpleado(empleado)
        if fila[2] is not None:
            departamento.gerente = EmpleadoDAO.obtenerPorId(fila[2])
        return departamento
