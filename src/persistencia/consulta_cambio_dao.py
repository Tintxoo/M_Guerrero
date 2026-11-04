import math
from datetime import date, datetime, timezone

from dominio.consulta_cambio import ConsultaCambio
from persistencia.conexion import conexion_segura, marcador_sql
from servicios.consultar_dolar import MONEDAS_DESTINO


class ConsultaCambioDAO:
    @staticmethod
    def insertar(moneda: str, fecha_valor: date, valor: float) -> ConsultaCambio:
        if moneda not in MONEDAS_DESTINO:
            raise ValueError("La moneda de destino no está permitida.")
        if type(fecha_valor) is not date:
            raise ValueError("La fecha del valor debe ser válida.")
        if type(valor) not in (int, float):
            raise ValueError("El valor de cambio debe ser positivo y finito.")
        try:
            valor = float(valor)
        except OverflowError as error:
            raise ValueError("El valor de cambio debe ser positivo y finito.") from error
        if not math.isfinite(valor) or valor <= 0:
            raise ValueError("El valor de cambio debe ser positivo y finito.")

        consultado_en = datetime.now(timezone.utc).replace(tzinfo=None)
        marca = marcador_sql()
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"""
                INSERT INTO consulta_cambio
                    (moneda, fecha_valor, valor, consultado_en)
                VALUES ({marca}, {marca}, {marca}, {marca})
                """,
                (
                    moneda,
                    fecha_valor.isoformat(),
                    valor,
                    consultado_en.isoformat(sep=" "),
                ),
            )
            consulta = ConsultaCambio(
                id=cursor.lastrowid,
                moneda=moneda,
                fecha_valor=fecha_valor,
                valor=valor,
                consultado_en=consultado_en,
            )
            conexion.commit()
        return consulta

    @staticmethod
    def listar() -> list[ConsultaCambio]:
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                """
                SELECT id, moneda, fecha_valor, valor, consultado_en
                FROM consulta_cambio
                ORDER BY id DESC
                """
            )
            filas = cursor.fetchall()
        return [ConsultaCambioDAO._fila_a_consulta(fila) for fila in filas]

    @staticmethod
    def _fila_a_consulta(fila) -> ConsultaCambio:
        fecha_valor = (
            fila[2] if isinstance(fila[2], date) else date.fromisoformat(str(fila[2]))
        )
        consultado_en = fila[4]
        if not isinstance(consultado_en, datetime):
            consultado_en = datetime.fromisoformat(str(consultado_en))
        return ConsultaCambio(
            id=fila[0],
            moneda=fila[1],
            fecha_valor=fecha_valor,
            valor=float(fila[3]),
            consultado_en=consultado_en,
        )
