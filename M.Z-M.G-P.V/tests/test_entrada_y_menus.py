import builtins
import contextlib
import io
import os
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from persistencia.crear_db import crear_tablas
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.proyecto_dao import ProyectoDAO
from persistencia.registro_tiempo_dao import RegistroTiempoDAO
from presentacion.entrada import (
    leer_correo,
    leer_decimal,
    leer_entero,
    leer_fecha,
    leer_id_opcional,
    leer_nombre,
    limpiar_consola,
)
from presentacion.menu_principal import iniciar_menu_principal


class EntradaYMenusTests(unittest.TestCase):
    def setUp(self):
        self.directorio = tempfile.TemporaryDirectory()
        self.variables_anteriores = {
            nombre: os.environ.get(nombre)
            for nombre in ("DB_ENGINE", "DB_NAME")
        }
        os.environ["DB_ENGINE"] = "sqlite"
        os.environ["DB_NAME"] = str(Path(self.directorio.name) / "menus.db")
        crear_tablas()

    def tearDown(self):
        for nombre, valor in self.variables_anteriores.items():
            if valor is None:
                os.environ.pop(nombre, None)
            else:
                os.environ[nombre] = valor
        self.directorio.cleanup()

    def test_entradas_invalidas_se_rechazan_y_se_vuelven_a_pedir(self):
        with patch.object(builtins, "input", side_effect=["-2", "1.5", "2"]):
            self.assertEqual(leer_entero("ID: "), 2)
        with patch.object(builtins, "input", side_effect=["-1", "abc", "4"]):
            self.assertEqual(leer_id_opcional("ID opcional: "), 4)
        with patch.object(builtins, "input", side_effect=["NaN", "1,25"]):
            self.assertEqual(leer_decimal("Horas: ", estrictamente_mayor=True), 1.25)
        with patch.object(builtins, "input", side_effect=["nombre sin correo", "ana@ejemplo.cl"]):
            self.assertEqual(leer_correo("Correo: "), "ana@ejemplo.cl")
        with patch.object(builtins, "input", side_effect=["ana 1", "Ana Pérez"]):
            self.assertEqual(leer_nombre("Nombre: "), "Ana Pérez")
        with patch.object(builtins, "input", side_effect=["13/10/2026", "2026-02-30", "2026-10-13"]):
            self.assertEqual(leer_fecha("Fecha: "), date(2026, 10, 13))

    def test_flujo_interactivo_registra_y_lista_todas_las_entidades(self):
        respuestas = [
            "1", "1", "Soporte", "", "2", "", "3", "1", "", "0",
            "2", "1", "Anita Lopez", "Avenida 1", "12345678",
            "anita@ejemplo.cl", "2026-01-15", "1200", "1", "", "0",
            "3", "1", "EcoApp", "Gestión interna", "2026-02-01", "", "0",
            "4", "1", "1", "1", "2026-02-03", "2,5",
            "Diseño de interfaz", "", "2", "", "0",
            "0",
        ]
        salida = io.StringIO()
        with patch.object(builtins, "input", side_effect=respuestas):
            with contextlib.redirect_stdout(salida):
                iniciar_menu_principal()

        empleado = EmpleadoDAO.obtenerPorId(1)
        proyecto = ProyectoDAO.obtenerPorId(1)
        registros = RegistroTiempoDAO.listar()
        self.assertEqual(empleado.nombre, "Anita Lopez")
        self.assertEqual(empleado.departamento_id, 1)
        self.assertEqual(proyecto.calcularHorasTotales(), 2.5)
        self.assertEqual(len(registros), 1)
        self.assertIn("Departamento registrado correctamente", salida.getvalue())
        self.assertIn("Nombre: Soporte", salida.getvalue())
        self.assertIn("Empleado registrado correctamente", salida.getvalue())
        self.assertIn("Proyecto registrado correctamente", salida.getvalue())
        self.assertIn("Registro guardado correctamente", salida.getvalue())
        self.assertIn("Diseño de interfaz", salida.getvalue())

    def test_menus_ejecutan_busqueda_actualizacion_y_eliminacion(self):
        respuestas = [
            "1", "1", "Soporte", "", "0",
            "2", "1", "Anita Lopez", "Avenida 1", "12345678",
            "anita@ejemplo.cl", "2026-01-15", "1200", "1", "",
            "2", "", "3", "1", "", "4", "1",
            "", "", "", "", "", "", "", "", "0",
            "3", "1", "EcoApp", "Gestión interna", "2026-02-01", "",
            "2", "", "3", "1", "", "4", "1", "", "", "", "",
            "0", "4", "1", "1", "1", "2026-02-03", "2.5",
            "Diseño de interfaz", "", "2", "", "3", "1", "",
            "4", "1", "0", "3", "", "", "5", "1", "", "0",
            "1", "4", "1", "", "1", "", "0",
            "2", "5", "1", "", "0",
            "3", "5", "1", "", "0",
            "1", "5", "1", "", "0",
            "0",
        ]
        salida = io.StringIO()
        with patch.object(builtins, "input", side_effect=respuestas):
            with contextlib.redirect_stdout(salida):
                iniciar_menu_principal()

        texto = salida.getvalue()
        self.assertIn("Empleado actualizado correctamente.", texto)
        self.assertIn("Proyecto actualizado correctamente.", texto)
        self.assertIn("Registro actualizado correctamente.", texto)
        self.assertIn("Departamento actualizado correctamente.", texto)
        self.assertIn("Registro eliminado correctamente.", texto)
        self.assertIn("Empleado eliminado correctamente.", texto)
        self.assertIn("Proyecto eliminado correctamente.", texto)
        self.assertIn("Departamento eliminado.", texto)
        self.assertEqual(EmpleadoDAO.listar(), [])
        self.assertEqual(ProyectoDAO.listar(), [])
        self.assertEqual(RegistroTiempoDAO.listar(), [])

    def test_limpiar_consola_solo_limpia_terminal_interactivo(self):
        salida_no_interactiva = io.StringIO()
        with patch("presentacion.entrada.subprocess.run") as ejecutar:
            with patch("presentacion.entrada.sys.stdout", salida_no_interactiva):
                limpiar_consola()
        ejecutar.assert_not_called()

        consola = Mock()
        consola.isatty.return_value = True
        with patch("presentacion.entrada.subprocess.run") as ejecutar:
            with patch("presentacion.entrada.sys.stdout", consola):
                limpiar_consola()
        ejecutar.assert_called_once()
