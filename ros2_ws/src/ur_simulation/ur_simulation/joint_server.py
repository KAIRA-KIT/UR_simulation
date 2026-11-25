#!/usr/bin/env python3
import rclpy
import time
import threading
import mujoco
import mujoco.viewer
import numpy as np
from ament_index_python.packages import get_package_share_directory
from control_msgs.action import FollowJointTrajectory
from rclpy.action import ActionServer
from rclpy.node import Node

JOINTS = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
          'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']

class URServer(Node):
    def __init__(self):
        super().__init__('UR_action_server')
        robot = self.declare_parameter('robot', 'ur10e').value
        path = f"{get_package_share_directory('ur_simulation')}/models/scene_{robot}.xml"
        self.m = mujoco.MjModel.from_xml_path(path)
        self.d = mujoco.MjData(self.m)
        mujoco.mj_resetDataKeyframe(self.m, self.d, 0)
        self.viewer = mujoco.viewer.launch_passive(self.m, self.d)
        threading.Thread(target=self.sim_loop, daemon=True).start()
        self._action_server = ActionServer(
            self,
            FollowJointTrajectory,
            'move_robot',
            self.execute_callback)

    def sim_loop(self):
        while self.viewer.is_running():
            t = time.time()
            mujoco.mj_step(self.m, self.d)
            self.viewer.sync()
            time.sleep(max(0, self.m.opt.timestep - (time.time() - t)))

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')
        traj = goal_handle.request.trajectory
        idx = [traj.joint_names.index(j) for j in JOINTS]
        ts = [0.0] + [p.time_from_start.sec + p.time_from_start.nanosec * 1e-9 for p in traj.points]
        qs = np.array([self.d.qpos[:6]] + [np.array(p.positions)[idx] for p in traj.points])
        t0 = time.time()
        while (t := time.time() - t0) < ts[-1]:
            self.d.ctrl[:] = [np.interp(t, ts, qs[:, j]) for j in range(6)]
            time.sleep(0.002)
        self.d.ctrl[:] = qs[-1]
        goal_handle.succeed()
        result = FollowJointTrajectory.Result()
        return result

def main():
    rclpy.init()
    ur_server = URServer()
    rclpy.spin(ur_server)

if __name__ == '__main__':
    main()