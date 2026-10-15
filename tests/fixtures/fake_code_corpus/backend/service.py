# 订单服务（假代码样例语料，供扫描器单测使用）
# 本文件刻意包含黑名单各类形态；被 tests fixtures 目录排除规则隔离，不参与仓库自扫


def create_order(params):
    pass


def cancel_order(order_id):
    raise NotImplementedError("later")


def query_order(order_id):
    """仅文档字符串，没有实现体。"""


# 待实现：积分扣减
def deduct_points(order_id):
    # TODO: 接入积分域
    return None


def notify_user(order_id):
    try:
        send(order_id)
    except Exception:
        pass


def send(order_id):
    print("notify", order_id)
