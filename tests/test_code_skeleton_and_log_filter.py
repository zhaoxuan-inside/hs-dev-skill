import os
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from code_skeleton import CodeSkeletonExtractor
from log_filter import LogFilter


class TestCodeSkeletonAndLogFilter(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_python_ast_skeleton_extraction(self):
        py_code = '''"""Sample Module Docstring."""

GLOBAL_FLAG = True
MAX_RETRIES = 5

class OrderProcessor(BaseProcessor):
    """Processes online orders."""
    order_id: str

    def __init__(self, order_id: str):
        self.order_id = order_id
        # detailed private setup
        x = 100
        y = 200

    async def execute_payment(self, amount: float, currency: str = "USD") -> bool:
        """Executes payment gateway call."""
        if amount <= 0:
            return False
        return True

def standalone_helper(data: dict) -> str:
    return str(data)
'''
        test_file = self.root / "sample_service.py"
        test_file.write_text(py_code, encoding="utf-8")

        extractor = CodeSkeletonExtractor()
        res = extractor.extract_file(test_file)

        self.assertIn("Sample Module Docstring", res["skeleton"])
        self.assertIn("class OrderProcessor", res["skeleton"])
        self.assertIn("def __init__(self, order_id: str): ...", res["skeleton"])
        self.assertIn("async def execute_payment(self, amount: float, currency: str) -> bool: ...", res["skeleton"])
        self.assertIn("def standalone_helper(data: dict) -> str: ...", res["skeleton"])
        self.assertIn("MAX_RETRIES = ...", res["skeleton"])
        # Check compression ratio is high
        self.assertGreater(res["total_lines"], res["skeleton_lines"])

    def test_log_filter_success_and_failure(self):
        lf = LogFilter(max_error_lines=10)

        # Successful long test output
        long_pass = "setup...\n" * 50 + "Ran 50 tests in 1.2s\n\nOK\n"
        pass_res = lf.filter_text(long_pass, returncode=0)
        self.assertIn("[FILTERED PASS]", pass_res)
        self.assertIn("Ran 50 tests in 1.2s", pass_res)

        # Failure output
        fail_text = "start\nFAIL: test_something\nAssertionError: False != True\n=== summary ===\nFAILED (failures=1)\n"
        fail_res = lf.filter_text(fail_text, returncode=1)
        self.assertIn("FAIL: test_something", fail_res)
        self.assertIn("AssertionError", fail_res)

    def test_multilang_skeleton_and_deps(self):
        extractor = CodeSkeletonExtractor()

        # 1. Dart / Flutter
        dart_code = """
import 'package:flutter/material.dart';

class OrderScreen extends StatelessWidget {
  final String orderId;
  OrderScreen({required this.orderId});

  @override
  Widget build(BuildContext context) {
    OrderService.fetchDetail(orderId);
    return Scaffold(body: Center(child: Text(orderId)));
  }
}
"""
        dart_file = self.root / "order_screen.dart"
        dart_file.write_text(dart_code, encoding="utf-8")
        dart_res = extractor.extract_file(dart_file)
        self.assertIn("class OrderScreen", dart_res["skeleton"])
        self.assertIn("Widget build", dart_res["skeleton"])

        dart_symbols = extractor.extract_symbols_metadata(dart_file)
        symbol_names = [s["name"] for s in dart_symbols]
        self.assertIn("OrderScreen", symbol_names)
        self.assertIn("build", symbol_names)

        dart_deps = extractor.extract_dependencies(dart_file)
        dep_targets = [d["target_symbol"] for d in dart_deps]
        self.assertIn("package:flutter/material.dart", dep_targets)
        self.assertIn("OrderService.fetchDetail", dep_targets)

        # 2. Java
        java_code = """
package com.demo.order;
import com.demo.payment.PaymentService;

public class OrderController {
    public ResponseEntity<String> createOrder(OrderDTO dto) {
        PaymentService.processPayment(dto);
        return ok("created");
    }
}
"""
        java_file = self.root / "OrderController.java"
        java_file.write_text(java_code, encoding="utf-8")
        java_res = extractor.extract_file(java_file)
        self.assertIn("public class OrderController", java_res["skeleton"])
        java_deps = extractor.extract_dependencies(java_file)
        java_targets = [d["target_symbol"] for d in java_deps]
        self.assertIn("com.demo.payment.PaymentService", java_targets)
        self.assertIn("PaymentService.processPayment", java_targets)


if __name__ == "__main__":
    unittest.main()

