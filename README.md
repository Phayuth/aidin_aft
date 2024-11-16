# AIDIN Robotics Force Torque Sensor
- AFT20-D15

## Install
```bash
pip install "python-can[gs_usb]"
```

## Setup
TODO

## Permission
```bash
sudo chmod 666 /dev/ttyUSB1
```

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

## Useful command

- USB detail `/bin/udevadm info --name=/dev/ttyUSB1`
- USB port `ls -l /dev/serial/by-id/`