from setuptools import find_packages, setup
from glob import glob

package_name = 'python_general_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test', 'tests']),
    data_files=[
        # 这些路径必须是相对路径！
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        # 如果后续要安装 config/urdf 等，也保持相对路径写法：
        # ('share/' + package_name + '/config', glob('config/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='lyx',
    maintainer_email='1712306800@qq.com',
    description='General python nodes for ROS 2 demos',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'simple_node = python_general_pkg.simple_node:main',
            'simple_publisher_node = python_general_pkg.simple_publisher_node:main',
            'simple_subscriber_node = python_general_pkg.simple_subscriber_node:main',
            'simple_server_node = python_general_pkg.simple_server_node:main',
            'simple_client_node = python_general_pkg.simple_client_node:main',
            'keyboard_joint_state_publisher = python_general_pkg.keyboard_joint_state_publisher:main',
        ],
    },
)
