import math
import os
import re
import subprocess
import sys
from collections.abc import Callable
from datetime import date
from typing import TypeVar


_PATRON_DECIMAL = re.compile(r"^[0-9]+(?:[.,][0-9]{1,2})?$")
_PATRON_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_PATRON_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PATRON_TELEFONO = re.compile(r"^\+?[0-9][0-9 ()-]{5,19}$")
_PATRON_NOMBRE = re.compile(
    r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+(?:[ '-][A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)*$"
)
T = TypeVar("T")


def limpiar_consola():
    if not sys.stdout.isatty():
        return
    comando = ["cmd.exe", "/c", "cls"] if os.name == "nt" else ["clear"]
    subprocess.run(comando, check=False)


def pausar():
    try:
        input("\nPresione Enter para continuar...")
    except EOFError:
        return


def leer_texto(
    mensaje: str,
    *,
    obligatorio: bool = True,
    maximo: int = 200,
    minimo: int = 1,
) -> str:
    while True:
        valor = input(mensaje).strip()
        if not valor and not obligatorio:
            return ""
        if len(valor) < minimo:
            print(f"Debe ingresar al menos {minimo} carácter(es).")
        elif len(valor) > maximo:
            print(f"El texto no puede superar {maximo} caracteres.")
        elif any(ord(caracter) < 32 for caracter in valor):
            print("El texto contiene caracteres de control no permitidos.")
        else:
            return valor


def leer_nombre(mensaje: str, *, obligatorio: bool = True) -> str:
    while True:
        if obligatorio:
            valor = leer_texto(mensaje, maximo=100)
        else:
            valor = input(mensaje).strip()
            if not valor:
                return ""
            if len(valor) > 100:
                print("El nombre no puede superar 100 caracteres.")
                continue
        if _PATRON_NOMBRE.fullmatch(valor):
            return valor
        print("Use solo letras, espacios, guiones o apóstrofes.")


def leer_correo_opcional(mensaje: str) -> str | None:
    while True:
        valor = input(mensaje).strip()
        if not valor:
            return None
        if _PATRON_EMAIL.fullmatch(valor):
            return valor
        print("Ingrese un correo válido, por ejemplo nombre@dominio.cl.")


def leer_correo(mensaje: str) -> str:
    while True:
        valor = leer_texto(mensaje, maximo=150)
        if _PATRON_EMAIL.fullmatch(valor):
            return valor
        print("Ingrese un correo válido, por ejemplo nombre@dominio.cl.")


def leer_telefono_opcional(mensaje: str) -> str | None:
    while True:
        valor = input(mensaje).strip()
        if not valor:
            return None
        digitos = sum(caracter.isdigit() for caracter in valor)
        if _PATRON_TELEFONO.fullmatch(valor) and 7 <= digitos <= 15:
            return valor
        print("Ingrese un teléfono con 7 a 15 dígitos; puede incluir +, espacios o guiones.")


def leer_telefono(mensaje: str) -> str:
    while True:
        valor = leer_texto(mensaje, maximo=20)
        digitos = sum(caracter.isdigit() for caracter in valor)
        if _PATRON_TELEFONO.fullmatch(valor) and 7 <= digitos <= 15:
            return valor
        print("Ingrese un teléfono con 7 a 15 dígitos; puede incluir +, espacios o guiones.")


def leer_entero(mensaje: str, *, minimo: int = 1, maximo: int | None = None) -> int:
    while True:
        valor = input(mensaje).strip()
        if not re.fullmatch(r"[0-9]+", valor):
            print("Ingrese un número entero sin signos ni decimales.")
            continue
        numero = int(valor)
        if numero < minimo:
            print(f"El número debe ser mayor o igual a {minimo}.")
        elif maximo is not None and numero > maximo:
            print(f"El número debe ser menor o igual a {maximo}.")
        else:
            return numero


def leer_id_opcional(
    mensaje: str,
    *,
    permitir_quitar: bool = False,
) -> int | None:
    while True:
        valor = input(mensaje).strip()
        if not valor:
            return None
        if not re.fullmatch(r"[0-9]+", valor):
            print("Ingrese un ID entero positivo.")
        elif int(valor) == 0 and permitir_quitar:
            return None
        elif int(valor) > 0:
            return int(valor)
        else:
            print("El ID debe ser un entero positivo.")


def leer_entidad_existente(
    mensaje: str,
    buscar: Callable[[int], T | None],
    nombre_entidad: str,
) -> T:
    while True:
        id_entidad = leer_entero(mensaje)
        entidad = buscar(id_entidad)
        if entidad is not None:
            return entidad
        print(f"No existe {nombre_entidad} con ese ID. Intente nuevamente.")


def leer_decimal(
    mensaje: str,
    *,
    minimo: float = 0,
    estrictamente_mayor: bool = False,
) -> float:
    while True:
        valor = input(mensaje).strip()
        try:
            return convertir_decimal(
                valor,
                minimo=minimo,
                estrictamente_mayor=estrictamente_mayor,
            )
        except ValueError as error:
            print(error)


def leer_decimal_opcional(
    mensaje: str,
    *,
    minimo: float = 0,
    estrictamente_mayor: bool = False,
) -> float | None:
    while True:
        valor = input(mensaje).strip()
        if not valor:
            return None
        try:
            return convertir_decimal(
                valor,
                minimo=minimo,
                estrictamente_mayor=estrictamente_mayor,
            )
        except ValueError as error:
            print(error)


def convertir_decimal(
    valor: str,
    *,
    minimo: float = 0,
    estrictamente_mayor: bool = False,
) -> float:
    if not _PATRON_DECIMAL.fullmatch(valor):
        raise ValueError(
            "Ingrese un número con hasta dos decimales, usando punto o coma."
        )
    numero = float(valor.replace(",", "."))
    if not math.isfinite(numero):
        raise ValueError("Ingrese un número finito.")
    if estrictamente_mayor and numero <= minimo:
        raise ValueError(f"El valor debe ser mayor que {minimo}.")
    if not estrictamente_mayor and numero < minimo:
        raise ValueError(f"El valor no puede ser menor que {minimo}.")
    return numero

def leer_fecha(
    mensaje: str,
    *,
    obligatorio: bool = True,
    permitir_futuro: bool = False,
    anos_max_antiguedad: int = 80,
    fecha_min: date | None = None,
    fecha_max: date | None = None,
) -> date | None:
    """Lee y valida una fecha ingresada por consola en formato AAAA-MM-DD.

    Por defecto: - No permite fechas futuras (permitir_futuro=False). - No
    permite fechas de más de 80 años de antigüedad.
    """
    hoy = date.today()

    # Configuración de fecha máxima (hoy por defecto si no se permite futuro)
    if fecha_max is None and not permitir_futuro:
        fecha_max = hoy

    # Configuración de fecha mínima (80 años atrás por defecto)
    if fecha_min is None and anos_max_antiguedad is not None:
        try:
            fecha_min = hoy.replace(year=hoy.year - anos_max_antiguedad)
        except ValueError:  # Manejo para años bisiestos (29 de febrero)
            fecha_min = hoy.replace(
                year=hoy.year - anos_max_antiguedad, day=28
            )

    while True:
        valor = input(mensaje).strip()

        # Entrada opcional vacía
        if not valor and not obligatorio:
            return None

        # Formato de texto AAAA-MM-DD
        if not _PATRON_FECHA.fullmatch(valor):
            print("Use el formato AAAA-MM-DD, por ejemplo 2026-10-13.")
            continue

        # Existencia en el calendario
        try:
            fecha_ingresada = date.fromisoformat(valor)
        except ValueError:
            print("La fecha indicada no existe en el calendario.")
            continue

        # Validación de fecha demasiado antigua
        if fecha_min is not None and fecha_ingresada < fecha_min:
            print(
                f"La fecha no puede ser anterior a {fecha_min.isoformat()} "
                f"(máximo {anos_max_antiguedad} años de antigüedad)."
            )
            continue

        # Validación de fecha futura / posterior
        if fecha_max is not None and fecha_ingresada > fecha_max:
            print(
                f"La fecha no puede ser posterior a {fecha_max.isoformat()}."
            )
            continue

        return fecha_ingresada


def leer_opcion(mensaje: str, opciones: set[str]) -> str:
    while True:
        try:
            valor = input(mensaje).strip()
        except EOFError:
            return "0"
        if valor in opciones:
            return valor
        print(f"Seleccione una opción válida: {', '.join(sorted(opciones))}.")
