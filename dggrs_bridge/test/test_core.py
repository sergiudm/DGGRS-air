import unittest

from dggrs_bridge.dggrs_bridge.core import Click, validate_click


class ValidateClickTests(unittest.TestCase):
    def test_accepts_click_inside_image_bounds(self) -> None:
        click = Click(x=640.0, y=480.0)
        self.assertTrue(validate_click(click, image_width=1280, image_height=720))

    def test_rejects_click_outside_image_bounds(self) -> None:
        click = Click(x=1400.0, y=480.0)
        self.assertFalse(validate_click(click, image_width=1280, image_height=720))


if __name__ == "__main__":
    unittest.main()
