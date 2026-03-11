# `dggrs_vision`

## Purpose
`dggrs_vision` is the perception entrypoint for the stack. It consumes the downward-facing camera feed, identifies the ground robot in image space, and produces a stable 2D pose estimate relative to the image frame: pixel center `(u, v)` and heading `theta`.

Because the downstream targeting pipeline works in relative coordinates, this package must prioritize consistent tracking over global localization. A noisy but continuous estimate is more useful than intermittent absolute detections.

## Responsibilities
- Subscribe to the calibrated camera stream and camera intrinsics.
- Detect the ground robot using a fiducial workflow such as AprilTag, ArUco, or a learned detector.
- Estimate robot center pixel coordinates and robot heading in image space.
- Publish optional debug overlays that show the current detection and heading arrow.
- Surface visibility state and confidence so downstream nodes can reject stale targets.

## Recommended Interfaces
- Input: `/camera/image_raw` as `sensor_msgs/msg/Image`
- Input: `/camera/camera_info` as `sensor_msgs/msg/CameraInfo`
- Output: `/vision/robot_pose_2d` as `geometry_msgs/msg/Pose2D`
  - `x` and `y` are image pixels
  - `theta` is robot heading in image plane radians
- Output: `/vision/debug_image` as `sensor_msgs/msg/Image`
- Output: `/vision/target_visible` as `std_msgs/msg/Bool`

## Key Parameters
- `detection_backend`: `apriltag`, `aruco`, or `yolo`
- `marker_family`: tag family when using fiducials
- `confidence_threshold`: minimum score for publishing a valid detection
- `publish_debug_image`: enable annotated image output
- `image_transport`: `raw` or compressed transport setting
- `max_detection_age_ms`: how long a result remains usable downstream

## Runtime Notes
The package should timestamp every published estimate with the source image stamp. If multiple detections exist, choose one deterministic target selection rule, such as highest confidence or known robot ID, and document it in config. When detection is lost, keep publishing visibility state changes immediately rather than silently freezing the last pose.

## Failure Modes And Tests
Primary failure cases are motion blur, partial occlusion, altitude changes that alter apparent tag scale, and false positives from background texture. Tests should cover detection on recorded bags, heading sign correctness, debug overlay alignment, and stale-result handling when detections disappear.
