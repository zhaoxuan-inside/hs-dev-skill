"""
payment_service.py
demo_project 支付领域六元组服务实现
Signature: exception payment_process(input, output, context, isolate, metrics, recall)
"""

import time
from typing import Optional, Dict, Any


def payment_process(
    input_data: Dict[str, Any],
    output_data: Dict[str, Any],
    context: Dict[str, Any],
    isolate: Dict[str, Any],
    metrics: Dict[str, Any],
    recall: Any = None
) -> Optional[Dict[str, Any]]:
    """
    1. 业务主方法: payment_process
    功能: 校验参数、扣减账户、调用支付网关
    """
    start_time = time.time()
    order_id = input_data.get("payment.order_id")
    amount = input_data.get("payment.amount")
    channel = input_data.get("payment.channel", "ALIPAY")

    try:
        # 参数校验
        if not order_id or amount is None:
            return {
                "code": "INVALID_PARAMS",
                "msg": "订单号与金额必填",
                "retryable": False,
                "details": {}
            }

        if amount <= 0:
            return {
                "code": "INVALID_AMOUNT",
                "msg": "支付金额必须大于0",
                "retryable": False,
                "details": {"amount": amount}
            }

        # 模拟渠道网关超时场景
        if channel == "TIMEOUT_CHANNEL":
            raise TimeoutError("Payment gateway response timeout")

        # 成功完成支付
        output_data["payment.id"] = f"pay_{int(time.time()*1000)}"
        output_data["payment.status"] = "SUCCESS"
        metrics["payment_process.success_count"] = metrics.get("payment_process.success_count", 0) + 1
        return None

    except TimeoutError as te:
        metrics["payment_process.timeout_count"] = metrics.get("payment_process.timeout_count", 0) + 1
        exc = {
            "code": "PAYMENT_GATEWAY_TIMEOUT",
            "msg": str(te),
            "retryable": True,
            "details": {"order_id": order_id, "amount": amount}
        }
        context["last_exception"] = exc
        return exc
    finally:
        metrics["payment_process.duration_ms"] = (time.time() - start_time) * 1000


def payment_process_compensate(
    input_data: Dict[str, Any],
    output_data: Dict[str, Any],
    context: Dict[str, Any],
    isolate: Dict[str, Any],
    metrics: Dict[str, Any],
    recall: Any = None
) -> Optional[Dict[str, Any]]:
    """
    2. 事务补偿方法: payment_process_compensate
    功能: 解冻预占资金，标记流水失败
    """
    metrics["payment_process.compensate_count"] = metrics.get("payment_process.compensate_count", 0) + 1
    output_data["payment.status"] = "COMPENSATED_FAILED"
    output_data["payment.funds_released"] = True
    return None


def payment_process_fallback(
    input_data: Dict[str, Any],
    output_data: Dict[str, Any],
    context: Dict[str, Any],
    isolate: Dict[str, Any],
    metrics: Dict[str, Any],
    recall: Any = None
) -> Optional[Dict[str, Any]]:
    """
    3. 异常降级方法: payment_process_fallback
    功能: 熔断时入队异步对账轮询
    """
    metrics["payment_process.fallback_count"] = metrics.get("payment_process.fallback_count", 0) + 1
    output_data["payment.status"] = "QUEUED_FOR_RECONCILIATION"
    return None
