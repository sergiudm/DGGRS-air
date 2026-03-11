from dataclasses import dataclass
import math


@dataclass(frozen=True)
class CameraIntrinsics:
    fx: float
    fy: float
    cx: float
    cy: float


@dataclass(frozen=True)
class GoalRequest:
    click_x: float
    click_y: float
    robot_x: float
    robot_y: float
    robot_theta: float
    altitude_m: float


@dataclass(frozen=True)
class GoalResult:
    x_m: float
    y_m: float
    debug_dx_m: float
    debug_dy_m: float


def compute_goal(
    request: GoalRequest,
    intrinsics: CameraIntrinsics,
    min_altitude_m: float,
    max_altitude_m: float,
) -> GoalResult | None:
    if not (min_altitude_m <= request.altitude_m <= max_altitude_m):
        return None
    if intrinsics.fx == 0.0 or intrinsics.fy == 0.0:
        return None

    click_x_cam, click_y_cam = unproject_pixel(
        pixel_x=request.click_x,
        pixel_y=request.click_y,
        altitude_m=request.altitude_m,
        intrinsics=intrinsics,
    )
    robot_x_cam, robot_y_cam = unproject_pixel(
        pixel_x=request.robot_x,
        pixel_y=request.robot_y,
        altitude_m=request.altitude_m,
        intrinsics=intrinsics,
    )

    dx_cam = click_x_cam - robot_x_cam
    dy_cam = click_y_cam - robot_y_cam

    goal_x = math.cos(request.robot_theta) * dx_cam + math.sin(request.robot_theta) * dy_cam
    goal_y = -math.sin(request.robot_theta) * dx_cam + math.cos(request.robot_theta) * dy_cam
    return GoalResult(x_m=goal_x, y_m=goal_y, debug_dx_m=dx_cam, debug_dy_m=dy_cam)


def unproject_pixel(pixel_x: float, pixel_y: float, altitude_m: float, intrinsics: CameraIntrinsics) -> tuple[float, float]:
    x_cam = (pixel_x - intrinsics.cx) * altitude_m / intrinsics.fx
    y_cam = (pixel_y - intrinsics.cy) * altitude_m / intrinsics.fy
    return x_cam, y_cam
