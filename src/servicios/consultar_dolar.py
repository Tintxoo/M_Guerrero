import math
from datetime import date
from email.utils import parsedate_to_datetime

import requests


MONEDAS_DESTINO = ("CLP", "ARS", "EUR")
_API_TASAS_DOLAR = "https://open.er-api.com/v6/latest/USD"


def obtener_datos():
    respuesta = requests.get(
        "https://mindicador.cl/api/dolar",
        timeout=(3, 5),
    )
    respuesta.raise_for_status()
    return respuesta.json()


def extraer_primero(datos):
    if not isinstance(datos, dict):
        raise ValueError("Respuesta inesperada.")
    serie = datos.get("serie")
    if not isinstance(serie, list) or not serie:
        raise ValueError("No hay valores disponibles.")

    registro = serie[0]
    if not isinstance(registro, dict):
        raise ValueError("El registro del indicador tiene un formato inválido.")
    valor = registro.get("valor")
    if not _es_valor_positivo_finito(valor):
        raise ValueError("Valor del indicador inválido.")

    fecha = registro.get("fecha")
    if not isinstance(fecha, str) or len(fecha) < 10:
        raise ValueError("La fecha del indicador tiene un formato inválido.")
    fecha_str = fecha[:10]
    try:
        date.fromisoformat(fecha_str)
    except ValueError as error:
        raise ValueError("La fecha del indicador tiene un formato inválido.") from error
    return fecha_str, valor


def obtener_tasas_dolar() -> tuple[date, dict[str, float]]:
    respuesta = requests.get(_API_TASAS_DOLAR, timeout=(3, 5))
    respuesta.raise_for_status()
    return extraer_tasas_dolar(respuesta.json())


def extraer_tasas_dolar(datos: object) -> tuple[date, dict[str, float]]:
    if not isinstance(datos, dict) or datos.get("result") != "success":
        raise ValueError("Respuesta inesperada de la API de tipos de cambio.")
    if datos.get("base_code") != "USD":
        raise ValueError("La API no devolvió tasas con base en el dólar estadounidense.")

    fecha_actualizacion = datos.get("time_last_update_utc")
    if not isinstance(fecha_actualizacion, str):
        raise ValueError("La API no informó la fecha de actualización de las tasas.")
    try:
        fecha = parsedate_to_datetime(fecha_actualizacion).date()
    except (TypeError, ValueError) as error:
        raise ValueError("La API devolvió una fecha de actualización inválida.") from error

    tasas = datos.get("rates")
    if not isinstance(tasas, dict):
        raise ValueError("La API no devolvió las tasas de cambio.")

    resultado = {}
    for moneda in MONEDAS_DESTINO:
        valor = tasas.get(moneda)
        if not _es_valor_positivo_finito(valor):
            raise ValueError(f"La tasa de cambio para {moneda} no es válida.")
        resultado[moneda] = float(valor)
    return fecha, resultado


def _es_valor_positivo_finito(valor: object) -> bool:
    if type(valor) not in (int, float):
        return False
    try:
        return math.isfinite(valor) and valor > 0
    except OverflowError:
        return False


if __name__ == "__main__":
    try:
        datos_api = obtener_datos()
        fecha, valor_clp = extraer_primero(datos_api)
        print(f"Fecha del registro: {fecha}")
        print(f"Valor del Dólar (CLP): ${valor_clp}")
    except Exception as error:
        print(f"Ocurrió un error: {error}")
