import math
import re
from datetime import date
from decimal import Decimal
from typing import Optional

from dominio.registro_tiempo import RegistroTiempo


_PATRON_NOMBRE = re.compile(
    r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+(?:[ '-][A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)*$"
)
_PATRON_EMAIL = re.compile(
    r"^[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*"
    r"@(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}$"
)
_PATRON_TELEFONO = re.compile(r"^\+?[0-9]+(?:[ ()-]?[0-9]+)*$")


class Empleado:
    def __init__(
        self,
        nombre: str,
        direccion: str,
        telefono: str,
        email: str,
        fechaInicioContrato: date | str,
        salario: float,
        departamento_id: Optional[int] = None,
        id: Optional[int] = None,
    ):
        nombre = self._validar_nombre(nombre)
        direccion = self._validar_direccion(direccion)
        telefono = self._validar_telefono(telefono)
        email = self._validar_email(email)
        self._validar_fecha(fechaInicioContrato)
        salario = self._validar_salario(salario)
        self._validar_id(id, "empleado", opcional=True)
        self._validar_id(departamento_id, "departamento", opcional=True)

        self.id = id
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.email = email
        self.fechaInicioContrato = fechaInicioContrato
        self.salario = salario
        self.departamento_id = departamento_id
        self._registroTiempo: list[RegistroTiempo] = []

    def mostrar_datos(self) -> str:
        return f"{self.nombre} - {self.email} - {self.telefono} - ${self.salario}"

    def actualizarDatos(
        self,
        nombre: Optional[str] = None,
        direccion: Optional[str] = None,
        telefono: Optional[str] = None,
        email: Optional[str] = None,
        salario: Optional[float] = None,
        fechaInicioContrato: Optional[date | str] = None,
    ):
        nuevos_datos = {
            "nombre": self._validar_nombre(
                nombre if nombre is not None else self.nombre
            ),
            "direccion": self._validar_direccion(
                direccion if direccion is not None else self.direccion
            ),
            "telefono": self._validar_telefono(
                telefono if telefono is not None else self.telefono
            ),
            "email": self._validar_email(email if email is not None else self.email),
            "salario": self._validar_salario(
                salario if salario is not None else self.salario
            ),
            "fechaInicioContrato": (
                fechaInicioContrato
                if fechaInicioContrato is not None
                else self.fechaInicioContrato
            ),
        }
        self._validar_fecha(nuevos_datos["fechaInicioContrato"])
        for campo, valor in nuevos_datos.items():
            setattr(self, campo, valor)

    @staticmethod
    def _validar_nombre(nombre: str) -> str:
        if not isinstance(nombre, str) or not _PATRON_NOMBRE.fullmatch(nombre.strip()):
            raise ValueError("El nombre del empleado tiene un formato inválido.")
        if len(nombre.strip()) > 100:
            raise ValueError("El nombre del empleado no puede superar 100 caracteres.")
        return nombre.strip()

    @staticmethod
    def _validar_direccion(direccion: str) -> str:
        if not isinstance(direccion, str):
            raise ValueError("La dirección debe ser texto.")
        direccion = direccion.strip()
        if (
            not direccion
            or len(direccion) > 200
            or any(ord(char) < 32 for char in direccion)
        ):
            raise ValueError("La dirección debe tener entre 1 y 200 caracteres válidos.")
        return direccion

    @staticmethod
    def _validar_telefono(telefono: str) -> str:
        if not isinstance(telefono, str):
            raise ValueError("El teléfono debe ser texto.")
        telefono = telefono.strip()
        digitos = sum(caracter.isdigit() for caracter in telefono)
        if (
            not _PATRON_TELEFONO.fullmatch(telefono)
            or len(telefono) > 20
            or not 7 <= digitos <= 15
        ):
            raise ValueError("El teléfono debe tener de 7 a 15 dígitos válidos.")
        return telefono

    @staticmethod
    def _validar_email(email: str) -> str:
        if (
            not isinstance(email, str)
            or len(email.strip()) > 150
            or not _PATRON_EMAIL.fullmatch(email.strip())
        ):
            raise ValueError("El email del empleado no es válido.")
        return email.strip()

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
    def _validar_salario(salario: float) -> float:
        if isinstance(salario, bool) or not isinstance(
            salario, (int, float, Decimal)
        ):
            raise ValueError("El salario debe ser un número finito no negativo.")
        try:
            if isinstance(salario, Decimal) and not salario.is_finite():
                raise ValueError(
                    "El salario debe ser un número finito no negativo."
                )
            salario = float(salario)
        except (OverflowError, ValueError) as error:
            raise ValueError(
                "El salario debe ser un número finito no negativo."
            ) from error
        if not math.isfinite(salario) or salario < 0:
            raise ValueError("El salario debe ser un número finito no negativo.")
        return salario

    @staticmethod
    def _validar_id(id_valor: int | None, nombre: str, *, opcional: bool) -> None:
        if id_valor is None and opcional:
            return
        if type(id_valor) is not int or id_valor <= 0:
            raise ValueError(f"El ID de {nombre} debe ser un entero positivo.")

    def asignarDepartamento(self, id_departamento: Optional[int]):
        self._validar_id(id_departamento, "departamento", opcional=True)
        self.departamento_id = id_departamento

    def agregarRegistroTiempo(self, registro: RegistroTiempo) -> bool:
        if registro not in self._registroTiempo:
            self._registroTiempo.append(registro)
            return True
        return False

    @property
    def registrosTiempo(self) -> tuple[RegistroTiempo, ...]:
        return tuple(self._registroTiempo)
