from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments=[ "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "tcp", "ftsensor"])

    ft_node = Node(
        package='aidin_aft',
        executable='aft20d15_server',
        name='aft20d15_node',
        output='screen')

    return LaunchDescription([static_tf, ft_node])