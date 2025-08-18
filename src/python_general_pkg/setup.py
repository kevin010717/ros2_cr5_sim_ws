from setuptools import find_packages, setup
from glob import glob

package_name = 'python_general_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='lyx',
    maintainer_email='1712306800@qq.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        'simple_node = python_general_pkg.simple_node:main',
        'simple_publisher_node = python_general_pkg.simple_publisher_node:main',
        'simple_subscriber_node = python_general_pkg.simple_subscriber_node:main',
        'simple_server_node = python_general_pkg.simple_server_node:main',
        'simple_client_node = python_general_pkg.simple_client_node:main',
        ],
    },
)
