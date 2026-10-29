from datetime import date
from typing import Optional

from dominio.registro_tiempo import RegistroTiempo


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
        if not nombre.strip():
            raise ValueError("El nombre del empleado no puede estar vacío.")
        if "@" not in email or email.startswith("@") or email.endswith("@"):
            raise ValueError("El email del empleado no es válido.")
        if salario < 0:
            raise ValueError("El salario no puede ser negativo.")

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
        if nombre is not None:
            if not nombre.strip():
                raise ValueError("El nombre del empleado no puede estar vacío.")
            self.nombre = nombre
        if direccion is not None:
            self.direccion = direccion
        if telefono is not None:
            self.telefono = telefono
        if email is not None:
            if "@" not in email or email.startswith("@") or email.endswith("@"):
                raise ValueError("El email del empleado no es válido.")
            self.email = email
        if salario is not None:
            if salario < 0:
                raise ValueError("El salario no puede ser negativo.")
            self.salario = salario
        if fechaInicioContrato is not None:
            self.fechaInicioContrato = fechaInicioContrato

    def asignarDepartamento(self, id_departamento: Optional[int]):
        self.departamento_id = id_departamento

    def agregarRegistroTiempo(self, registro: RegistroTiempo) -> bool:
        if registro not in self._registroTiempo:
            self._registroTiempo.append(registro)
            return True
        return False

    @property
    def registrosTiempo(self) -> tuple[RegistroTiempo, ...]:
        return tuple(self._registroTiempo)
