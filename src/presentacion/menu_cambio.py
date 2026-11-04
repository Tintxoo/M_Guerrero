from persistencia.consulta_cambio_dao import ConsultaCambioDAO
from servicios.consultar_dolar import obtener_tasas_dolar
from servicios.entrada import leer_opcion, limpiar_consola, pausar


_NOMBRES_MONEDA = {
    "CLP": "Peso chileno",
    "ARS": "Peso argentino",
    "EUR": "Euro",
}
_OPCIONES_MONEDA = {"1": "CLP", "2": "ARS", "3": "EUR"}


def consultar_cambio():
    print("\n--- Consultar cambio del dólar ---")
    print("1. Peso chileno (CLP)")
    print("2. Peso argentino (ARS)")
    print("3. Euro (EUR)")
    opcion = leer_opcion("Seleccione la moneda de destino: ", set(_OPCIONES_MONEDA))
    moneda = _OPCIONES_MONEDA[opcion]
    fecha, tasas = obtener_tasas_dolar()
    consulta = ConsultaCambioDAO.insertar(moneda, fecha, tasas[moneda])
    print(
        f"1 USD = {consulta.valor:.8g} {moneda} "
        f"({_NOMBRES_MONEDA[moneda]})"
    )
    print(f"Fecha del valor: {consulta.fecha_valor.isoformat()}")
    print("Consulta guardada en el historial.")


def mostrar_historial_cambios():
    print("\n--- Historial de consultas del dólar ---")
    consultas = ConsultaCambioDAO.listar()
    if not consultas:
        print("Todavía no hay consultas guardadas.")
        return

    for consulta in consultas:
        print(
            f"{_NOMBRES_MONEDA[consulta.moneda]} ({consulta.moneda}) | "
            f"Fecha del valor: {consulta.fecha_valor.isoformat()} | "
            f"1 USD = {consulta.valor:.8g} {consulta.moneda} | "
            f"Consultado: {consulta.consultado_en.isoformat(sep=' ', timespec='seconds')} UTC"
        )


def menu_cambio():
    while True:
        limpiar_consola()
        print("\n===== CAMBIO DEL DÓLAR =====")
        print("1. Consultar cambio")
        print("2. Ver historial de consultas")
        print("0. Volver")
        opcion = leer_opcion("Seleccione una opción: ", {"0", "1", "2"})
        if opcion == "0":
            return

        try:
            if opcion == "1":
                consultar_cambio()
            else:
                mostrar_historial_cambios()
        except Exception as error:
            print(f"No fue posible completar la consulta: {error}")
        pausar()
