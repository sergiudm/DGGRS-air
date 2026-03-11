from dataclasses import dataclass


@dataclass(frozen=True)
class MockInputConfig:
    image_width: int
    image_height: int
    altitude_m: float
    frame_id: str


@dataclass(frozen=True)
class MockInputState:
    image_width: int
    image_height: int
    altitude_m: float
    frame_id: str
    camera_matrix: tuple[float, float, float, float, float, float, float, float, float]


def build_mock_input_state(config: MockInputConfig) -> MockInputState:
    return MockInputState(
        image_width=config.image_width,
        image_height=config.image_height,
        altitude_m=config.altitude_m,
        frame_id=config.frame_id,
        camera_matrix=(
            800.0,
            0.0,
            float(config.image_width) / 2.0,
            0.0,
            800.0,
            float(config.image_height) / 2.0,
            0.0,
            0.0,
            1.0,
        ),
    )
