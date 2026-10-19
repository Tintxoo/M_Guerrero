import os
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
import pymysql
from dotenv import load_dotenv

load_dotenv()


def obtener_motor() -> str:
    return os.getenv("DB_ENGINE", "sqlite").lower()


def abrir_conexion():
    motor = obtener_motor()

    if motor == "sqlite":
        nombre_db = os.getenv("DB_NAME", "ecotech.db")
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_absoluta = os.path.join(directorio_actual, nombre_db)
        conexion = sqlite3.connect(ruta_absoluta, timeout=10)
        conexion.execute("PRAGMA foreign_keys = ON")
        return conexion

    if motor == "mysql":
        variables_requeridas = ("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD")
        faltantes = [nombre for nombre in variables_requeridas if not os.getenv(nombre)]
        if faltantes:
            raise ValueError(
                "Faltan variables de entorno para MySQL: " + ", ".join(faltantes)
            )

        return pymysql.connect(
            host=os.environ["DB_HOST"],
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"],
            charset="utf8mb4",
            connect_timeout=10,
        )

    raise ValueError(f"Motor no soportado: {motor}")


@contextmanager
def conexion_segura():
    conexion = abrir_conexion()
    try:
        yield conexion
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def marcador_sql() -> str:
    return "?" if obtener_motor() == "sqlite" else "%s"


def normalizar_fecha(valor: date | datetime | str) -> str:
    return valor.isoformat() if isinstance(valor, (date, datetime)) else valor
