import unittest

from dggrs_bringup.dggrs_bringup.simulator import SimulatorConfig, simulate_scenario


class SimulatorTests(unittest.TestCase):
    def test_preserves_relative_goal_under_drone_drift(self) -> None:
        result = simulate_scenario(
            SimulatorConfig(
                duration_s=6.0,
                step_s=0.5,
                drone_velocity_x_mps=0.6,
                drone_velocity_y_mps=-0.35,
                robot_velocity_x_mps=0.15,
                robot_velocity_y_mps=0.1,
                robot_start_theta_rad=0.4,
                robot_yaw_rate_radps=0.08,
                target_world_x_m=5.5,
                target_world_y_m=1.5,
            )
        )

        self.assertTrue(all(sample.click_valid for sample in result.samples))
        self.assertGreater(len(result.samples), 2)
        self.assertLess(result.max_goal_error_m, 1e-9)

    def test_flags_targets_that_leave_the_image(self) -> None:
        result = simulate_scenario(
            SimulatorConfig(
                altitude_m=4.0,
                target_world_x_m=12.0,
                target_world_y_m=0.0,
                duration_s=1.0,
                step_s=0.5,
                drone_velocity_x_mps=0.0,
                drone_velocity_y_mps=0.0,
                robot_velocity_x_mps=0.0,
                robot_velocity_y_mps=0.0,
            )
        )

        self.assertTrue(all(not sample.click_valid for sample in result.samples))
        self.assertTrue(all(sample.goal_x_m is None for sample in result.samples))
        self.assertEqual(result.max_goal_error_m, 0.0)


if __name__ == "__main__":
    unittest.main()
