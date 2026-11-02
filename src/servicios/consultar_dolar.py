import requests
import math

def obtener_datos():
    respuesta = requests.get(
        "https://mindicador.cl/api/dolar",
        timeout=(3, 5),
    )
    respuesta.raise_for_status()
    return respuesta.json()

def extraer_primero(datos):
    # Verificar que la respuesta sea un diccionario.
    if not isinstance(datos, dict):
        raise ValueError("Respuesta inesperada.")

    # Obtener la lista de registros del indicador.
    serie = datos.get("serie")

    # Comprobar que sea una lista y contenga registros.
    if not isinstance(serie, list) or not serie:
        raise ValueError("No hay valores disponibles.")

    # Seleccionar el primer registro y obtener su valor.
    registro = serie[0]
    valor = registro["valor"]

    # Aceptar solo números finitos y mayores que cero.
    if (
        type(valor) not in (int, float)
        or not math.isfinite(valor)
        or valor <= 0
    ):
        raise ValueError("Valor del indicador inválido.")

    # Extraer la fecha limpia (solo los primeros 10 caracteres: YYYY-MM-DD)
    fecha_str = registro.get("fecha", "")[:10]

    # Devolver la fecha limpia y el valor en CLP
    return fecha_str, valor

if __name__ == "__main__":
    try:
        datos_api = obtener_datos()
        fecha, valor_clp = extraer_primero(datos_api)
        print(f"Fecha del registro: {fecha}")
        print(f"Valor del Dólar (CLP): ${valor_clp}")
    except Exception as error:
        print(f"Ocurrió un error: {error}")
