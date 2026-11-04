from __future__ import annotations

import math
import re
from datetime import date
from decimal import Decimal
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
        horas = self._validar_horas(horas)
        if type(empleado_id) is not int or type(proyecto_id) is not int:
            raise ValueError("El empleado y el proyecto deben tener IDs válidos.")
        if empleado_id <= 0 or proyecto_id <= 0:
            raise ValueError("El empleado y el proyecto deben tener IDs válidos.")
        self._validar_fecha(fecha)
        descripcion = self._validar_descripcion(descripcion)
        if id is not None and (type(id) is not int or id <= 0):
            raise ValueError("El ID del registro debe ser un entero positivo.")
        if empleado is not None and empleado.id not in (None, empleado_id):
            raise ValueError("El empleado relacionado no coincide con su ID.")
        if proyecto is not None and proyecto.id not in (None, proyecto_id):
            raise ValueError("El proyecto relacionado no coincide con su ID.")
        self.id = id
        self.fecha = fecha
        self.horas = horas
        self.descripcion = descripcion
        self.empleado_id = empleado_id
        self.proyecto_id = proyecto_id
        self.empleado = empleado
        self.proyecto = proyecto

    def modificarRegistro(self, h: float, desc: str):
        nuevas_horas = self._validar_horas(h)
        nueva_descripcion = self._validar_descripcion(desc)
        self.horas = nuevas_horas
        self.descripcion = nueva_descripcion

    @staticmethod
    def _validar_horas(horas: float) -> float:
        if isinstance(horas, bool) or not isinstance(horas, (int, float, Decimal)):
            raise ValueError("Las horas deben ser un número finito mayor que cero.")
        try:
            if isinstance(horas, Decimal) and not horas.is_finite():
                raise ValueError(
                    "Las horas deben ser un número finito mayor que cero."
                )
            horas = float(horas)
        except (OverflowError, ValueError) as error:
            raise ValueError(
                "Las horas deben ser un número finito mayor que cero."
            ) from error
        if not math.isfinite(horas) or horas <= 0:
            raise ValueError("Las horas deben ser un número finito mayor que cero.")
        return horas

    @staticmethod
    def _validar_fecha(fecha: date | str) -> None:
        if type(fecha) is date:
            return
        if (
            not isinstance(fecha, str)
            or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fecha)
        ):
            raise ValueError("La fecha debe tener el formato AAAA-MM-DD.")
        try:
            date.fromisoformat(fecha)
        except ValueError as error:
            raise ValueError("La fecha indicada no existe en el calendario.") from error

    @staticmethod
    def _validar_descripcion(descripcion: str) -> str:
        if (
            not isinstance(descripcion, str)
            or not descripcion.strip()
            or len(descripcion.strip()) > 1000
            or any(ord(caracter) < 32 for caracter in descripcion)
        ):
            raise ValueError(
                "La descripción debe tener entre 1 y 1000 caracteres válidos."
            )
        return descripcion.strip()

    def mostrar_tiempo(self) -> str:
        return f"{self.fecha} - {self.horas} horas"
