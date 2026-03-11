from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import math

try:
    from dggrs_bridge.core import Click, validate_click
    from dggrs_spatial_math.core import CameraIntrinsics, GoalRequest, compute_goal
except ImportError:
    from dggrs_bridge.dggrs_bridge.core import Click, validate_click
    from dggrs_spatial_math.dggrs_spatial_math.core import (
        CameraIntrinsics,
        GoalRequest,
        compute_goal,
    )


@dataclass(frozen=True)
class SimulatorConfig:
    image_width: int = 1280
    image_height: int = 720
    altitude_m: float = 8.0
    fx: float = 800.0
    fy: float = 800.0
    target_world_x_m: float = 6.0
    target_world_y_m: float = 2.0
    duration_s: float = 5.0
    step_s: float = 1.0
    drone_start_x_m: float = 0.0
    drone_start_y_m: float = 0.0
    drone_velocity_x_mps: float = 0.4
    drone_velocity_y_mps: float = -0.2
    robot_start_x_m: float = 2.0
    robot_start_y_m: float = 0.5
    robot_velocity_x_mps: float = 0.2
    robot_velocity_y_mps: float = 0.05
    robot_start_theta_rad: float = 0.3
    robot_yaw_rate_radps: float = 0.05
    min_altitude_m: float = 0.5
    max_altitude_m: float = 100.0


@dataclass(frozen=True)
class SimulatorSample:
    time_s: float
    click_valid: bool
    drone_x_m: float
    drone_y_m: float
    robot_world_x_m: float
    robot_world_y_m: float
    robot_theta_rad: float
    robot_x_px: float
    robot_y_px: float
    click_x_px: float
    click_y_px: float
    expected_goal_x_m: float
    expected_goal_y_m: float
    goal_x_m: float | None
    goal_y_m: float | None
    goal_error_m: float | None


@dataclass(frozen=True)
class SimulationResult:
    samples: tuple[SimulatorSample, ...]
    max_goal_error_m: float


def simulate_scenario(config: SimulatorConfig) -> SimulationResult:
    intrinsics = CameraIntrinsics(
        fx=config.fx,
        fy=config.fy,
        cx=float(config.image_width) / 2.0,
        cy=float(config.image_height) / 2.0,
    )
    samples: list[SimulatorSample] = []
    max_goal_error_m = 0.0

    for time_s in _time_samples(config.duration_s, config.step_s):
        drone_x_m = config.drone_start_x_m + config.drone_velocity_x_mps * time_s
        drone_y_m = config.drone_start_y_m + config.drone_velocity_y_mps * time_s
        robot_world_x_m = config.robot_start_x_m + config.robot_velocity_x_mps * time_s
        robot_world_y_m = config.robot_start_y_m + config.robot_velocity_y_mps * time_s
        robot_theta_rad = config.robot_start_theta_rad + config.robot_yaw_rate_radps * time_s

        robot_x_px, robot_y_px = project_world_to_pixel(
            world_x_m=robot_world_x_m,
            world_y_m=robot_world_y_m,
            camera_x_m=drone_x_m,
            camera_y_m=drone_y_m,
            altitude_m=config.altitude_m,
            intrinsics=intrinsics,
        )
        click_x_px, click_y_px = project_world_to_pixel(
            world_x_m=config.target_world_x_m,
            world_y_m=config.target_world_y_m,
            camera_x_m=drone_x_m,
            camera_y_m=drone_y_m,
            altitude_m=config.altitude_m,
            intrinsics=intrinsics,
        )

        expected_goal_x_m, expected_goal_y_m = rotate_world_to_robot_frame(
            delta_x_m=config.target_world_x_m - robot_world_x_m,
            delta_y_m=config.target_world_y_m - robot_world_y_m,
            robot_theta_rad=robot_theta_rad,
        )
        click_valid = validate_click(
            Click(x=click_x_px, y=click_y_px),
            image_width=config.image_width,
            image_height=config.image_height,
        )
        goal_x_m: float | None = None
        goal_y_m: float | None = None
        goal_error_m: float | None = None

        if click_valid:
            goal = compute_goal(
                GoalRequest(
                    click_x=click_x_px,
                    click_y=click_y_px,
                    robot_x=robot_x_px,
                    robot_y=robot_y_px,
                    robot_theta=robot_theta_rad,
                    altitude_m=config.altitude_m,
                ),
                intrinsics=intrinsics,
                min_altitude_m=config.min_altitude_m,
                max_altitude_m=config.max_altitude_m,
            )
            if goal is not None:
                goal_x_m = goal.x_m
                goal_y_m = goal.y_m
                goal_error_m = math.hypot(
                    goal.x_m - expected_goal_x_m,
                    goal.y_m - expected_goal_y_m,
                )
                max_goal_error_m = max(max_goal_error_m, goal_error_m)

        samples.append(
            SimulatorSample(
                time_s=time_s,
                click_valid=click_valid,
                drone_x_m=drone_x_m,
                drone_y_m=drone_y_m,
                robot_world_x_m=robot_world_x_m,
                robot_world_y_m=robot_world_y_m,
                robot_theta_rad=robot_theta_rad,
                robot_x_px=robot_x_px,
                robot_y_px=robot_y_px,
                click_x_px=click_x_px,
                click_y_px=click_y_px,
                expected_goal_x_m=expected_goal_x_m,
                expected_goal_y_m=expected_goal_y_m,
                goal_x_m=goal_x_m,
                goal_y_m=goal_y_m,
                goal_error_m=goal_error_m,
            )
        )

    return SimulationResult(samples=tuple(samples), max_goal_error_m=max_goal_error_m)


