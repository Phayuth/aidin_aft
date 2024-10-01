import rclpy
from rclpy.node import Node
from geometry_msgs.msg import WrenchStamped
from .aft20d15 import AFT20D15


class AFT20D15Node(Node):

    def __init__(self):
        super().__init__("aft_server")
        # hardware
        self.sensor = AFT20D15("socket")

        # publisher
        self.wmsg = WrenchStamped()
        self.wmsg.header.frame_id = "ftsensor"
        self.ftpub = self.create_publisher(WrenchStamped, "wrench", 1)
        self.timer = self.create_timer(0.01, self.sensor_handle)

        self.get_logger().info("Force Torque Sensor Started !")

    def shutdown(self):
        self.sensor.shutdown()
        self.get_logger().info("Force Torque Sensor Shutdown !")

    def sensor_handle(self):
        ft = self.sensor.receive()
        self.wmsg.header.stamp = self.get_clock().now().to_msg()
        self.wmsg.wrench.force.x = ft[0]
        self.wmsg.wrench.force.y = ft[1]
        self.wmsg.wrench.force.z = ft[2]
        self.wmsg.wrench.torque.x = ft[3]
        self.wmsg.wrench.torque.y = ft[4]
        self.wmsg.wrench.torque.z = ft[5]
        self.ftpub.publish(self.wmsg)


def main(args=None):
    rclpy.init(args=args)
    try:
        n = AFT20D15Node()
        rclpy.spin(n)
    finally:
        n.shutdown()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
