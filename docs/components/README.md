# Component Documentation

This repository does not yet contain the ROS 2 packages described in the system overview. The documents in this directory act as implementation-facing specifications for those packages so contributors can build against a shared contract.

## Components

### `dggrs_vision`
Vision frontend for locating the ground robot in the downward camera image and estimating its in-image heading.

See [dggrs_vision.md](dggrs_vision.md).

### `dggrs_streamer`
Low-latency video delivery package for sending raw or annotated camera frames to the operator UI using Jetson-friendly hardware encoding.

See [dggrs_streamer.md](dggrs_streamer.md).

### `dggrs_spatial_math`
Control-plane math package that turns a UI pixel click, robot image pose, and altitude estimate into a local goal in the ground robot frame.

See [dggrs_spatial_math.md](dggrs_spatial_math.md).

### `dggrs_bridge`
Networking and protocol adapter between ROS 2 topics and external systems such as the web UI and the ground robot network.

See [dggrs_bridge.md](dggrs_bridge.md).

### `dggrs_bringup`
Launch, configuration, and environment wiring package that assembles the full stack for hardware runs and repeatable testing.

See [dggrs_bringup.md](dggrs_bringup.md).

## Conventions Used In These Docs

The interfaces described here are the recommended canonical ones for the initial implementation. If code diverges from these docs, update the matching document in the same change so the repository keeps one source of truth for topics, parameters, and runtime behavior.
