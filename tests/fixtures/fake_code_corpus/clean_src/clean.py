from abc import ABC, abstractmethod
from typing import Protocol


class OrderGateway(ABC):
    @abstractmethod
    def save(self, order):
        ...


class Notifier(Protocol):
    def notify(self, order_id: int) -> None:
        ...


def plugin_hook(payload):
    pass  # hs-allow: 插件 SPI 桩，由宿主注入实现


def parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def fallback(order_id):
    try:
        risky(order_id)
    except NotImplementedError:
        pass


# 业务文案含「未实现」字样（如「未实现清单」）不应触发占位规则
NOT_IMPLEMENTED_LIST_LABEL = "未实现清单已显式报告用户"


def risky(order_id):
    return int(order_id)
