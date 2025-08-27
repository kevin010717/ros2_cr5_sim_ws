#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import math
import threading
import select
import tty
import termios
from contextlib import contextmanager

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


@contextmanager
def raw_nonblocking_stdin():
    """
    将 stdin 设为原始模式；若非 TTY 或设置失败，则让调用方捕获并降级。
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


class KeyboardReader(threading.Thread):
    def __init__(self, on_key, poll_hz=60.0):
        super().__init__(daemon=True)
        self.on_key = on_key
        self._stop = threading.Event()
        self._period = 1.0 / float(poll_hz)
        self._ctx = None  # 上下文管理器句柄

    def stop(self):
        self._stop.set()

    def run(self):
        # 非 TTY 时直接返回（由主线程打印提示）
        if not sys.stdin.isatty():
            return

        try:
            with raw_nonblocking_stdin():
                while not self._stop.is_set():
                    rlist, _, _ = select.select([sys.stdin], [], [], self._period)
                    if rlist:
                        ch = sys.stdin.read(1)
                        if ch:
                            self.on_key(ch)
        except Exception as e:
            # 非 TTY 或其他终端控制异常时，静默退出，让节点继续运行
            # 也可以打印：print(f"[KeyboardReader] disabled: {e}", flush=True)
            return


class KeyboardJointStatePublisher(Node):
    def __init__(self):
        super().__init__('keyboard_joint_state_publisher')
        self.publisher_ = self.create_publisher(JointState, '/joint_states', 10)

        self.joint_names = [f'joint{i}' for i in range(1, 7)]
        self.position = [0.0] * 6
        self.velocity = [0.0] * 6
        self.effort = [0.0] * 6

        self.selected = 0
        self.step = 0.05
        self.publish_enabled = True
        self.position_limit = math.pi

        self._quit_requested = False

        # 50 Hz 发布
        self.timer = self.create_timer(0.02, self.timer_cb)

        # 键盘线程（仅当 stdin 是 TTY 才启用）
        self.kb = None
        if sys.stdin.isatty():
            self.kb = KeyboardReader(self.on_key, poll_hz=100.0)
            self.kb.start()
            self.print_help()
            self.get_logger().info("Keyboard control ENABLED (TTY detected).")
        else:
            self.get_logger().warn(
                "未检测到可交互终端（stdin 非 TTY）。键盘控制已禁用。"
                "请在真实终端中通过 `ros2 run` 运行，或用 `launch` 时为节点分配伪终端（见下文说明）。"
            )

    def destroy_node(self):
        try:
            if self.kb is not None:
                self.kb.stop()
                self.kb.join(timeout=1.0)
        except Exception:
            pass
        return super().destroy_node()

    @staticmethod
    def clamp(x, lo, hi):
        return max(lo, min(hi, x))

    def on_key(self, ch: str):
        if ch == 'q':
            self.get_logger().info("Quit requested (q).")
            self._quit_requested = True
            # 在主线程中安全关闭
            self.executor.create_task(self._shutdown_soon())
            return

        if ch in '123456':
            self.selected = ord(ch) - ord('1')
            self.get_logger().info(f"Selected joint: {self.selected + 1}")
            return

        if ch == 'j':
            self.position[self.selected] = self.clamp(
                self.position[self.selected] - self.step, -self.position_limit, self.position_limit
            )
            return
        if ch == 'k':
            self.position[self.selected] = self.clamp(
                self.position[self.selected] + self.step, -self.position_limit, self.position_limit
            )
            return

        if ch == '[':
            self.step = max(0.001, self.step / 1.5)
            self.get_logger().info(f"Step: {self.step:.5f} rad")
            return
        if ch == ']':
            self.step = min(1.0, self.step * 1.5)
            self.get_logger().info(f"Step: {self.step:.5f} rad")
            return

        if ch == 'r':
            self.position = [0.0] * 6
            self.get_logger().info("Reset all joints to 0.0")
            return
        if ch == 'z':
            import random
            self.position = [random.uniform(-1.0, 1.0) for _ in range(6)]
            self.get_logger().info("Randomized joint positions in [-1, 1]")
            return

        if ch == 'p':
            self.publish_enabled = not self.publish_enabled
            self.get_logger().info(f"Publish: {'ON' if self.publish_enabled else 'OFF'}")
            return

        if ch in ('h', '?'):
            self.print_help()
            return

    async def _shutdown_soon(self):
        # 给发布周期一个机会 flush
        await rclpy.task.Future(asyncio=True).sleep(0.05)  # 小延时，非严格必要
        try:
            self.destroy_node()
        finally:
            try:
                rclpy.shutdown()
            except Exception:
                pass

    def timer_cb(self):
        if not self.publish_enabled:
            return
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = list(self.position)
        msg.velocity = list(self.velocity)
        msg.effort = list(self.effort)
        self.publisher_.publish(msg)

    def print_help(self):
        help_text = (
            "\n=== Keyboard JointState Teleop ===\n"
            "[1..6]  选择关节\n"
            "j / k   当前关节 -step / +step（默认 0.05 rad）\n"
            "[ / ]   减小/增大步长\n"
            "r       重置为 0\n"
            "z       随机化位置\n"
            "p       暂停/恢复发布\n"
            "h/?     显示帮助\n"
            "q       退出\n"
            "----------------------------------\n"
            f"当前：joint={self.selected+1}, step={self.step:.5f} rad\n"
        )
        print(help_text, flush=True)


def main(args=None):
    rclpy.init(args=args)
    node = KeyboardJointStatePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        try:
            rclpy.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()
