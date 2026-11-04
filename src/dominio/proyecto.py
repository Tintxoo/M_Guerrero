from __future__ import annotations

import re
from datetime import date
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from dominio.registro_tiempo import RegistroTiempo


class Proyecto:
    def __init__(
        self,
        nombre: str,
        descripcion: str,
        fechaInicio: date | str,
        id: Optional[int] = None,
    ):
        if (
            not isinstance(nombre, str)
            or not nombre.strip()
            or len(nombre.strip()) > 100
            or any(ord(caracter) < 32 for caracter in nombre)
        ):
            raise ValueError(
                "El nombre del proyecto debe tener entre 1 y 100 caracteres válidos."
            )
        if (
            not isinstance(descripcion, str)
            or len(descripcion.strip()) > 1000
            or any(ord(caracter) < 32 for caracter in descripcion)
        ):
            raise ValueError("La descripción del proyecto no es válida.")
        if type(fechaInicio) not in (date, str):
            raise ValueError("La fecha de inicio del proyecto no es válida.")
        if type(fechaInicio) is str:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fechaInicio):
                raise ValueError("La fecha debe tener el formato AAAA-MM-DD.")
            try:
                date.fromisoformat(fechaInicio)
            except ValueError as error:
                raise ValueError(
                    "La fecha indicada no existe en el calendario."
                ) from error
        if id is not None and (type(id) is not int or id <= 0):
            raise ValueError("El ID del proyecto debe ser un entero positivo.")
        self.id = id
        self.nombre = nombre.strip()
        self.descripcion = descripcion.strip()
        self.fechaInicio = fechaInicio
        self._registros_horas: list[RegistroTiempo] = []

    def agregarRegistro(self, r: RegistroTiempo) -> bool:
        if r not in self._registros_horas:
            self._registros_horas.append(r)
            return True
        return False

    def calcularHorasTotales(self) -> float:
        return sum(
            (registro.horas for registro in self._registros_horas),
            start=0.0,
        )

    @property
    def registrosTiempo(self) -> tuple[RegistroTiempo, ...]:
        return tuple(self._registros_horas)
