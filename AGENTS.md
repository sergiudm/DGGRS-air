# Repository Guidelines

## Project Structure & Module Organization
This repository currently contains a single planning document, `README.md`, which defines the intended ROS 2 workspace layout for the Drone-Guided Ground Robot System. New code should be added as top-level ROS 2 packages that match the architecture described there: `dggrs_vision`, `dggrs_streamer`, `dggrs_spatial_math`, `dggrs_bridge`, and `dggrs_bringup`.

Keep each package in standard ROS 2 form: source in `src/`, public headers in `include/`, launch files in `launch/`, configuration in `config/`, and tests in `test/`. Store calibration YAML, topic defaults, and camera parameters under `config/`, not hardcoded in nodes.

## Build, Test, and Development Commands
Use standard ROS 2 workspace commands from the workspace root:

```bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
source install/setup.bash
ros2 launch dggrs_bringup air_guide.launch.py
ros2 topic pub -1 /ui/target_click geometry_msgs/msg/Point "{x: 640.0, y: 480.0, z: 0.0}"
```

Run tests with:

```bash
colcon test --event-handlers console_direct+
colcon test-result --verbose
```

Use the topic publish command above for quick end-to-end validation of click-to-goal flow.

## Coding Style & Naming Conventions
Follow ROS 2 conventions. Use 4-space indentation, `snake_case` for package names, Python modules, topics, parameters, and YAML keys, and `PascalCase` for C++ classes. Name launch files `*.launch.py` and keep node executables descriptive, for example `target_transform_node`.

Prefer small, single-purpose nodes with explicit topic and frame names. Document camera assumptions, coordinate frames, and units in code comments where ambiguity would cause integration errors.

## Testing Guidelines
Add unit tests beside each package under `test/`. Prioritize coverage for pixel-to-ground transforms, frame rotation, topic contracts, and failure handling for missing detections or altitude input. For integration changes, include a launch test or a reproducible topic-based check.

## Commit & Pull Request Guidelines
Git history is not available in this checkout, so use concise imperative commit subjects under 72 characters, for example `Add dggrs_bridge click relay node`. Keep commits focused by package.

PRs should describe the affected packages, the runtime scenario tested, and any hardware assumptions. Include logs, launch commands, or screenshots when touching UI streaming, calibration, or robot-goal behavior.
