import os
import sqlite3
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dominio.departamento import Departamento
from dominio.empleado import Empleado
from dominio.proyecto import Proyecto
from dominio.registro_tiempo import RegistroTiempo
from persistencia.crear_db import crear_tablas
from persistencia.departamento_dao import DepartamentoDAO
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.proyecto_dao import ProyectoDAO
from persistencia.registro_tiempo_dao import RegistroTiempoDAO
from cargar_ejemplos import (
    EMPLEADOS_EJEMPLO,
    PROYECTOS_EJEMPLO,
    cargar_datos_ejemplo,
)


class CRUDTests(unittest.TestCase):
    def setUp(self):
        self.directorio = tempfile.TemporaryDirectory()
        self.variables_anteriores = {
            nombre: os.environ.get(nombre)
            for nombre in ("DB_ENGINE", "DB_NAME")
        }
        os.environ["DB_ENGINE"] = "sqlite"
        os.environ["DB_NAME"] = str(Path(self.directorio.name) / "pruebas.db")
        crear_tablas()

    def tearDown(self):
        for nombre, valor in self.variables_anteriores.items():
            if valor is None:
                os.environ.pop(nombre, None)
            else:
                os.environ[nombre] = valor
        self.directorio.cleanup()

    def test_crud_y_relaciones_del_diagrama(self):
        departamento = DepartamentoDAO.insertar(Departamento("Desarrollo"))
        empleado = EmpleadoDAO.insertar(
            Empleado(
                "Ana Pérez",
                "Calle 1",
                "555-0101",
                "ana@example.com",
                date(2026, 1, 2),
                1250,
                departamento.id,
            )
        )
        departamento.agregarEmpleado(empleado)
        departamento.asignarGerente(empleado)
        self.assertTrue(DepartamentoDAO.actualizar(departamento))

        proyecto = ProyectoDAO.insertar(
            Proyecto("EcoApp", "Plataforma interna", date(2026, 2, 1))
        )
        registro = RegistroTiempoDAO.insertar(
            RegistroTiempo(
                fecha=date(2026, 2, 3),
                horas=2.5,
                descripcion="Diseño de interfaz",
                empleado_id=empleado.id,
                proyecto_id=proyecto.id,
                empleado=empleado,
                proyecto=proyecto,
            )
        )
        with self.assertRaises(sqlite3.IntegrityError):
            ProyectoDAO.eliminar(proyecto.id)

        departamento_recuperado = DepartamentoDAO.obtenerPorId(departamento.id)
        self.assertEqual(departamento_recuperado.gerente.id, empleado.id)
        self.assertEqual(departamento_recuperado.cantidad_empleados(), 1)
        self.assertEqual(
            ProyectoDAO.obtenerPorId(proyecto.id).calcularHorasTotales(), 2.5
        )
        self.assertEqual(
            len(EmpleadoDAO.obtenerPorId(empleado.id).registrosTiempo), 1
        )
        self.assertEqual(RegistroTiempoDAO.obtenerPorId(registro.id).empleado.id, empleado.id)

        registro.modificarRegistro(3, "Implementación")
        self.assertTrue(RegistroTiempoDAO.actualizar(registro))
        self.assertEqual(
            ProyectoDAO.obtenerPorId(proyecto.id).calcularHorasTotales(), 3
        )

        empleado.actualizarDatos(salario=1400)
        self.assertTrue(EmpleadoDAO.actualizar(empleado))
        proyecto.descripcion = "Versión actualizada"
        self.assertTrue(ProyectoDAO.actualizar(proyecto))
        departamento.nombre = "Ingeniería"
        self.assertTrue(DepartamentoDAO.actualizar(departamento))

        self.assertTrue(RegistroTiempoDAO.eliminar(registro.id))
        self.assertTrue(EmpleadoDAO.eliminar(empleado.id))
        self.assertTrue(ProyectoDAO.eliminar(proyecto.id))
        self.assertTrue(DepartamentoDAO.eliminar(departamento.id))

    def test_gerente_debe_pertenecer_al_departamento(self):
        departamento = DepartamentoDAO.insertar(Departamento("Operaciones"))
        otro_departamento = DepartamentoDAO.insertar(Departamento("Finanzas"))
        empleado = EmpleadoDAO.insertar(
            Empleado(
                "Luis Soto",
                "Calle 2",
                "555-0102",
                "luis@example.com",
                date(2026, 1, 3),
                1100,
                departamento.id,
            )
        )
        with self.assertRaises(ValueError):
            otro_departamento.asignarGerente(empleado)

        departamento.asignarGerente(empleado)
        DepartamentoDAO.actualizar(departamento)
        empleado.asignarDepartamento(otro_departamento.id)
        EmpleadoDAO.actualizar(empleado)
        self.assertIsNone(DepartamentoDAO.obtenerPorId(departamento.id).gerente)

    def test_validaciones_del_dominio(self):
        with self.assertRaises(ValueError):
            Empleado(" ", "Calle 1", "555", "ana@example.com", date.today(), 100)
        with self.assertRaises(ValueError):
            Empleado("Ana", "Calle 1", "555", "ana@example.com", date.today(), -1)
        with self.assertRaises(ValueError):
            RegistroTiempo(date.today(), 0, "Sin horas", 1, 1)

        registro = RegistroTiempo(date.today(), 1, "Tarea", 1, 1)
        with self.assertRaises(ValueError):
            registro.modificarRegistro(0, "Horas inválidas")

    def test_datos_ejemplo_se_pueden_cargar_mas_de_una_vez(self):
        cargar_datos_ejemplo()
        cargar_datos_ejemplo()

        emails_ejemplo = {datos["email"] for datos in EMPLEADOS_EJEMPLO}
        nombres_proyecto = {datos["nombre"] for datos in PROYECTOS_EJEMPLO}
        empleados_ejemplo = [
            empleado
            for empleado in EmpleadoDAO.listar()
            if empleado.email in emails_ejemplo
        ]
        proyectos_ejemplo = [
            proyecto
            for proyecto in ProyectoDAO.listar()
            if proyecto.nombre in nombres_proyecto
        ]
        registros_ejemplo = [
            registro
            for registro in RegistroTiempoDAO.listar()
            if registro.empleado.email in emails_ejemplo
            and registro.proyecto.nombre in nombres_proyecto
        ]

        self.assertEqual(len(empleados_ejemplo), 2)
        self.assertEqual(len(proyectos_ejemplo), 2)
        self.assertEqual(len(registros_ejemplo), 3)
