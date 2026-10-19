from __future__ import annotations

from datetime import date
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from dominio.empleado import Empleado
    from dominio.proyecto import Proyecto


class RegistroTiempo:
    def __init__(
        self,
        fecha: date | str,
        horas: float,
        descripcion: str,
        empleado_id: int,
        proyecto_id: int,
        id: Optional[int] = None,
        empleado: Optional[Empleado] = None,
        proyecto: Optional[Proyecto] = None,
    ):
        if horas <= 0:
            raise ValueError("Las horas registradas deben ser mayores que cero.")
        if empleado_id <= 0 or proyecto_id <= 0:
            raise ValueError("El empleado y el proyecto deben tener IDs válidos.")
        if empleado is not None and empleado.id not in (None, empleado_id):
            raise ValueError("El empleado relacionado no coincide con su ID.")
        if proyecto is not None and proyecto.id not in (None, proyecto_id):
            raise ValueError("El proyecto relacionado no coincide con su ID.")
        self.id = id
        self.fecha = fecha
        self.horas = float(horas)
        self.descripcion = descripcion
        self.empleado_id = empleado_id
        self.proyecto_id = proyecto_id
        self.empleado = empleado
        self.proyecto = proyecto

    def modificarRegistro(self, h: float, desc: str):
        if h <= 0:
            raise ValueError("Las horas registradas deben ser mayores que cero.")
        self.horas = float(h)
        self.descripcion = desc

    def mostrar_tiempo(self) -> str:
        return f"{self.fecha} - {self.horas} horas"
