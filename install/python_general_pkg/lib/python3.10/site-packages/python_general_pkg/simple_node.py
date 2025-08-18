import rclpy
from rclpy.node import Node


def main():
    rclpy.init()
    node = Node("python_simple_node")
    node.get_logger().info("你好, 这是一个最简单的 Python 节点!")
    rclpy.spin(node)
    rclpy.shutdown()
