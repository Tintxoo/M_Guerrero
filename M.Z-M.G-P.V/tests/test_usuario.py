import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dominio.usuario import Usuario


class UsuarioTests(unittest.TestCase):
    def test_usuario_se_normaliza_y_valida(self):
        usuario = Usuario("  ANA  ", "hash_seguro_123", 2)
        self.assertEqual(usuario.nombre_usuario, "ana")
        self.assertEqual(usuario.password_hash, "hash_seguro_123")
        self.assertEqual(usuario.empleado_id, 2)

    def test_usuario_rechaza_datos_invalidos(self):
        with self.assertRaises(ValueError):
            Usuario("ab", "hash_seguro_123", 1)
        with self.assertRaises(ValueError):
            Usuario("nombre_valido", "abc", 1)
        with self.assertRaises(ValueError):
            Usuario("nombre_valido", "hash_seguro_123", 0)
        with self.assertRaises(ValueError):
            Usuario("nombre_valido", "hash_seguro_123", -1)


if __name__ == "__main__":
    unittest.main()
