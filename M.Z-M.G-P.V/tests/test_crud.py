import contextlib
import io
import os
import sqlite3
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dominio.departamento import Departamento
from dominio.empleado import Empleado
from dominio.proyecto import Proyecto
from dominio.registro_tiempo import RegistroTiempo
from dominio.usuario import Usuario
from presentacion.menu_autoservicio import consultar_mis_registros
from presentacion.menu_usuario import registrar_usuario
from persistencia.crear_db import crear_tablas
from persistencia.departamento_dao import DepartamentoDAO
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.proyecto_dao import ProyectoDAO
from persistencia.registro_tiempo_dao import RegistroTiempoDAO
from persistencia.usuario_dao import UsuarioDAO
from servicios.seguridad import hash_password, verify_password
from scripts.cargar_ejemplos import (
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

    def test_usuario_guarda_rol_y_no_permite_actualizarlo_con_dao(self):
        empleado = EmpleadoDAO.insertar(
            Empleado(
                "Ana Torres",
                "Calle 1",
                "555-0101",
                "ana@example.com",
                date(2026, 1, 2),
                1250,
            )
        )
        usuario = Usuario(
            "ana.torres",
            hash_password("clave-segura"),
            empleado.id,
            rol=Usuario.ROL_ADMINISTRADOR,
        )
        UsuarioDAO.insertar(usuario)

        usuario.rol = Usuario.ROL_EMPLEADO
        self.assertTrue(UsuarioDAO.actualizar(usuario))
        guardado = UsuarioDAO.buscar_por_nombre("ana.torres")
        self.assertEqual(guardado.rol, Usuario.ROL_ADMINISTRADOR)
        self.assertEqual(guardado.empleado_id, empleado.id)

    def test_administrador_registra_cuenta_con_rol_empleado(self):
        empleado = EmpleadoDAO.insertar(
            Empleado(
                "Carlos Ruiz",
                "Calle 2",
                "555-0102",
                "carlos@example.com",
                date(2026, 1, 3),
                1100,
            )
        )
        administrador = Usuario(
            "ana.torres",
            "hash_seguro",
            1,
            rol=Usuario.ROL_ADMINISTRADOR,
        )

        with (
            patch("builtins.input", side_effect=["carlos.ruiz", str(empleado.id)]),
            patch("presentacion.menu_usuario.getpass", return_value="clave-segura"),
            patch("builtins.print"),
        ):
            registrar_usuario(administrador)

        cuenta = UsuarioDAO.buscar_por_nombre("carlos.ruiz")
        self.assertEqual(cuenta.rol, Usuario.ROL_EMPLEADO)
        self.assertTrue(verify_password("clave-segura", cuenta.password_hash))

    def test_migracion_legacy_asigna_ana_admin_y_resto_empleado(self):
        db_anterior = os.environ["DB_NAME"]
        ruta_legacy = str(Path(self.directorio.name) / "legacy.db")
        os.environ["DB_NAME"] = ruta_legacy
        try:
            conexion = sqlite3.connect(ruta_legacy)
            try:
                conexion.execute(
                    """
                    CREATE TABLE usuario (
                        id INTEGER PRIMARY KEY,
                        nombre_usuario TEXT NOT NULL,
                        password_hash TEXT NOT NULL,
                        empleado_id INTEGER NOT NULL
                    )
                    """
                )
                conexion.executemany(
                    """
                    INSERT INTO usuario (id, nombre_usuario, password_hash, empleado_id)
                    VALUES (?, ?, ?, ?)
                    """,
                    [
                    (1, "ana.torres", "legacy_hash", 1),
                    (2, "carlos.ruiz", "legacy_hash", 2),
                    ],
                )
                conexion.commit()
            finally:
                conexion.close()

            crear_tablas()
            ana = UsuarioDAO.buscar_por_nombre("ana.torres")
            carlos = UsuarioDAO.buscar_por_nombre("carlos.ruiz")
            self.assertEqual(ana.rol, Usuario.ROL_ADMINISTRADOR)
            self.assertEqual(carlos.rol, Usuario.ROL_EMPLEADO)
        finally:
            os.environ["DB_NAME"] = db_anterior

    def test_perfil_empleado_solo_actualiza_nombre_y_correo(self):
        departamento = DepartamentoDAO.insertar(Departamento("Tecnología"))
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

        self.assertTrue(
            EmpleadoDAO.actualizar_perfil(empleado.id, "Luis Pérez", "luis.perez@example.com")
        )
        actualizado = EmpleadoDAO.obtenerPorId(empleado.id)
        self.assertEqual(actualizado.nombre, "Luis Pérez")
        self.assertEqual(actualizado.email, "luis.perez@example.com")
        self.assertEqual(actualizado.direccion, "Calle 2")
        self.assertEqual(actualizado.telefono, "555-0102")
        self.assertEqual(actualizado.salario, 1100)
        self.assertEqual(actualizado.departamento_id, departamento.id)

    def test_empleado_consulta_solo_sus_registros(self):
        empleados = [
            EmpleadoDAO.insertar(
                Empleado(
                    nombre,
                    "Calle 1",
                    "555-0101",
                    email,
                    date(2026, 1, 2),
                    1250,
                )
            )
            for nombre, email in (
                ("Ana Torres", "ana@example.com"),
                ("Carlos Ruiz", "carlos@example.com"),
            )
        ]
        proyecto = ProyectoDAO.insertar(
            Proyecto("EcoApp", "Plataforma interna", date(2026, 2, 1))
        )
        for empleado, descripcion in zip(
            empleados, ("Registro privado Ana", "Registro privado Carlos")
        ):
            RegistroTiempoDAO.insertar(
                RegistroTiempo(
                    fecha=date(2026, 2, 3),
                    horas=2,
                    descripcion=descripcion,
                    empleado_id=empleado.id,
                    proyecto_id=proyecto.id,
                )
            )

        usuario = Usuario("ana", "hash_seguro", empleados[0].id)
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            consultar_mis_registros(usuario)

        self.assertIn("Registro privado Ana", salida.getvalue())
        self.assertNotIn("Registro privado Carlos", salida.getvalue())

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
