from dataclasses import dataclass

try:
    from dggrs_bridge.core import Click, validate_click
    from dggrs_spatial_math.core import CameraIntrinsics, GoalResult, GoalRequest, compute_goal
    from dggrs_vision.tracker import RobotPoseEstimate, estimate_robot_pose
except ImportError:
    from dggrs_bridge.dggrs_bridge.core import Click, validate_click
    from dggrs_spatial_math.dggrs_spatial_math.core import (
        CameraIntrinsics,
        GoalResult,
        GoalRequest,
        compute_goal,
    )
    from dggrs_vision.dggrs_vision.tracker import RobotPoseEstimate, estimate_robot_pose


@dataclass(frozen=True)
class DemoInputs:
    image_width: int
    image_height: int
    click_x: float
    click_y: float
    altitude_m: float
    robot_theta: float


@dataclass(frozen=True)
class DemoResult:
    click_valid: bool
    robot_pose: RobotPoseEstimate
    goal: GoalResult | None


def run_demo_pipeline(inputs: DemoInputs) -> DemoResult:
    click = Click(x=inputs.click_x, y=inputs.click_y)
    click_valid = validate_click(click, image_width=inputs.image_width, image_height=inputs.image_height)
    robot_pose = estimate_robot_pose(
        image_width=inputs.image_width,
        image_height=inputs.image_height,
        theta_rad=inputs.robot_theta,
    )
    if not click_valid:
        return DemoResult(click_valid=False, robot_pose=robot_pose, goal=None)

    intrinsics = CameraIntrinsics(
        fx=800.0,
        fy=800.0,
        cx=float(inputs.image_width) / 2.0,
        cy=float(inputs.image_height) / 2.0,
    )
    goal = compute_goal(
        GoalRequest(
            click_x=click.x,
            click_y=click.y,
            robot_x=robot_pose.x_px,
            robot_y=robot_pose.y_px,
            robot_theta=robot_pose.theta_rad,
            altitude_m=inputs.altitude_m,
        ),
        intrinsics=intrinsics,
        min_altitude_m=0.5,
        max_altitude_m=100.0,
    )
    return DemoResult(click_valid=True, robot_pose=robot_pose, goal=goal)
