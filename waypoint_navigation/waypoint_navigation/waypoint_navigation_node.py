
""" Waypoint Navigation """

from typing import List
import rclpy

from geometry_msgs.msg import Pose
from nav2_msgs.action import NavigateToPose
from waypoint_navigation_msgs.action import NavigateToWp
from waypoint_navigation_msgs.msg import Wp
from waypoint_navigation_msgs.srv import (
    AddWp,
    GetWp,
    GetWps
)

from simple_node import Node


class WaypointNavigationNode(Node):
    """ Waypoint Navigation Node """

    def __init__(self) -> None:
        super().__init__("waypoint_navigation_node")

        self.__wp_dict = {}

        # param names
        nav_action_param_name = "nav_action"
        wps_param_name = "wps"

        # declaring params
        self.declare_parameter(nav_action_param_name,
                               "/navigate_to_pose")
        self.declare_parameter(wps_param_name, None)

        # getting params
        nav_action = self.get_parameter(
            nav_action_param_name).get_parameter_value().string_value
        waypoints = self.get_parameter(
            wps_param_name).get_parameter_value().string_array_value

        # load points
        self.load_wps(waypoints)

        # actions
        self.__action_client = self.create_action_client(
            NavigateToPose, nav_action)
        self.__action_server = self.create_action_server(
            NavigateToWp,
            "navigate_to_wp",
            execute_callback=self.__execute_server,
            cancel_callback=self.__cancel_callback
        )

        # services
        self.create_service(
            AddWp, "add_wp", self.__add_wp,
            callback_group=self.__action_server.callback_group)

        self.create_service(
            GetWp, "get_wp", self.__get_wp,
            callback_group=self.__action_server.callback_group)

        self.create_service(
            GetWps, "get_wps", self.__get_wps,
            callback_group=self.__action_server.callback_group)

    def load_wps(self, waypoints: List[str]):
        """ load waypoints of list strings into a dictionary of floats

        Args:
            points (List[str]): list of points
        """

        if not waypoints:
            return

        for i in range(0, len(waypoints), 5):

            self.__wp_dict[waypoints[i]] = Pose()
            self.__wp_dict[waypoints[i]].position.x = float(waypoints[i + 1])
            self.__wp_dict[waypoints[i]].position.y = float(waypoints[i + 2])
            self.__wp_dict[waypoints[i]].orientation.z = float(
                waypoints[i + 3])
            self.__wp_dict[waypoints[i]].orientation.w = float(
                waypoints[i + 4])

    def __get_wp(
        self,
        req: GetWp.Request,
        res: GetWp.Response
    ) -> GetWp.Response:
        """ srv callback to get a point

        Args:
            req (GetPoint.Request): request with the point name
            res (GetPoint.Response): point

        Returns:
            GetPoint.Response: point
        """

        if req.wp_id in self.__wp_dict:
            res.wp = Wp()
            res.wp.id = req.wp_id
            res.wp.pose = self.__wp_dict[req.wp_id]

        return res

    def __get_wps(
        self,
        req: GetWps.Request,
        res: GetWps.Response
    ) -> GetWps.Response:
        """ srv callback to get all points

        Args:
            req (GetPoints.Request): empty
            res (GetPoints.Response): points

        Returns:
            GetPoints.Response: points
        """

        for p_id in self.__wp_dict:
            wp = Wp()
            wp.id = p_id
            wp.pose = self.__wp_dict[p_id]
            res.wps.append(wp)

        return res

    def __add_wp(
        self,
        req: AddWp.Request,
        res: AddWp.Response
    ) -> AddWp.Response:
        """ srv callback to add new points

        Args:
            req (AddPoint.Request): request with the point
            res (AddPoint.Response): overwrites an existing point?

        Returns:
            AddPoint.Response: overwrites an existing point?
        """

        wp = req.wp
        overwrite = wp.id in self.__wp_dict
        res.overwrite = overwrite

        if not overwrite:
            self.__wp_dict[wp.id] = {}

        self.__wp_dict[wp.id] = wp.pose

        return res

    def __cancel_callback(self) -> None:
        """ cancel action server """

        self.__action_client.cancel_goal()

    def __execute_server(self, goal_handle) -> NavigateToWp.Result:
        """ execute action server

        Args:
            goal_handle: goal_handle

        Returns:
            NavigateToWp.Result: navigation result
        """

        request = goal_handle.request
        result = NavigateToWp.Result()

        if request.wp_id not in self.__wp_dict:
            goal_handle.abort()
            return result

        pose = self.__wp_dict[request.wp_id]
        goal = NavigateToPose.Goal()
        goal.pose.pose = pose
        goal.pose.header.frame_id = "map"

        self.__action_client.wait_for_server()
        self.__action_client.send_goal(goal)
        self.__action_client.wait_for_result()

        if self.__action_client.is_succeeded():
            goal_handle.succeed()

        elif goal_handle.is_cancel_requested:
            goal_handle.canceled()

        else:
            goal_handle.abort()

        return result


def main():
    rclpy.init()
    node = WaypointNavigationNode()
    node.join_spin()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
