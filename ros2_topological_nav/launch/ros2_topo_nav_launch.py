from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
import ament_index_python


def generate_launch_description():

    pkg_name = 'ros2_topological_nav'
    stdout_linebuf_envvar = SetEnvironmentVariable(
        'RCUTILS_CONSOLE_STDOUT_LINE_BUFFERED', '1')

    #
    # ARGS
    #

    points = LaunchConfiguration('points')
    declare_points_cmd = DeclareLaunchArgument(
        'points',
        default_value=ament_index_python.get_package_share_directory(
            pkg_name) + '/params/apartamento_leon.yaml',
        description='YAML points file')

    nav_action = LaunchConfiguration('nav_action')
    declare_nav_action_cmd = DeclareLaunchArgument(
        'nav_action',
        default_value='/navigate_to_pose',
        description='Navigation2 action server name')

    #
    # NODES
    #

    topo_nav_node_cmd = Node(
        package=pkg_name,
        executable='topo_nav_node',
        name='topo_nav_node',
        namespace="topo_nav/",
        parameters=[points,
                    {'nav_action': nav_action}]

    )

    ld = LaunchDescription()

    ld.add_action(stdout_linebuf_envvar)

    ld.add_action(declare_points_cmd)
    ld.add_action(declare_nav_action_cmd)

    ld.add_action(topo_nav_node_cmd)

    return ld
