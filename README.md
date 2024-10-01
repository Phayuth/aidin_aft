# AIDIN Robotics Force Torque Sensor
- AFT20-D15

## Install
```bash
pip install "python-can[gs_usb]"
```

## Setup
TODO

## Open communication
- Attach canbus ```sudo ip link set dev can0 up type can bitrate 1000000```
- Listen to canbus ```candump can0```
- Send to canbus ```cansend can0 001#1122334455667788```
- Check hardware diagnostic message ```dmesg```

## Launch ROS Node
```bash
ros2 launch aidin_aft aft_bringup.launch.py
```

## Reference [List](./doc/)