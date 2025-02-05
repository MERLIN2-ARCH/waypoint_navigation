from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
import ament_index_python


def generate_launch_description():

    pkg_name = "waypoint_navigation"
    stdout_linebuf_envvar = SetEnvironmentVariable(
        "RCUTILS_CONSOLE_STDOUT_LINE_BUFFERED", "1"
    )

    #
    # ARGS
    #
    points = LaunchConfiguration("wps")
    declare_points_cmd = DeclareLaunchArgument(
        "wps",
        default_value=ament_index_python.get_package_share_directory(pkg_name)
        + "/params/apartamento_leon.yaml",
        description="YAML waypoints file",
    )

    nav_action = LaunchConfiguration("nav_action")
    declare_nav_action_cmd = DeclareLaunchArgument(
        "nav_action",
        default_value="/navigate_to_pose",
        description="Navigation2 action server name",
    )

    #
    # NODES
    #
    waypoint_navigation_node_cmd = Node(
        package=pkg_name,
        executable="waypoint_navigation_node",
        name="waypoint_navigation_node",
        namespace="waypoint_navigation/",
        parameters=[points, {"nav_action": nav_action}],
    )

    ld = LaunchDescription()

    ld.add_action(stdout_linebuf_envvar)

    ld.add_action(declare_points_cmd)
    ld.add_action(declare_nav_action_cmd)

    ld.add_action(waypoint_navigation_node_cmd)

    return ld
