"""
order_service.py
六元组标准实现：订单创建、Saga补偿与降级
Signature: exception method_name(input, output, context, isolate, metrics, recall)
"""

import time
from typing import Optional, Dict, Any


class SixTupleException(Exception):
    def __init__(self, code: str, msg: str, retryable: bool = False, details: Optional[Dict[str, Any]] = None):
        self.code = code
        self.msg = msg
        self.retryable = retryable
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "msg": self.msg,
            "retryable": self.retryable,
            "details": self.details,
        }


def order_create(
    input_data: Dict[str, Any],
    output_data: Dict[str, Any],
    context: Dict[str, Any],
    isolate: Dict[str, Any],
    metrics: Dict[str, Any],
    recall: Any = None
) -> Optional[Dict[str, Any]]:
    """
    1. 业务主方法: order_create
    功能: 校验参数、调用库存锁定 RPC、落库订单
    """
    start_time = time.time()
    user_id = input_data.get("order.user_id")
    item_id = input_data.get("order.item_id")
    amount = input_data.get("order.amount")

    try:
        # 参数校验
        if not user_id or not item_id or amount is None:
            return SixTupleException("INVALID_ORDER_PARAMS", "下单参数不完整", retryable=False).to_dict()

        if amount <= 0:
            return SixTupleException("INVALID_ORDER_AMOUNT", "下单金额必须大于0", retryable=False).to_dict()

        # 模拟调用库存服务
        if item_id == "item_timeout":
            # 模拟超时触发
            raise TimeoutError("Stock lock RPC timed out after 3000ms")

        # 业务成功，填充 output
        output_data["order.id"] = f"ord_{int(time.time()*1000)}"
        output_data["order.status"] = "CREATED"

        metrics["order_create.success_count"] = metrics.get("order_create.success_count", 0) + 1
        return None

    except TimeoutError as te:
        metrics["order_create.timeout_count"] = metrics.get("order_create.timeout_count", 0) + 1
        exc = SixTupleException(
            code="ORDER_STOCK_LOCK_TIMEOUT",
            msg=str(te),
            retryable=True,
            details={"item_id": item_id, "user_id": user_id}
        ).to_dict()
        context["last_exception"] = exc
        return exc
    finally:
        metrics["order_create.duration_ms"] = (time.time() - start_time) * 1000


def order_create_compensate(
    input_data: Dict[str, Any],
    output_data: Dict[str, Any],
    context: Dict[str, Any],
    isolate: Dict[str, Any],
    metrics: Dict[str, Any],
    recall: Any = None
) -> Optional[Dict[str, Any]]:
    """
    2. 事务补偿方法: order_create_compensate
    功能: 释放锁定的库存、回滚中间状态
    """
    last_exc = context.get("last_exception")
    item_id = input_data.get("order.item_id")
    # 执行释放库存逻辑
    metrics["order_create.compensate_count"] = metrics.get("order_create.compensate_count", 0) + 1
    output_data["order.compensate_status"] = "STOCK_UNLOCKED"
    return None


def order_create_fallback(
    input_data: Dict[str, Any],
    output_data: Dict[str, Any],
    context: Dict[str, Any],
    isolate: Dict[str, Any],
    metrics: Dict[str, Any],
    recall: Any = None
) -> Optional[Dict[str, Any]]:
    """
    3. 异常降级方法: order_create_fallback
    功能: 熔断/降级时返回排队中状态
    """
    metrics["order_create.fallback_count"] = metrics.get("order_create.fallback_count", 0) + 1
    output_data["order.status"] = "QUEUING"
    output_data["order.notice"] = "系统繁忙，订单已进入排队队列"
    return None
