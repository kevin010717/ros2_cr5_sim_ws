import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimpleSubscriberNode(Node):
    def __init__(self, node_name):
        super().__init__(node_name)
        self._subscriber = self.create_subscription(
            msg_type = String, 
            topic = "/simple_topic", 
            callback = self._callback,
            qos_profile = 10, 
            )
        self.get_logger().info(f"订阅节点 {node_name} 已启动!")

    def _callback(self, msg):
        self.get_logger().info(f"订阅消息: {msg.data}")


def main():
    rclpy.init()
    node = SimpleSubscriberNode("python_simple_subscriber")
    rclpy.spin(node)
    rclpy.shutdown()
