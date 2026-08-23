# Horizon Stabilization Module

This is an engineering-ready module for horizon stabilization in moving cameras, combining IMU and vision data.

## Features
- Modular design with HorizonStabilizer class
- IMU data integration with Kalman filtering
- Vision-based horizon detection with probabilistic Hough transform
- Camera undistortion for wide-angle lenses (~105° FOV)
- Real-time processing capability
- Output stabilized video

## Requirements
Install dependencies:
```
pip install -r requirements.txt
```

## Usage
Run the stabilization:
```
python main.py --video path/to/input.mp4 --output path/to/output.mp4
```

For real IMU data, modify the `simulate_imu` function to read from sensors.

## Class Overview
- `HorizonStabilizer`: Main class handling stabilization
  - `process_frame(frame, imu_data, timestamp)`: Process single frame
  - Returns stabilized frame and correction angle

## Integration
Import and use in your application:
```python
from main import HorizonStabilizer
stabilizer = HorizonStabilizer()
stabilized, angle = stabilizer.process_frame(frame, (roll, pitch, yaw), time.time())
```