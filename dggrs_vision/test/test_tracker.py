import unittest

from dggrs_vision.dggrs_vision.tracker import estimate_robot_pose


class EstimateRobotPoseTests(unittest.TestCase):
    def test_estimates_centered_mock_pose(self) -> None:
        pose = estimate_robot_pose(image_width=1280, image_height=720, theta_rad=0.25)

        self.assertEqual(pose.x_px, 640.0)
        self.assertEqual(pose.y_px, 360.0)
        self.assertEqual(pose.theta_rad, 0.25)


if __name__ == "__main__":
    unittest.main()
