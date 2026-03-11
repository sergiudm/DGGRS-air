# `dggrs_bringup`

## Purpose
`dggrs_bringup` is the assembly package for the system. It should own launch files, packaged configuration, environment defaults, and operational profiles for hardware runs, lab validation, and simulation.

This package is where contributors should look first when they need to understand how the full system is wired together.

## Responsibilities
- Launch the camera, vision, streamer, spatial math, and bridge nodes with coherent namespaces and parameters.
- Centralize configuration files for camera calibration, networking, detection backend, and topic names.
- Provide separate launch entrypoints for hardware, debug, and test scenarios.
- Declare startup ordering assumptions and fail clearly when required resources are missing.

## Expected Package Layout
- `launch/air_guide.launch.py`: full hardware stack
- `launch/vision_debug.launch.py`: camera plus `dggrs_vision`
- `launch/click_pipeline_test.launch.py`: bridge plus spatial math for lab testing
- `launch/basic_demo.launch.py`: full mock-input demo pipeline
- `config/camera_params.yaml`: intrinsic matrix and distortion values
- `config/vision.yaml`, `config/streamer.yaml`, `config/bridge.yaml`: per-package defaults

## Launch Behavior
The main launch file should expose only a small set of high-value arguments such as camera source, detection backend, stream mode, and whether debug overlays are enabled. Per-node tuning belongs in YAML files. Bringup should also make frame IDs, topic remaps, and namespace prefixes explicit so multi-robot or simulation use is possible later without hidden assumptions.

## Operational Notes
Prefer deterministic startup over convenience. For example, the stack should not publish operator-ready status until camera calibration is loaded and the bridge transport is bound successfully. If diagnostics are available, aggregate them here so operators can see a single system status view.

For local validation without ROS middleware, this package may also ship pure-Python simulation helpers as long as they exercise the same topic contracts and math assumptions as the live nodes. The current scaffold includes a `dggrs_simulator` CLI that models drone drift, robot motion, and image projection while reusing the same spatial-math core.

## Tests And Maintenance
Launch tests should confirm that all declared files exist, parameters load cleanly, and required topics appear. Any change to topic names, frame IDs, or configuration paths should be reflected in this package first, then in the affected component docs.
