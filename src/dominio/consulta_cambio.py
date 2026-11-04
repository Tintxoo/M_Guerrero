from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class ConsultaCambio:
    id: int
    moneda: str
    fecha_valor: date
    valor: float
    consultado_en: datetime