def project_world_to_pixel(
    world_x_m: float,
    world_y_m: float,
    camera_x_m: float,
    camera_y_m: float,
    altitude_m: float,
    intrinsics: CameraIntrinsics,
) -> tuple[float, float]:
    x_cam_m = world_x_m - camera_x_m
    y_cam_m = world_y_m - camera_y_m
    pixel_x = intrinsics.cx + (intrinsics.fx * x_cam_m / altitude_m)
    pixel_y = intrinsics.cy + (intrinsics.fy * y_cam_m / altitude_m)
    return pixel_x, pixel_y


def rotate_world_to_robot_frame(
    delta_x_m: float,
    delta_y_m: float,
    robot_theta_rad: float,
) -> tuple[float, float]:
    goal_x_m = math.cos(robot_theta_rad) * delta_x_m + math.sin(robot_theta_rad) * delta_y_m
    goal_y_m = -math.sin(robot_theta_rad) * delta_x_m + math.cos(robot_theta_rad) * delta_y_m
    return goal_x_m, goal_y_m


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Simulate DGGRS relative targeting under robot motion and drone drift."
    )
    parser.add_argument("--image-width", type=int, default=1280)
    parser.add_argument("--image-height", type=int, default=720)
    parser.add_argument("--altitude-m", type=float, default=8.0)
    parser.add_argument("--fx", type=float, default=800.0)
    parser.add_argument("--fy", type=float, default=800.0)
    parser.add_argument("--target-world-x-m", type=float, default=6.0)
    parser.add_argument("--target-world-y-m", type=float, default=2.0)
    parser.add_argument("--duration-s", type=float, default=5.0)
    parser.add_argument("--step-s", type=float, default=1.0)
    parser.add_argument("--drone-start-x-m", type=float, default=0.0)
    parser.add_argument("--drone-start-y-m", type=float, default=0.0)
    parser.add_argument("--drone-velocity-x-mps", type=float, default=0.4)
    parser.add_argument("--drone-velocity-y-mps", type=float, default=-0.2)
    parser.add_argument("--robot-start-x-m", type=float, default=2.0)
    parser.add_argument("--robot-start-y-m", type=float, default=0.5)
    parser.add_argument("--robot-velocity-x-mps", type=float, default=0.2)
    parser.add_argument("--robot-velocity-y-mps", type=float, default=0.05)
    parser.add_argument("--robot-start-theta-rad", type=float, default=0.3)
    parser.add_argument("--robot-yaw-rate-radps", type=float, default=0.05)
    parser.add_argument("--json", action="store_true", dest="emit_json")
    return parser


def config_from_args(args: argparse.Namespace) -> SimulatorConfig:
    return SimulatorConfig(
        image_width=args.image_width,
        image_height=args.image_height,
        altitude_m=args.altitude_m,
        fx=args.fx,
        fy=args.fy,
        target_world_x_m=args.target_world_x_m,
        target_world_y_m=args.target_world_y_m,
        duration_s=args.duration_s,
        step_s=args.step_s,
        drone_start_x_m=args.drone_start_x_m,
        drone_start_y_m=args.drone_start_y_m,
        drone_velocity_x_mps=args.drone_velocity_x_mps,
        drone_velocity_y_mps=args.drone_velocity_y_mps,
        robot_start_x_m=args.robot_start_x_m,
        robot_start_y_m=args.robot_start_y_m,
        robot_velocity_x_mps=args.robot_velocity_x_mps,
        robot_velocity_y_mps=args.robot_velocity_y_mps,
        robot_start_theta_rad=args.robot_start_theta_rad,
        robot_yaw_rate_radps=args.robot_yaw_rate_radps,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    result = simulate_scenario(config_from_args(args))
    if args.emit_json:
        print(
            json.dumps(
                {
                    "max_goal_error_m": result.max_goal_error_m,
                    "samples": [asdict(sample) for sample in result.samples],
                },
                indent=2,
            )
        )
        return 0

    print("t[s]  drone[m]     robot_px      click_px      goal[m]       expected[m]   err[m]")
    for sample in result.samples:
        goal_text = "n/a"
        if sample.goal_x_m is not None and sample.goal_y_m is not None:
            goal_text = f"({sample.goal_x_m:6.2f},{sample.goal_y_m:6.2f})"
        error_text = "n/a" if sample.goal_error_m is None else f"{sample.goal_error_m:6.4f}"
        print(
            f"{sample.time_s:4.1f}  "
            f"({sample.drone_x_m:5.2f},{sample.drone_y_m:5.2f})  "
            f"({sample.robot_x_px:7.1f},{sample.robot_y_px:7.1f})  "
            f"({sample.click_x_px:7.1f},{sample.click_y_px:7.1f})  "
            f"{goal_text:>15}  "
            f"({sample.expected_goal_x_m:6.2f},{sample.expected_goal_y_m:6.2f})  "
            f"{error_text}"
        )
    print(f"max goal error: {result.max_goal_error_m:.6f} m")
    return 0


def _time_samples(duration_s: float, step_s: float) -> tuple[float, ...]:
    if step_s <= 0.0:
        raise ValueError("step_s must be positive")
    if duration_s < 0.0:
        raise ValueError("duration_s must be non-negative")

    samples: list[float] = []
    steps = int(math.floor(duration_s / step_s))
    for index in range(steps + 1):
        samples.append(round(index * step_s, 10))
    if not math.isclose(samples[-1], duration_s):
        samples.append(duration_s)
    return tuple(samples)


if __name__ == "__main__":
    raise SystemExit(main())
