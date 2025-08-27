#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import math
import threading
import select
import tty
import termios
import random
from contextlib import contextmanager

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


@contextmanager
def raw_nonblocking_stdin():
    """
    将 stdin 设为原始模式（cbreak），便于非阻塞单字符读取。
    若非 TTY 或设置失败，抛出异常交由调用方处理。
    """
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)   # 不回显、无需回车即可读取
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


class KeyboardReader(threading.Thread):
    """
    在独立线程里轮询 stdin，捕获单字符并回调 on_key。
    仅当 stdin 是 TTY 时才会启用。
    """
    def __init__(self, on_key, poll_hz: float = 100.0):
        super().__init__(daemon=True)
        self.on_key = on_key
        self._stop = threading.Event()
        self._period = 1.0 / float(poll_hz)

    def stop(self):
        self._stop.set()

    def run(self):
        if not sys.stdin.isatty():
            return
        try:
            with raw_nonblocking_stdin():
                while not self._stop.is_set():
                    rlist, _, _ = select.select([sys.stdin], [], [], self._period)
                    if rlist:
                        ch = sys.stdin.read(1)
                        if ch:
                            try:
                                self.on_key(ch)
                            except Exception as e:
                                # 不让输入线程因为回调异常而崩
                                print(f"[KeyboardReader] on_key error: {e}", flush=True)
        except Exception:
            # 非 TTY 或终端控制异常，静默退出
            return


class KeyboardJointStatePublisher(Node):
    """
    通过键盘控制 6 关节的 position，并周期发布 /joint_states。
    - 数字 1..6 选择关节
    - j / k   当前关节 -step / +step
    - [ / ]   减小/增大步长
    - r       重置所有关节为 0
    - z       随机化位置于 [-1, 1]
    - p       暂停/恢复发布
    - h/?     显示帮助
    - q       退出
    """
    def __init__(self):
        super().__init__('keyboard_joint_state_publisher')

        # 发布器与参数
        self.pub = self.create_publisher(JointState, '/joint_states', 10)
        self.joint_names = [f'joint{i}' for i in range(1, 7)]
        self.position = [0.0] * 6
        self.velocity = [0.0] * 6
        self.effort   = [0.0] * 6

        self.selected = 0
        self.step = 0.05               # 每次按键的步长（rad）
        self.position_limit = math.pi  # 位置限幅（±π，可按需调整）
        self.publish_enabled = True

        self._lock = threading.Lock()

        # 10 Hz 发布（和你原来的假发布器一致）
        self.timer = self.create_timer(0.1, self._on_timer)

        # 启动键盘线程（仅当 stdin 是 TTY）
        self.kb = None
        if sys.stdin.isatty():
            self.kb = KeyboardReader(self._on_key, poll_hz=120.0)
            self.kb.start()
            self._print_help()
            self.get_logger().info("Keyboard control ENABLED (TTY detected).")
        else:
            self.get_logger().warning(
                "未检测到可交互终端（stdin 非 TTY）。键盘控制禁用。\n"
                "请在真实终端中通过 `ros2 run` 运行，或在 launch 文件里为节点设置 emulate_tty=True。"
            )

        self.get_logger().info("Keyboard JointState publisher started.")

    # ----------------- 回调与工具 -----------------

    @staticmethod
    def _clamp(x, lo, hi):
        return max(lo, min(hi, x))

    def _on_timer(self):
        if not self.publish_enabled:
            return
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        with self._lock:
            msg.position = list(self.position)
            msg.velocity = list(self.velocity)
            msg.effort   = list(self.effort)
        self.pub.publish(msg)

    def _on_key(self, ch: str):
        # 退出
        if ch == 'q':
            self.get_logger().info("Quit requested (q). Shutting down rclpy...")
            # 触发 rclpy.spin() 退出；清理在 main() 的 finally 里做
            rclpy.shutdown()
            return

        # 选择关节 1..6
        if ch in '123456':
            self.selected = ord(ch) - ord('1')
            self.get_logger().info(f"Selected joint: {self.selected + 1}")
            self._print_status()
            return

        # 减少/增加当前关节位置
        if ch == 'j':
            with self._lock:
                self.position[self.selected] = self._clamp(
                    self.position[self.selected] - self.step,
                    -self.position_limit, self.position_limit
                )
            self._print_status()
            return
        if ch == 'k':
            with self._lock:
                self.position[self.selected] = self._clamp(
                    self.position[self.selected] + self.step,
                    -self.position_limit, self.position_limit
                )
            self._print_status()
            return

        # 调整步长
        if ch == '[':
            self.step = max(1e-3, self.step / 1.5)
            self.get_logger().info(f"Step: {self.step:.5f} rad")
            self._print_status()
            return
        if ch == ']':
            self.step = min(1.0, self.step * 1.5)
            self.get_logger().info(f"Step: {self.step:.5f} rad")
            self._print_status()
            return

        # 重置/随机化
        if ch == 'r':
            with self._lock:
                self.position = [0.0] * 6
            self.get_logger().info("Reset all joints to 0.0")
            self._print_status()
            return
        if ch == 'z':
            with self._lock:
                self.position = [random.uniform(-1.0, 1.0) for _ in range(6)]
            self.get_logger().info("Randomized joint positions in [-1, 1]")
            self._print_status()
            return

        # 暂停/恢复发布
        if ch == 'p':
            self.publish_enabled = not self.publish_enabled
            self.get_logger().info(f"Publish: {'ON' if self.publish_enabled else 'OFF'}")
            return

        # 帮助
        if ch in ('h', '?'):
            self._print_help()
            return

    def _print_status(self):
        with self._lock:
            pos = ", ".join(f"{p:+.3f}" for p in self.position)
        print(
            f"[joint {self.selected+1}] step={self.step:.5f} rad | "
            f"pos=[{pos}]",
            flush=True
        )

    def _print_help(self):
        help_text = (
            "\n=== Keyboard JointState Teleop ===\n"
            "[1..6]  选择关节\n"
            "j / k   当前关节 -step / +step（默认 0.05 rad）\n"
            "[ / ]   减小/增大步长\n"
            "r       重置为 0\n"
            "z       随机化位置 [-1, 1]\n"
            "p       暂停/恢复发布\n"
            "h/?     显示帮助\n"
            "q       退出\n"
            "----------------------------------\n"
            f"当前：joint={self.selected+1}, step={self.step:.5f} rad\n"
        )
        print(help_text, flush=True)

    # ----------------- 生命周期 -----------------

    def destroy_node(self):
        try:
            if self.kb is not None:
                self.kb.stop()
                self.kb.join(timeout=1.0)
        except Exception:
            pass
        return super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = KeyboardJointStatePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        # 若先按 q，会先触发 shutdown；这里再次调用也安全
        try:
            rclpy.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()
