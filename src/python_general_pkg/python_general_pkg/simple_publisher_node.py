#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math
import time
import random

class FakeJointStatePublisher(Node):
    def __init__(self):
        super().__init__('fake_joint_state_publisher')

        # 创建发布器
        self.publisher_ = self.create_publisher(JointState, '/joint_states', 10)

        # 设置发布周期（10Hz）
        timer_period = 0.1
        self.timer = self.create_timer(timer_period, self.timer_callback)

        # 定义 6 关节的名称
        self.joint_names = [
            'joint1',
            'joint2',
            'joint3',
            'joint4',
            'joint5',
            'joint6'
        ]
        self.start_time = self.get_clock().now()

        self.get_logger().info("Fake joint state publisher started for 6-DOF arm.")

    def timer_callback(self):
        # 计算当前时间
        now = self.get_clock().now()
        elapsed = (now - self.start_time).nanoseconds / 1e9

        # 创建 JointState 消息
        joint_state = JointState()
        joint_state.header.stamp = now.to_msg()
        joint_state.name = self.joint_names

        # 模拟关节数据：使用正弦函数变化
        # joint_state.position = [math.sin(elapsed + i) for i in range(6)]
        joint_state.position = [random.uniform(-1.57, 1.57) for _ in range(6)]
        joint_state.velocity = [math.cos(elapsed + i) for i in range(6)]
        joint_state.effort = [0.5 * math.sin(elapsed + i) for i in range(6)]

        # 发布
        self.publisher_.publish(joint_state)
        # self.get_logger().info(f"Published joint states: {joint_state.position}")

def main(args=None):
    rclpy.init(args=args)
    node = FakeJointStatePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
