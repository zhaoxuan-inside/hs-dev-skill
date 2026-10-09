import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))
from order_service import order_create, order_create_compensate, order_create_fallback


class TestOrderService(unittest.TestCase):
    def setUp(self):
        self.context = {"trace_id": "trace_12345"}
        self.isolate = {"tenant_id": "tenant_default"}
        self.metrics = {}

    def test_order_create_success(self):
        in_data = {
            "order.user_id": "usr_100",
            "order.item_id": "item_200",
            "order.amount": 99.5
        }
        out_data = {}
        exc = order_create(in_data, out_data, self.context, self.isolate, self.metrics)

        self.assertIsNone(exc)
        self.assertIn("order.id", out_data)
        self.assertEqual(out_data["order.status"], "CREATED")
        self.assertEqual(self.metrics["order_create.success_count"], 1)

    def test_order_create_timeout_and_compensate(self):
        in_data = {
            "order.user_id": "usr_100",
            "order.item_id": "item_timeout",
            "order.amount": 99.5
        }
        out_data = {}
        exc = order_create(in_data, out_data, self.context, self.isolate, self.metrics)

        self.assertIsNotNone(exc)
        self.assertEqual(exc["code"], "ORDER_STOCK_LOCK_TIMEOUT")
        self.assertTrue(exc["retryable"])

        # 触发补偿
        comp_out = {}
        comp_exc = order_create_compensate(in_data, comp_out, self.context, self.isolate, self.metrics)
        self.assertIsNone(comp_exc)
        self.assertEqual(comp_out["order.compensate_status"], "STOCK_UNLOCKED")

    def test_order_create_fallback(self):
        in_data = {"order.user_id": "usr_100"}
        out_data = {}
        exc = order_create_fallback(in_data, out_data, self.context, self.isolate, self.metrics)
        self.assertIsNone(exc)
        self.assertEqual(out_data["order.status"], "QUEUING")


if __name__ == "__main__":
    unittest.main()
