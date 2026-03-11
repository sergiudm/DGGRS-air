import math
import unittest

from dggrs_spatial_math.dggrs_spatial_math.core import (
    CameraIntrinsics,
    GoalRequest,
    compute_goal,
)


class ComputeGoalTests(unittest.TestCase):
    def test_computes_relative_goal_in_robot_frame(self) -> None:
        intrinsics = CameraIntrinsics(fx=800.0, fy=800.0, cx=640.0, cy=360.0)
        request = GoalRequest(
            click_x=740.0,
            click_y=360.0,
            robot_x=640.0,
            robot_y=360.0,
            robot_theta=0.0,
            altitude_m=8.0,
        )

        goal = compute_goal(request, intrinsics, min_altitude_m=0.5, max_altitude_m=100.0)

        self.assertIsNotNone(goal)
        self.assertAlmostEqual(goal.x_m, 1.0)
        self.assertAlmostEqual(goal.y_m, 0.0)
        self.assertAlmostEqual(goal.debug_dx_m, 1.0)
        self.assertAlmostEqual(goal.debug_dy_m, 0.0)

    def test_rotates_camera_vector_into_robot_frame(self) -> None:
        intrinsics = CameraIntrinsics(fx=800.0, fy=800.0, cx=640.0, cy=360.0)
        request = GoalRequest(
            click_x=640.0,
            click_y=460.0,
            robot_x=640.0,
            robot_y=360.0,
            robot_theta=math.pi / 2.0,
            altitude_m=8.0,
        )

        goal = compute_goal(request, intrinsics, min_altitude_m=0.5, max_altitude_m=100.0)

        self.assertIsNotNone(goal)
        self.assertAlmostEqual(goal.x_m, 1.0, places=5)
        self.assertAlmostEqual(goal.y_m, 0.0, places=5)

    def test_rejects_out_of_range_altitude(self) -> None:
        intrinsics = CameraIntrinsics(fx=800.0, fy=800.0, cx=640.0, cy=360.0)
        request = GoalRequest(
            click_x=740.0,
            click_y=360.0,
            robot_x=640.0,
            robot_y=360.0,
            robot_theta=0.0,
            altitude_m=0.1,
        )

        goal = compute_goal(request, intrinsics, min_altitude_m=0.5, max_altitude_m=100.0)

        self.assertIsNone(goal)


if __name__ == "__main__":
    unittest.main()
