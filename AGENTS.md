# Repository Guidelines

## Project Structure & Module Organization
This repository is documentation-first today. [`README.md`](/Users/sergiu/ws/air-ground/README.md) defines the DGGRS system, and [`docs/components/`](/Users/sergiu/ws/air-ground/docs/components/README.md) contains implementation-facing specs for the planned ROS 2 packages: `dggrs_vision`, `dggrs_streamer`, `dggrs_spatial_math`, `dggrs_bridge`, and `dggrs_bringup`.

When adding code, keep each package in standard ROS 2 layout: `src/` for node code, `include/` for public headers, `launch/` for launch entrypoints, `config/` for YAML defaults, and `test/` for unit or launch tests.

## Build, Test, and Development Commands
Use normal ROS 2 workspace commands from the workspace root once packages are present:

```bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
source install/setup.bash
colcon test --event-handlers console_direct+
colcon test-result --verbose
ros2 launch dggrs_bringup air_guide.launch.py
```

For pipeline checks, the project README uses:

```bash
ros2 topic pub -1 /ui/target_click geometry_msgs/msg/Point "{x: 640.0, y: 480.0, z: 0.0}"
```

## Coding Style & Naming Conventions
Follow ROS 2 conventions. Use 4-space indentation, `snake_case` for package names, topics, parameters, Python modules, and YAML keys, and `PascalCase` for C++ classes. Name launch files `*.launch.py` and keep executables descriptive, for example `target_transform_node`.

Prefer small, single-purpose nodes. Keep frame IDs, topic names, and units explicit. If behavior changes from the component specs, update the matching file under `docs/components/` in the same change.

## Testing Guidelines
Add tests under each package’s `test/` directory. Prioritize math correctness, topic contracts, stale-input rejection, and launch-level wiring. Use reproducible inputs such as recorded bags or fixed topic publishes, and keep expected outputs deterministic.

## Commit & Pull Request Guidelines
The visible history is minimal, so use short imperative commit subjects such as `Add spatial math goal validation`. Keep commits focused by package or subsystem.

PRs should state what changed, which package specs were updated, how the change was validated, and any hardware assumptions. Include logs or screenshots when touching streaming, calibration, or operator-facing behavior.

## Configuration Tips
Store camera intrinsics, detector settings, and network endpoints in YAML under `config/`; do not hardcode them in nodes. Avoid committing environment-specific IPs, secrets, or machine-local calibration artifacts unless they are sanitized sample files.
