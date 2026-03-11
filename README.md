# DGGRS Air

DGGRS Air is a ROS 2 architecture for a heterogeneous robot team where a hovering drone acts as an overhead guide for a ground robot. The drone streams a downward-facing camera feed to an operator, the operator clicks a destination in the video, and the system converts that image-space click into a local goal for the ground robot.

The design is centered on relative visual geometry rather than the drone's absolute position. That keeps targeting stable even when the drone drifts in hover.

Repository: `https://github.com/sergiudm/DGGRS-air.git`

## Project Status

This repository is currently documentation-first. It contains the system design, package contracts, and implementation-facing specifications for the ROS 2 stack, but it does not yet contain the full package implementations.

The component specifications live under [docs/components/](docs/components/README.md) and act as the source of truth for topics, parameters, and expected runtime behavior.

## What The System Does

- Streams low-latency overhead video from the drone to an operator UI.
- Detects the ground robot in the image and estimates its in-image heading.
- Accepts a UI click as the desired destination.
- Converts that click into a drift-resistant local goal relative to the ground robot.
- Forwards the goal to the ground robot through ROS 2 or a bridge transport.

## Why Relative Targeting

The key design choice is to avoid depending on the drone's global position for target placement. Instead, the system compares two things observed in the same image:

- the clicked target pixel
- the ground robot's current pixel position

Both are projected through the camera model using the current altitude. The resulting relative vector is then rotated into the ground robot's local frame. This makes the command resilient to hover drift and GPS noise.

## Planned Package Architecture

The stack is split into five ROS 2 packages:

- `dggrs_vision`: detects the ground robot in the camera image and publishes its image-space pose.
- `dggrs_streamer`: delivers low-latency video to the operator UI using Jetson-friendly hardware encoding.
- `dggrs_spatial_math`: converts image clicks and robot image pose into a local goal in the robot frame.
- `dggrs_bridge`: bridges external UI and robot-network traffic into and out of ROS 2.
- `dggrs_bringup`: owns launch files, configuration, and full-system wiring.

Detailed package specs:

- [docs/components/dggrs_vision.md](docs/components/dggrs_vision.md)
- [docs/components/dggrs_streamer.md](docs/components/dggrs_streamer.md)
- [docs/components/dggrs_spatial_math.md](docs/components/dggrs_spatial_math.md)
- [docs/components/dggrs_bridge.md](docs/components/dggrs_bridge.md)
- [docs/components/dggrs_bringup.md](docs/components/dggrs_bringup.md)

## End-To-End Data Flow

1. The downward-facing camera publishes calibrated images.
2. `dggrs_vision` detects the ground robot and estimates its image-space heading.
3. `dggrs_streamer` serves video to the operator UI.
4. The operator clicks a point in the video feed.
5. `dggrs_bridge` validates and publishes that click into ROS 2.
6. `dggrs_spatial_math` combines the click, robot image pose, altitude, and camera intrinsics.
7. The system publishes a local goal for the ground robot.
8. `dggrs_bridge` or native ROS networking forwards the goal to the robot.

## Mathematical Core

Let the clicked target pixel be $(u_t, v_t)$ and the observed robot pixel be $(u_r, v_r)$. With camera intrinsics $K$ and altitude $Z$, both pixels are unprojected into the camera frame:

$$
\begin{bmatrix} X_c \\ Y_c \\ Z_c \end{bmatrix}
=
Z \cdot K^{-1}
\begin{bmatrix} u \\ v \\ 1 \end{bmatrix}
$$

This yields two camera-frame ground points, one for the click and one for the robot. Their relative ground-plane vector is:

$$
\vec{V}_{cam} =
\begin{bmatrix}
X_{c,t} - X_{c,r} \\
Y_{c,t} - Y_{c,r}
\end{bmatrix}
$$

Using the robot's visual heading $\theta_r$, the system rotates that vector into the robot's local frame:

$$
\begin{bmatrix} X_{goal} \\ Y_{goal} \end{bmatrix}
=
\begin{bmatrix}
\cos(-\theta_r) & -\sin(-\theta_r) \\
\sin(-\theta_r) & \cos(-\theta_r)
\end{bmatrix}
\vec{V}_{cam}
$$

The result is a target in meters expressed in the ground robot's local frame, typically `odom` or `base_link`.

## Target Deployment Assumptions

### Hardware

- Companion computer: NVIDIA Jetson Orin Nano on the drone.
- Camera: downward-facing calibrated CSI or USB camera.
- Altitude source: RTK GPS or equivalent altitude estimate.
- Ground robot: local odometry frame plus a visible fiducial or otherwise reliable visual marker.

### Software

- Ubuntu 22.04 LTS
- ROS 2 Humble or later
- GStreamer with Jetson encoder support such as `nvv4l2h264enc`
- `cv_bridge` and `image_transport`
- `tf2_ros`
- AprilTag, ArUco, or another supported detection backend

## Repository Layout

```text
.
├── README.md
└── docs/
	└── components/
		├── README.md
		├── dggrs_bridge.md
		├── dggrs_bringup.md
		├── dggrs_spatial_math.md
		├── dggrs_streamer.md
		└── dggrs_vision.md
```

## Getting Started

Clone the repository into the `src` directory of a ROS 2 workspace:

```bash
cd ~/ros2_ws/src
git clone https://github.com/sergiudm/DGGRS-air.git
```

At the moment, this repository provides the design and interface contracts for the system. Once the packages are implemented, the intended workflow is:

```bash
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
source install/setup.bash
```

## Planned Bringup Workflow

The intended full-stack launch entrypoint is:

```bash
ros2 launch dggrs_bringup air_guide.launch.py
```

For pipeline validation, the system is expected to accept a test click like this:

```bash
ros2 topic pub -1 /ui/target_click geometry_msgs/msg/Point "{x: 640.0, y: 480.0, z: 0.0}"
```

The expected output is a local goal on `/ground_robot/goal_pose`.

## Implementation Notes

- Keep package behavior aligned with the specs in [docs/components/](docs/components/README.md).
- If runtime interfaces change, update the matching component document in the same change.
- Prefer explicit topic names, frame IDs, and configuration files over hidden launch-time assumptions.

## License

No project license is defined in this repository yet.
