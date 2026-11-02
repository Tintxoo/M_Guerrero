import hashlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dominio.usuario import Usuario
from servicios.seguridad import hash_password, needs_rehash, verify_password
from servicios.permisos import exigir_administrador, exigir_empleado, exigir_rol


class UsuarioTests(unittest.TestCase):
    def test_hash_password_verifica_contrasena_y_usa_sal_aleatoria(self):
        password = "contrasena-segura"
        hash_uno = hash_password(password)
        hash_dos = hash_password(password)

        self.assertNotEqual(hash_uno, hash_dos)
        self.assertTrue(verify_password(password, hash_uno))
        self.assertFalse(verify_password("otra-contrasena", hash_uno))
        self.assertFalse(needs_rehash(hash_uno))

    def test_hash_sha256_heredado_se_verifica_y_requiere_migracion(self):
        password = "contrasena-antigua"
        hash_antiguo = hashlib.sha256(password.encode("utf-8")).hexdigest()

        self.assertTrue(verify_password(password, hash_antiguo))
        self.assertFalse(verify_password("incorrecta", hash_antiguo))
        self.assertTrue(needs_rehash(hash_antiguo))

    def test_inicio_de_sesion_migra_hash_sha256_heredado(self):
        from presentacion import menu_usuario

        password = "contrasena-antigua"
        hash_antiguo = hashlib.sha256(password.encode("utf-8")).hexdigest()
        usuario = Usuario("ana", hash_antiguo, 1)

        with (
            patch("builtins.input", return_value="ana"),
            patch("presentacion.menu_usuario.getpass", return_value=password),
            patch.object(menu_usuario.UsuarioDAO, "buscar_por_nombre", return_value=usuario),
            patch.object(menu_usuario.UsuarioDAO, "actualizar", return_value=True) as actualizar,
            patch("builtins.print"),
        ):
            self.assertTrue(menu_usuario.iniciar_sesion())

        actualizar.assert_called_once_with(usuario)
        self.assertTrue(verify_password(password, usuario.password_hash))
        self.assertFalse(needs_rehash(usuario.password_hash))

    def test_empleado_no_puede_registrar_cuentas(self):
        from presentacion.menu_usuario import registrar_usuario

        usuario = Usuario("carlos", "hash_seguro_123", 2)
        with patch("builtins.input") as leer_input, patch("builtins.print"):
            registrar_usuario(usuario)
        leer_input.assert_not_called()

    def test_usuario_se_normaliza_y_valida(self):
        usuario = Usuario("  ANA  ", "hash_seguro_123", 2)
        self.assertEqual(usuario.nombre_usuario, "ana")
        self.assertEqual(usuario.password_hash, "hash_seguro_123")
        self.assertEqual(usuario.empleado_id, 2)
        self.assertEqual(usuario.rol, Usuario.ROL_EMPLEADO)

        administrador = Usuario(
            "ana.torres",
            "hash_seguro_123",
            1,
            rol=Usuario.ROL_ADMINISTRADOR,
        )
        self.assertEqual(administrador.rol, Usuario.ROL_ADMINISTRADOR)

    def test_usuario_rechaza_datos_invalidos(self):
        with self.assertRaises(ValueError):
            Usuario("ab", "hash_seguro_123", 1)
        with self.assertRaises(ValueError):
            Usuario("nombre_valido", "abc", 1)
        with self.assertRaises(ValueError):
            Usuario("nombre_valido", "hash_seguro_123", 0)
        with self.assertRaises(ValueError):
            Usuario("nombre_valido", "hash_seguro_123", -1)
        with self.assertRaises(ValueError):
            Usuario("nombre_valido", "hash_seguro_123", 1, rol="superusuario")

    def test_permisos_rechazan_rol_incorrecto(self):
        empleado = Usuario("empleado", "hash_seguro_123", 2)
        administrador = Usuario(
            "ana.torres",
            "hash_seguro_123",
            1,
            rol=Usuario.ROL_ADMINISTRADOR,
        )

        exigir_empleado(empleado)
        exigir_administrador(administrador)
        with self.assertRaises(PermissionError):
            exigir_administrador(empleado)
        with self.assertRaises(PermissionError):
            exigir_empleado(administrador)
        with self.assertRaises(ValueError):
            exigir_rol(empleado, "superusuario")


if __name__ == "__main__":
    unittest.main()
