#!/usr/bin/env python3
import rclpy
from builtin_interfaces.msg import Duration
from control_msgs.action import FollowJointTrajectory
from rclpy.action import ActionClient
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectoryPoint

JOINTS = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
          'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']

class JointClient(Node):
    def __init__(self):
        super().__init__('UR_action_client')
        self._action_client = ActionClient(self, FollowJointTrajectory, 'move_robot')

    def send_goal(self, positions, seconds):
        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = JOINTS
        goal.trajectory.points = [JointTrajectoryPoint(
            positions=positions, time_from_start=Duration(sec=seconds))]
        self._action_client.wait_for_server()
        future = self._action_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        result = future.result().get_result_async()
        rclpy.spin_until_future_complete(self, result)

def main():
    rclpy.init()
    JointClient().send_goal([-3.14, -1.0, 1.0, -1.57, -1.57, 0.0], 3)

if __name__ == '__main__':
    main()