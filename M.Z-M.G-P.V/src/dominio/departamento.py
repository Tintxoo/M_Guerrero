from typing import Optional

from dominio.empleado import Empleado


class Departamento:
    def __init__(
        self,
        nombre: str,
        gerente: Optional[Empleado] = None,
        id: Optional[int] = None,
        gerente_id: Optional[int] = None,
    ):
        if not nombre.strip():
            raise ValueError("El nombre del departamento no puede estar vacío.")
        self.id = id
        self.nombre = nombre
        self.gerente = gerente
        self._gerente_id = gerente.id if gerente else gerente_id
        self._empleados: list[Empleado] = []

    def asignarGerente(self, e: Empleado):
        if self.id is not None and e.departamento_id != self.id:
            raise ValueError("El gerente debe pertenecer al departamento.")
        self.gerente = e
        self._gerente_id = e.id

    @property
    def gerente_id(self) -> Optional[int]:
        return self.gerente.id if self.gerente else self._gerente_id

    def quitarGerente(self):
        self.gerente = None
        self._gerente_id = None

    def agregarEmpleado(self, e: Empleado) -> bool:
        if any(
            empleado is e
            or (empleado.id is not None and empleado.id == e.id)
            for empleado in self._empleados
        ):
            return False
        self._empleados.append(e)
        if self.id is not None:
            e.asignarDepartamento(self.id)
        return True

    def quitarEmpleado(self, e: Empleado) -> bool:
        if e in self._empleados:
            self._empleados.remove(e)
            if e.departamento_id == self.id:
                e.asignarDepartamento(None)
            if self.gerente is e:
                self.quitarGerente()
            return True
        return False

    @property
    def empleados(self) -> tuple[Empleado, ...]:
        return tuple(self._empleados)

    def cantidad_empleados(self) -> int:
        return len(self._empleados)