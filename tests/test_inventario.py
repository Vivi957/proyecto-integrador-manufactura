import unittest
from unittest.mock import MagicMock

class InventarioService:
    def __init__(self, stock_repository):
        self.stock_repo = stock_repository

    def verificar_y_reservar(self, sku: str, cantidad_requerida: int) -> bool:
        stock_actual = self.stock_repo.obtener_stock(sku)
        stock_seguridad = self.stock_repo.obtener_stock_seguridad(sku)
        
        # Regla de negocio crítica: Bloquear si cae por debajo del stock de seguridad
        if (stock_actual - cantidad_requerida) < stock_seguridad:
            return False
        
        self.stock_repo.descontar_stock(sku, cantidad_requerida)
        return True

class TestInventarioService(unittest.TestCase):
    def setUp(self):
        # Mock para aislar la base de datos (Pirámide de Cohn / TDD)
        self.mock_repo = MagicMock()
        self.servicio = InventarioService(self.mock_repo)

    def test_bloquear_orden_si_stock_inferior_a_seguridad(self):
        # Stock actual 15, seguridad 10, requeridos 8 -> Quedarían 7 (< 10) -> Debe bloquear
        self.mock_repo.obtener_stock.return_value = 15
        self.mock_repo.obtener_stock_seguridad.return_value = 10

        resultado = self.servicio.verificar_y_reservar("MAT-ACERO-01", 8)

        self.assertFalse(resultado)
        self.mock_repo.descontar_stock.assert_not_called()

    def test_aprobar_orden_con_stock_suficiente(self):
        # Stock actual 50, seguridad 10, requeridos 10 -> Quedarían 40 (>= 10) -> Debe aprobar
        self.mock_repo.obtener_stock.return_value = 50
        self.mock_repo.obtener_stock_seguridad.return_value = 10

        resultado = self.servicio.verificar_y_reservar("MAT-ACERO-01", 10)

        self.assertTrue(resultado)
        self.mock_repo.descontar_stock.assert_called_once_with("MAT-ACERO-01", 10)

if __name__ == '__main__':
    unittest.main()
