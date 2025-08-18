import launch
import launch_ros


def generate_launch_description():
    simple_subscriber_node = launch_ros.actions.Node(
        package="python_general_pkg",
        executable="simple_subscriber_node",
        output="screen",
    )
    simple_server_node = launch_ros.actions.Node(
        package="python_general_pkg",
        executable="simple_server_node",
        output="screen",
    )
    launch_description = launch.LaunchDescription(
        [
            simple_subscriber_node,
            simple_server_node,
        ],
    )
    return launch_description
