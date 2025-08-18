import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class SimpleServerNode(Node):
    def __init__(self, node_name):
        super().__init__(node_name)
        self._service = self.create_service(
            AddTwoInts, 
            "/python_simple_service", 
            self._callback, 
            )
        self.get_logger().info(f"服务节点 {node_name} 已启动!")

    def _callback(self, request, response):
        a = request.a
        b = request.b
        response.sum = a + b

        self.get_logger().info(f"收到请求: a={request.a}, b={request.b}")
        self.get_logger().info(f"返回响应: sum={response.sum}")
        return response


def main():
    rclpy.init()
    node = SimpleServerNode("python_simple_server")
    rclpy.spin(node)
    rclpy.shutdown()
