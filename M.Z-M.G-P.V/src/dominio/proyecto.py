from __future__ import annotations

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
        if not nombre.strip():
            raise ValueError("El nombre del proyecto no puede estar vacío.")
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
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
