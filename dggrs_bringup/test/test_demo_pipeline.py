import unittest

from dggrs_bringup.dggrs_bringup.demo_pipeline import DemoInputs, run_demo_pipeline


class DemoPipelineTests(unittest.TestCase):
    def test_runs_click_to_goal_flow(self) -> None:
        result = run_demo_pipeline(
            DemoInputs(
                image_width=1280,
                image_height=720,
                click_x=740.0,
                click_y=360.0,
                altitude_m=8.0,
                robot_theta=0.0,
            )
        )

        self.assertTrue(result.click_valid)
        self.assertIsNotNone(result.goal)
        self.assertAlmostEqual(result.goal.x_m, 1.0)
        self.assertAlmostEqual(result.goal.y_m, 0.0)


if __name__ == "__main__":
    unittest.main()
