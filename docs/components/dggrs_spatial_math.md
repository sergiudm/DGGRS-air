# `dggrs_spatial_math`

## Purpose
`dggrs_spatial_math` is the core targeting package. It converts an operator click in image space into a goal in the ground robot's local frame by comparing the clicked pixel against the currently observed robot pixel and scaling both through camera intrinsics and altitude.

This package exists to remove drone drift from the targeting problem. It should rely on relative geometry, not on the drone's global position estimate.

## Responsibilities
- Subscribe to UI click coordinates, robot image pose, altitude, and camera intrinsics.
- Reject incomplete, stale, or physically invalid input combinations.
- Compute the relative ground-plane vector between robot and clicked target.
- Rotate that vector into the ground robot's local frame using the detected heading.
- Publish the final local goal and optional debug outputs for inspection.

## Recommended Interfaces
- Input: `/ui/target_click` as `geometry_msgs/msg/Point`
  - `x` and `y` carry clicked pixel coordinates
- Input: `/vision/robot_pose_2d` as `geometry_msgs/msg/Pose2D`
- Input: `/rtk/altitude_m` as `std_msgs/msg/Float64`
- Input: `/camera/camera_info` as `sensor_msgs/msg/CameraInfo`
- Output: `/ground_robot/goal_pose` as `geometry_msgs/msg/PoseStamped`
- Output: `/spatial_math/debug_vector` as `geometry_msgs/msg/Vector3Stamped`

## Algorithm Contract
For click pixel `(u_t, v_t)` and robot pixel `(u_r, v_r)`, unproject both through the camera intrinsic matrix `K` using the current altitude `Z`. Compute the camera-frame ground vector `V_cam = P_t - P_r`, then rotate by `-theta_r` to express the target in the robot frame. Preserve units in meters end to end.

If the camera optical axis is not normal to the ground plane, this package should be extended with extrinsic calibration rather than silently assuming nadir geometry.

## Key Parameters
- `max_click_age_ms`
- `max_robot_pose_age_ms`
- `min_altitude_m` and `max_altitude_m`
- `goal_frame_id`, typically `odom` or `base_link`
- `publish_debug_topics`

## Failure Modes And Tests
Reject requests when any required input is stale, altitude is outside bounds, or the robot is not currently visible. Unit tests should verify matrix math, heading sign conventions, and meter-per-pixel scaling at representative altitudes. Integration tests should replay recorded clicks and confirm deterministic goals for fixed inputs.
