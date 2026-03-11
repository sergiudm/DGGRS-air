# Drone-Guided Ground Robot System (DGGRS)

This repository contains the ROS 2 software stack for a heterogeneous multi-robot system where a hovering drone acts as an "eye in the sky" guide for a ground robot.

The software runs on the drone's companion computer (NVIDIA Jetson Orin Nano). It streams low-latency, downward-facing video to a user interface. When the user clicks a target destination on the video feed, the system visually anchors to the ground robot, calculates the target's relative physical coordinates to counteract drone drift, and sends a local odometry goal to the ground robot.

## 🌟 Key Features

* **Drift-Resistant Targeting:** Uses relative visual tracking (ArUco/AprilTag or YOLO) to calculate target points relative to the ground robot's current position in the frame, neutralizing drone hover drift.
* **Hardware-Accelerated Streaming:** Utilizes the Jetson Orin Nano's NVENC hardware encoder via GStreamer for low-latency, high-quality video streaming (WebRTC/RTSP) without bottlenecking the CPU.
* **Modular ROS 2 Architecture:** Highly decoupled nodes for vision processing, coordinate transformation, and communication.

## 🛠️ Hardware & Software Requirements

### Hardware

* **Companion Computer:** NVIDIA Jetson Orin Nano (running on the drone).
* **Camera:** Downward-facing CSI or USB 3.0 camera (calibrated).
* **Sensors:** RTK GPS module (for accurate drone altitude $Z$).
* **Ground Robot:** Must have a local odometry frame (`base_link` or `odom`) and a prominent visual fiducial marker (e.g., AprilTag) on its roof.

### Software

* **OS:** Ubuntu 22.04 LTS
* **Middleware:** ROS 2 (Humble or later)
* **Dependencies:** * `gstreamer1.0` and `gst-plugins-bad` (with `nvv4l2h264enc` support)
* `cv_bridge` and `image_transport`
* `isaac_ros_apriltag` (or standard `apriltag_ros` if not using NVIDIA Isaac ROS)
* `tf2_ros`



## 🏗️ System Architecture & Package Structure

The repository is structured into the following primary ROS 2 packages:

* `dggrs_vision`: Detects the ground robot in the raw camera feed. Outputs the robot's pixel coordinates and 2D heading in the image frame.
* `dggrs_streamer`: Subscribes to the raw camera frames, compresses them using hardware acceleration, and serves them to the UI gateway.
* `dggrs_spatial_math`: The core transformation engine. Subscribes to the UI click coordinates, RTK altitude, and the vision node's output to calculate the physical target.
* `dggrs_bridge`: Handles external communications, ingesting UI clicks via WebSockets/UDP and transmitting the final physical goal to the ground robot's ROS 2 network.

Detailed package specifications live under [`docs/components/`](docs/components/README.md):

* [`dggrs_vision`](docs/components/dggrs_vision.md)
* [`dggrs_streamer`](docs/components/dggrs_streamer.md)
* [`dggrs_spatial_math`](docs/components/dggrs_spatial_math.md)
* [`dggrs_bridge`](docs/components/dggrs_bridge.md)
* [`dggrs_bringup`](docs/components/dggrs_bringup.md)

## 🧮 Mathematical Core: The Spatial Transform

To eliminate drone drift, the `dggrs_spatial_math` node avoids using the drone's global global position. Instead, it relies on the camera's intrinsic matrix $K$, the RTK altitude $Z$, the user's target pixel $(u_t, v_t)$, and the tracked robot pixel $(u_r, v_r)$.

The transformation from the 2D pixel space to the ground robot's local 3D frame is calculated as follows:

1. **Unproject Pixels to Camera Frame Rays:**
We map both the target pixel and the robot pixel to normalized 3D rays in the camera frame using the inverse of the intrinsic matrix $K$:
$$\begin{bmatrix} X_{c} \\ Y_{c} \\ Z_{c} \end{bmatrix} = Z \cdot K^{-1} \begin{bmatrix} u \\ v \\ 1 \end{bmatrix}$$


2. **Calculate Relative Physical Vector:**
By applying this to both the target point $P_t$ and the robot point $P_r$, we get their 3D coordinates relative to the camera lens. We then find the physical vector $\vec{V}_{cam}$ between them on the ground plane:
$$\vec{V}_{cam} = \begin{bmatrix} X_{c,t} - X_{c,r} \\ Y_{c,t} - Y_{c,r} \end{bmatrix}$$


3. **Rotate to Robot's Local Frame:**
Finally, we rotate this vector by the ground robot's visual heading $\theta_r$ (extracted from the fiducial marker) to generate the final goal $(X_{goal}, Y_{goal})$ in the ground robot's local odometry frame:
$$\begin{bmatrix} X_{goal} \\ Y_{goal} \end{bmatrix} = \begin{bmatrix} \cos(-\theta_r) & -\sin(-\theta_r) \\ \sin(-\theta_r) & \cos(-\theta_r) \end{bmatrix} \vec{V}_{cam}$$



## 🚀 Installation & Setup

1. **Clone the repository into your ROS 2 workspace:**
```bash
cd ~/ros2_ws/src
git clone https://github.com/your-org/dggrs.git

```


2. **Install dependencies using rosdep:**
```bash
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y

```


3. **Build the workspace:**
```bash
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release

```


4. **Source the workspace:**
```bash
source install/setup.bash

```



## 💻 Usage

To launch the entire stack on the Jetson Orin Nano:

1. Update the `config/camera_params.yaml` file with your specific camera's intrinsic matrix and focal length.
2. Run the main launch file:
```bash
ros2 launch dggrs_bringup air_guide.launch.py

```



### Simulating a UI Click

To test the pipeline without the UI connected, you can publish a mock UI click using the command line:

```bash
ros2 topic pub -1 /ui/target_click geometry_msgs/msg/Point "{x: 640.0, y: 480.0, z: 0.0}"

```

The stack will output the calculated local goal on the `/ground_robot/goal_pose` topic.
