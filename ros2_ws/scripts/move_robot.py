#!/usr/bin/env python3
"""Same as:
    ros2 run lucy_motion move_joints left_shoulder_pitch=-1.0 left_elbow=-1.2 head_yaw=0.8 --duration 2

Needs the simulator and joint_server running. Run with:
    source /opt/ros/jazzy/setup.bash
    source ~/unitree_mujoco/example/ros2_lucy/install/setup.bash
    python3 move_robot.py
"""
import rclpy
import time
from rclpy.node import Node
import xml.etree.ElementTree as ET
from control_msgs.action import FollowJointTrajectory
from sensor_msgs.msg import JointState
from lucy_motion.move_joints import LucyMotionClient
from lucy_motion.lucy_model import find_model_xml

class JointStateListener(Node):
    def __init__(self):
        super().__init__("joint_state_listener")
        self.joint_states = None
        self.robot = self.declare_parameter("robot", "lucy_gibbon").value
        self.root = ET.parse(find_model_xml(self.robot)).getroot()
        self.create_subscription(JointState, "/joint_states", self.get_current_joint_states, 10)
    def get_current_joint_states(self, msg: JointState):
        self.joint_states = dict(zip(msg.name, msg.position))
    def get_joint_limits(self, name):
        for joint in self.root.iter("joint"):
            if joint.get("name") == name:
                lower, upper = (float(v) for v in joint.get("range").split())
                return lower, upper

def main():
    rclpy.init()
    node = JointStateListener()
    client = LucyMotionClient()
    try:
        while node.joint_states is None:
            rclpy.spin_once(node, timeout_sec=0.1)
        default_pose = {}
        for name, pos in node.joint_states.items():
            lower, upper = node.get_joint_limits(name)
            default_pose[name] = min(max(pos, lower), upper)
        time.sleep(2)
        result = client.move(
            {
                # legs: thighs forward under the body, knees bent, feet flat
                "left_hip_pitch": -1.2, "right_hip_pitch": -1.2,
                "left_leg_knee": 0.8, "right_leg_knee": 0.8,
                "left_ankle_pitch": -0.5, "right_ankle_pitch": -0.5,
                "left_hip_roll": 0.1, "right_hip_roll": -0.1,          # feet slightly apart
                # arms: reaching down to the ground, almost straight
                "left_shoulder_pitch": -1.0, "right_shoulder_pitch": -1.0,
                "left_elbow": -0.2, "right_elbow": -0.2,
                "left_shoulder_roll": 0.15, "right_shoulder_roll": -0.15,  # hands slightly apart
                # head: look forward instead of at the ground
                "head_pitch": -0.6,
            }
        )
        if result.error_code == FollowJointTrajectory.Result.SUCCESSFUL:
            print("SUCCESSFUL")
        else:
            print(f"failed (error_code {result.error_code}): {result.error_string}")
        time.sleep(10)
        result = client.move(
            default_pose
        )

    finally:
        client.destroy()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
