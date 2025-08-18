import time
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class SimpleClientNode(Node):
    def __init__(self, node_name):
        super().__init__(node_name)
        self._client = self.create_client(AddTwoInts, "/python_simple_service")

        while not self._client.wait_for_service(timeout_sec=1.5):
            self.get_logger().warn("服务未就绪，请稍等...")

    def call_service(self, a, b):
        request = AddTwoInts.Request()
        request.a = a
        request.b = b

        future = self._client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        self.get_logger().info(f"发出请求: a={a}, b={b}")

        if future.result() is not None:
            self.get_logger().info(f"收到响应: sum={future.result().sum}")
        else:
            self.get_logger().error("请求失败!")


def main():
    rclpy.init()
    node = SimpleClientNode("python_simple_client")
    a = 0
    b = 1
    while True:
        node.call_service(a, b)
        a += 1
        b += 3
        time.sleep(1)
        if a > 10:
            break
    rclpy.spin(node)
    rclpy.shutdown()
