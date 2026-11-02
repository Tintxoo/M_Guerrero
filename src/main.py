from persistencia.crear_db import crear_tablas
from persistencia.semillas import inicializar_base_datos
from presentacion.menu_principal import iniciar_menu_principal
from presentacion.menu_usuario import menu_usuario


def main():
    try:
        crear_tablas()
        inicializar_base_datos()
    except Exception as error:
        raise SystemExit(f"No fue posible inicializar la base de datos: {error}") from error

    usuario = menu_usuario()
    if usuario is not None:
        iniciar_menu_principal(usuario)


if __name__ == "__main__":
    main()