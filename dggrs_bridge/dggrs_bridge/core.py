from dataclasses import dataclass


@dataclass(frozen=True)
class Click:
    x: float
    y: float


def validate_click(click: Click, image_width: int, image_height: int) -> bool:
    return 0.0 <= click.x <= float(image_width) and 0.0 <= click.y <= float(image_height)
