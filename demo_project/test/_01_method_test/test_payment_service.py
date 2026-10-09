import unittest
import sys
from pathlib import Path

# 引入 backend 服务
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))
from payment_service import payment_process, payment_process_compensate, payment_process_fallback


class TestPaymentService(unittest.TestCase):
    def setUp(self):
        self.context = {"trace_id": "trace_pay_999"}
        self.isolate = {"tenant_id": "tenant_100"}
        self.metrics = {}

    def test_payment_success(self):
        in_data = {"payment.order_id": "ord_1001", "payment.amount": 88.0, "payment.channel": "ALIPAY"}
        out_data = {}
        exc = payment_process(in_data, out_data, self.context, self.isolate, self.metrics)

        self.assertIsNone(exc)
        self.assertEqual(out_data["payment.status"], "SUCCESS")
        self.assertIn("payment.id", out_data)
        self.assertEqual(self.metrics["payment_process.success_count"], 1)

    def test_payment_timeout_and_compensation(self):
        in_data = {"payment.order_id": "ord_1002", "payment.amount": 88.0, "payment.channel": "TIMEOUT_CHANNEL"}
        out_data = {}
        exc = payment_process(in_data, out_data, self.context, self.isolate, self.metrics)

        self.assertIsNotNone(exc)
        self.assertEqual(exc["code"], "PAYMENT_GATEWAY_TIMEOUT")
        self.assertTrue(exc["retryable"])

        # 触发事务补偿
        comp_out = {}
        comp_exc = payment_process_compensate(in_data, comp_out, self.context, self.isolate, self.metrics)
        self.assertIsNone(comp_exc)
        self.assertEqual(comp_out["payment.status"], "COMPENSATED_FAILED")
        self.assertTrue(comp_out["payment.funds_released"])

    def test_payment_fallback(self):
        in_data = {"payment.order_id": "ord_1003", "payment.amount": 88.0}
        out_data = {}
        exc = payment_process_fallback(in_data, out_data, self.context, self.isolate, self.metrics)
        self.assertIsNone(exc)
        self.assertEqual(out_data["payment.status"], "QUEUED_FOR_RECONCILIATION")


if __name__ == "__main__":
    unittest.main()
