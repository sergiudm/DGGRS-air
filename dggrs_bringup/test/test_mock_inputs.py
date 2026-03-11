import unittest

from dggrs_bringup.dggrs_bringup.mock_inputs import MockInputConfig, build_mock_input_state


class MockInputStateTests(unittest.TestCase):
    def test_builds_consistent_mock_sensor_state(self) -> None:
        state = build_mock_input_state(
            MockInputConfig(
                image_width=1280,
                image_height=720,
                altitude_m=8.0,
                frame_id="camera_optical_frame",
            )
        )

        self.assertEqual(state.image_width, 1280)
        self.assertEqual(state.image_height, 720)
        self.assertEqual(state.altitude_m, 8.0)
        self.assertEqual(state.camera_matrix, (800.0, 0.0, 640.0, 0.0, 800.0, 360.0, 0.0, 0.0, 1.0))


if __name__ == "__main__":
    unittest.main()
