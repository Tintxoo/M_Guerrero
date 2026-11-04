import contextlib
import io
import os
import sqlite3
import sys
import tempfile
import unittest
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dominio.departamento import Departamento
from dominio.empleado import Empleado
from dominio.proyecto import Proyecto
from dominio.registro_tiempo import RegistroTiempo
from dominio.usuario import Usuario
from presentacion.menu_cambio import menu_cambio
from presentacion.menu_empleado import asignar_proyecto, quitar_asignacion_proyecto
from presentacion.menu_autoservicio import (
    cambiar_credenciales,
    consultar_mis_registros,
    menu_autoservicio_empleado,
    modificar_mi_perfil,
)
from presentacion.menu_proyecto import buscar_proyecto, listar_proyectos
from presentacion.menu_usuario import registrar_usuario
from persistencia.crear_db import crear_tablas
from persistencia.consulta_cambio_dao import ConsultaCambioDAO
from persistencia.departamento_dao import DepartamentoDAO
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.proyecto_dao import ProyectoDAO
from persistencia.registro_tiempo_dao import RegistroTiempoDAO
from persistencia.semillas import inicializar_base_datos
from persistencia.usuario_dao import UsuarioDAO
from servicios.seguridad import hash_password, verify_password
from servicios.consultar_dolar import extraer_tasas_dolar
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

    def test_perfil_empleado_actualiza_datos_permitidos(self):
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
            EmpleadoDAO.actualizar_perfil(
                empleado.id,
                "Luis Pérez",
                "luis.perez@example.com",
                "Calle 3",
                "+56912345678",
            )
        )
        actualizado = EmpleadoDAO.obtenerPorId(empleado.id)
        self.assertEqual(actualizado.nombre, "Luis Pérez")
        self.assertEqual(actualizado.email, "luis.perez@example.com")
        self.assertEqual(actualizado.direccion, "Calle 3")
        self.assertEqual(actualizado.telefono, "+56912345678")
        self.assertEqual(actualizado.salario, 1100)
        self.assertEqual(actualizado.departamento_id, departamento.id)

    def test_perfil_rechaza_correo_ya_usado_por_otro_empleado(self):
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

        with self.assertRaisesRegex(ValueError, "ya está asociado"):
            EmpleadoDAO.actualizar_perfil(
                empleados[0].id,
                empleados[0].nombre,
                "CARLOS@example.com",
                empleados[0].direccion,
                empleados[0].telefono,
            )

        actualizado = EmpleadoDAO.obtenerPorId(empleados[0].id)
        self.assertEqual(actualizado.email, "ana@example.com")

    def test_formulario_perfil_ignora_datos_iguales_y_permite_actualizar_ficha(self):
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
        usuario = Usuario("ana", "hash_seguro", empleado.id)
        salida = io.StringIO()

        with patch("builtins.input", side_effect=["", "", "", ""]):
            with contextlib.redirect_stdout(salida):
                modificar_mi_perfil(usuario)

        self.assertIn("No se realizaron cambios.", salida.getvalue())
        self.assertEqual(EmpleadoDAO.obtenerPorId(empleado.id).direccion, "Calle 1")

        with patch(
            "builtins.input",
            side_effect=["", "ana.nueva@example.com", "Calle 2", "+56912345678"],
        ):
            with contextlib.redirect_stdout(salida):
                modificar_mi_perfil(usuario)

        actualizado = EmpleadoDAO.obtenerPorId(empleado.id)
        self.assertEqual(actualizado.email, "ana.nueva@example.com")
        self.assertEqual(actualizado.direccion, "Calle 2")
        self.assertEqual(actualizado.telefono, "+56912345678")
        self.assertIn("Tu ficha fue actualizada correctamente.", salida.getvalue())

    def test_empleado_cambia_usuario_y_contrasena(self):
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
        usuario = UsuarioDAO.insertar(
            Usuario("ana.torres", hash_password("clave-anterior"), empleado.id)
        )
        salida = io.StringIO()

        with (
            patch("builtins.input", return_value="ana.nueva"),
            patch(
                "presentacion.menu_autoservicio.getpass",
                side_effect=["clave-nueva", "clave-nueva"],
            ),
            contextlib.redirect_stdout(salida),
        ):
            cambiar_credenciales(usuario)

        actualizado = UsuarioDAO.buscar_por_empleado(empleado.id)
        self.assertEqual(actualizado.nombre_usuario, "ana.nueva")
        self.assertTrue(verify_password("clave-nueva", actualizado.password_hash))
        self.assertIn("se actualizaron correctamente", salida.getvalue())

    def test_usuario_no_permite_nombre_existente_sin_distinguir_mayusculas(self):
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
        usuarios = [
            UsuarioDAO.insertar(
                Usuario(nombre, hash_password("clave-valida"), empleado.id)
            )
            for nombre, empleado in zip(("ana.torres", "carlos.ruiz"), empleados)
        ]

        usuarios[0].nombre_usuario = "CARLOS.RUIZ"
        with self.assertRaisesRegex(ValueError, "ya está registrado"):
            UsuarioDAO.actualizar(usuarios[0])

        actualizado = UsuarioDAO.buscar_por_empleado(empleados[0].id)
        self.assertEqual(actualizado.nombre_usuario, "ana.torres")

    def test_cambiar_credenciales_no_actualiza_si_no_hay_cambios(self):
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
        usuario = UsuarioDAO.insertar(
            Usuario("ana.torres", hash_password("clave-actual"), empleado.id)
        )
        salida = io.StringIO()

        with (
            patch("builtins.input", return_value=""),
            patch("presentacion.menu_autoservicio.getpass", return_value=""),
            patch.object(UsuarioDAO, "actualizar") as actualizar,
            contextlib.redirect_stdout(salida),
        ):
            cambiar_credenciales(usuario)

        actualizar.assert_not_called()
        self.assertIn("No se realizaron cambios.", salida.getvalue())

    def test_api_dolar_extrae_monedas_y_fecha_de_actualizacion(self):
        fecha, tasas = extraer_tasas_dolar(
            {
                "result": "success",
                "base_code": "USD",
                "time_last_update_utc": "Wed, 04 Nov 2026 00:02:31 +0000",
                "rates": {"CLP": 980.5, "ARS": 1500.25, "EUR": 0.89},
            }
        )

        self.assertEqual(fecha, date(2026, 11, 4))
        self.assertEqual(tasas, {"CLP": 980.5, "ARS": 1500.25, "EUR": 0.89})

    def test_menu_cambio_guarda_y_muestra_historial_de_consultas(self):
        fecha_tasa = date(2026, 11, 4)
        salida = io.StringIO()
        respuestas = ["1", "2", "", "2", "", "0"]

        with (
            patch(
                "presentacion.menu_cambio.obtener_tasas_dolar",
                return_value=(
                    fecha_tasa,
                    {"CLP": 980.5, "ARS": 1500.25, "EUR": 0.89},
                ),
            ),
            patch("builtins.input", side_effect=respuestas),
            contextlib.redirect_stdout(salida),
        ):
            menu_cambio()

        consultas = ConsultaCambioDAO.listar()
        self.assertEqual(len(consultas), 1)
        self.assertEqual(consultas[0].moneda, "ARS")
        self.assertEqual(consultas[0].fecha_valor, fecha_tasa)
        self.assertEqual(consultas[0].valor, 1500.25)
        self.assertIn("1 USD = 1500.25 ARS", salida.getvalue())
        self.assertIn("Peso argentino (ARS)", salida.getvalue())
        self.assertIn("Fecha del valor: 2026-11-04", salida.getvalue())

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

    def test_administrador_asigna_y_quita_proyectos_de_empleado(self):
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
        proyecto = ProyectoDAO.insertar(
            Proyecto("EcoApp", "Plataforma interna", date(2026, 2, 1))
        )
        salida = io.StringIO()

        with patch(
            "builtins.input",
            side_effect=[
                str(empleado.id),
                str(proyecto.id),
                str(empleado.id),
                str(proyecto.id),
            ],
        ):
            with contextlib.redirect_stdout(salida):
                asignar_proyecto()
                self.assertEqual(
                    [
                        asignado.id
                        for asignado in ProyectoDAO.listarPorEmpleado(empleado.id)
                    ],
                    [proyecto.id],
                )
                self.assertFalse(
                    ProyectoDAO.asignarEmpleado(proyecto.id, empleado.id)
                )
                quitar_asignacion_proyecto()

        self.assertIn("Proyecto asignado correctamente.", salida.getvalue())
        self.assertIn(
            "Asignación de proyecto eliminada correctamente.", salida.getvalue()
        )
        self.assertEqual(ProyectoDAO.listarPorEmpleado(empleado.id), [])

    def test_empleado_consulta_solo_sus_proyectos_asignados(self):
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
        proyectos = [
            ProyectoDAO.insertar(
                Proyecto(nombre, "Proyecto interno", date(2026, 2, 1))
            )
            for nombre in ("EcoApp Ana", "EcoApp Carlos")
        ]
        ProyectoDAO.asignarEmpleado(proyectos[0].id, empleados[0].id)
        ProyectoDAO.asignarEmpleado(proyectos[1].id, empleados[1].id)
        salida = io.StringIO()
        respuestas = ["5", "", "0"]

        with patch("builtins.input", side_effect=respuestas):
            with contextlib.redirect_stdout(salida):
                menu_autoservicio_empleado(
                    Usuario("ana", "hash_seguro", empleados[0].id)
                )

        self.assertIn("EcoApp Ana", salida.getvalue())
        self.assertNotIn("EcoApp Carlos", salida.getvalue())

    def test_administrador_ve_empleados_asignados_y_sus_registros_en_proyecto(self):
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
        for empleado in empleados:
            ProyectoDAO.asignarEmpleado(proyecto.id, empleado.id)
        RegistroTiempoDAO.insertar(
            RegistroTiempo(
                date(2026, 2, 3),
                2.5,
                "Desarrollo Ana",
                empleados[0].id,
                proyecto.id,
            )
        )
        RegistroTiempoDAO.insertar(
            RegistroTiempo(
                date(2026, 2, 4),
                1.5,
                "Pruebas Carlos",
                empleados[1].id,
                proyecto.id,
            )
        )
        salida = io.StringIO()

        with patch("builtins.input", return_value=str(proyecto.id)):
            with contextlib.redirect_stdout(salida):
                buscar_proyecto()

        texto = salida.getvalue()
        self.assertIn("Empleado: Ana Torres", texto)
        self.assertIn("Registro 1", texto)
        self.assertIn("Desarrollo Ana", texto)
        self.assertIn("Empleado: Carlos Ruiz", texto)
        self.assertIn("Pruebas Carlos", texto)

    def test_proyecto_muestra_empleado_asignado_aunque_no_tenga_registros(self):
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
        proyecto = ProyectoDAO.insertar(
            Proyecto("EcoApp", "Plataforma interna", date(2026, 2, 1))
        )
        ProyectoDAO.asignarEmpleado(proyecto.id, empleado.id)
        salida = io.StringIO()

        with patch("builtins.input", return_value=""):
            with contextlib.redirect_stdout(salida):
                listar_proyectos()

        self.assertIn("Empleado: Ana Torres", salida.getvalue())
        self.assertIn("Sin registros de tiempo en este proyecto.", salida.getvalue())

    def test_empleado_registra_tiempo_propio_y_lo_ve_en_su_historial(self):
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
        ProyectoDAO.asignarEmpleado(proyecto.id, empleados[0].id)
        proyecto_no_asignado = ProyectoDAO.insertar(
            Proyecto("EcoApp ajeno", "Proyecto de otro empleado", date(2026, 2, 1))
        )
        RegistroTiempoDAO.insertar(
            RegistroTiempo(
                fecha=date(2026, 2, 3),
                horas=2,
                descripcion="Registro privado Carlos",
                empleado_id=empleados[1].id,
                proyecto_id=proyecto.id,
            )
        )
        usuario = Usuario("ana", "hash_seguro", empleados[0].id)
        salida = io.StringIO()
        respuestas = [
            "4",
            str(proyecto_no_asignado.id),
            str(proyecto.id),
            "2026-02-04",
            "2,5",
            "Trabajo propio",
            "",
            "2", "", "0",
        ]

        with patch("builtins.input", side_effect=respuestas):
            with contextlib.redirect_stdout(salida):
                menu_autoservicio_empleado(usuario)

        registros = RegistroTiempoDAO.listarPorEmpleado(empleados[0].id)
        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0].empleado_id, empleados[0].id)
        self.assertEqual(registros[0].proyecto_id, proyecto.id)
        self.assertEqual(registros[0].horas, 2.5)
        self.assertIn("Registro guardado correctamente", salida.getvalue())
        self.assertIn("El proyecto no está asignado a tu cuenta.", salida.getvalue())
        self.assertIn("Trabajo propio", salida.getvalue())
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
            Empleado(
                " ",
                "Calle 1",
                "555-0101",
                "ana@example.com",
                date.today(),
                100,
            )
        with self.assertRaises(ValueError):
            Empleado(
                "Ana",
                "Calle 1",
                "555-0101",
                "ana@example.com",
                date.today(),
                -1,
            )
        with self.assertRaises(ValueError):
            Empleado(
                "Ana",
                "Calle 1",
                "555-0101",
                "ana@.com",
                date.today(),
                100,
            )
        with self.assertRaises(ValueError):
            Empleado(
                "Ana",
                "Calle 1",
                "555-0101",
                "ana@example.com",
                date.today(),
                float("nan"),
            )
        with self.assertRaises(ValueError):
            Empleado(
                "Ana",
                "Calle 1",
                "555-0101",
                "ana@example.com",
                date.today(),
                10**5000,
            )
        self.assertEqual(
            Empleado(
                "Ana",
                "Calle 1",
                "555-0101",
                "ana@example.com",
                date.today(),
                Decimal("100.50"),
            ).salario,
            100.5,
        )
        with self.assertRaises(ValueError):
            RegistroTiempo(date.today(), 0, "Sin horas", 1, 1)
        with self.assertRaises(ValueError):
            RegistroTiempo(date.today(), float("nan"), "Horas inválidas", 1, 1)
        with self.assertRaises(ValueError):
            RegistroTiempo(date.today(), Decimal("Infinity"), "Horas inválidas", 1, 1)
        with self.assertRaises(ValueError):
            RegistroTiempo(datetime.now(), 1, "Fecha inválida", 1, 1)
        with self.assertRaises(ValueError):
            RegistroTiempo("2026-02-30", 1, "Fecha inválida", 1, 1)

        registro = RegistroTiempo(date.today(), 1, "Tarea", 1, 1)
        with self.assertRaises(ValueError):
            registro.modificarRegistro(0, "Horas inválidas")
        with self.assertRaises(ValueError):
            registro.modificarRegistro(1, " ")

    def test_daos_revalidan_entidades_mutadas_antes_de_guardar(self):
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
        proyecto = ProyectoDAO.insertar(
            Proyecto("EcoApp", "Plataforma interna", date(2026, 2, 1))
        )
        registro = RegistroTiempo(
            date(2026, 2, 3),
            2,
            "Tarea",
            empleado.id,
            proyecto.id,
        )
        registro.horas = float("inf")
        with self.assertRaises(ValueError):
            RegistroTiempoDAO.insertar(registro)
        self.assertEqual(RegistroTiempoDAO.listar(), [])

        empleado.salario = float("nan")
        with self.assertRaises(ValueError):
            EmpleadoDAO.actualizar(empleado)
        self.assertEqual(
            EmpleadoDAO.obtenerPorId(empleado.id).salario,
            1250,
        )

        proyecto.nombre = " "
        with self.assertRaises(ValueError):
            ProyectoDAO.actualizar(proyecto)
        self.assertEqual(ProyectoDAO.obtenerPorId(proyecto.id).nombre, "EcoApp")

    def test_insertar_empleado_rechaza_correo_existente_sin_distinguir_mayusculas(self):
        EmpleadoDAO.insertar(
            Empleado(
                "Ana Torres",
                "Calle 1",
                "555-0101",
                "ana@example.com",
                date(2026, 1, 2),
                1250,
            )
        )
        with self.assertRaisesRegex(ValueError, "ya está asociado"):
            EmpleadoDAO.insertar(
                Empleado(
                    "Ana Duplicada",
                    "Calle 2",
                    "555-0102",
                    "ANA@example.com",
                    date(2026, 1, 3),
                    1200,
                )
            )

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

    def test_semilla_asigna_proyectos_y_registro_a_cada_empleado_sin_duplicar(self):
        inicializar_base_datos()

        departamentos = DepartamentoDAO.listar()
        empleados = EmpleadoDAO.listar()
        proyectos = ProyectoDAO.listar()
        proyectos_por_nombre = {proyecto.nombre: proyecto for proyecto in proyectos}
        proyectos_semilla = {
            f"Proyecto - {departamento.nombre}"[:100]: departamento
            for departamento in departamentos
        }
        usuarios = {usuario.empleado_id: usuario for usuario in UsuarioDAO.listar()}
        empleados_asignables = [
            empleado
            for empleado in empleados
            if usuarios[empleado.id].rol != Usuario.ROL_ADMINISTRADOR
        ][:10]

        self.assertEqual(
            set(proyectos_semilla).intersection(proyectos_por_nombre),
            set(proyectos_semilla),
        )
        self.assertEqual(len(proyectos_semilla), len(departamentos))
        for empleado in empleados_asignables:
            asignaciones = ProyectoDAO.listarPorEmpleado(empleado.id)
            self.assertEqual(len(asignaciones), 1)
            self.assertIn(asignaciones[0].nombre, proyectos_semilla)
        for empleado in empleados:
            if usuarios[empleado.id].rol == Usuario.ROL_ADMINISTRADOR:
                self.assertEqual(ProyectoDAO.listarPorEmpleado(empleado.id), [])

        registros_antes = RegistroTiempoDAO.listar()
        self.assertTrue(
            all(
                any(registro.empleado_id == empleado.id for registro in registros_antes)
                for empleado in empleados
            )
        )
        conteo_proyectos = len(proyectos)

        inicializar_base_datos()

        self.assertEqual(len(ProyectoDAO.listar()), conteo_proyectos)
        self.assertEqual(len(RegistroTiempoDAO.listar()), len(registros_antes))
        self.assertTrue(
            all(
                RegistroTiempoDAO.listarPorEmpleado(empleado.id)
                for empleado in EmpleadoDAO.listar()
            )
        )
