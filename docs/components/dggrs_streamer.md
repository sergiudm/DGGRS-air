# `dggrs_streamer`

## Purpose
`dggrs_streamer` is responsible for operator video. It should provide the lowest practical latency from camera to UI without consuming CPU budget needed by perception and control nodes. On Jetson hardware, this package should favor NVENC-backed GStreamer pipelines.

This package is not part of the control loop, but operator trust depends on it. A laggy or unstable stream directly reduces click accuracy and perceived system quality.

## Responsibilities
- Subscribe to the selected video source, typically raw camera frames or a debug overlay feed.
- Encode video using hardware acceleration when available.
- Serve the stream to the UI gateway over WebRTC or RTSP.
- Expose health and pipeline state so bringup can detect encoder or transport failures.
- Optionally switch between raw and annotated feeds through configuration.

## Recommended Interfaces
- Input: `/camera/image_raw` or `/vision/debug_image` as `sensor_msgs/msg/Image`
- Output: external stream endpoint such as `rtsp://<host>:8554/dggrs` or a WebRTC session
- Output: `/streamer/status` as `diagnostic_msgs/msg/DiagnosticArray` or equivalent health topic

## Key Parameters
- `source_topic`: ROS image topic to stream
- `transport_mode`: `rtsp` or `webrtc`
- `codec`: start with `h264`
- `bitrate_kbps`: encoder target bitrate
- `gop_size`: keyframe interval
- `bind_host` and `bind_port`: network exposure
- `overlay_enabled`: whether to stream annotated frames

## Runtime Notes
Keep buffering shallow. For operator control, it is usually better to drop frames under load than to queue them and increase latency. The streamer should start after the camera topic is live and should fail fast if the requested encoder element is unavailable. Any required GStreamer string should live in config, not in launch logic.

## Failure Modes And Tests
Common issues include missing `nvv4l2h264enc`, oversized bitrate for the radio link, and firewall or NAT problems on the serving port. Validate with a local viewer first, then measure end-to-end latency on the target network. Regression tests should include startup with no camera feed, reconnect behavior after source drop, and CPU usage checks on Jetson hardware.
