#include <cstdlib>
#include <cstring>
#include <iostream>
#include <linux/can.h>
#include <linux/can/raw.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <unistd.h>

unsigned int datafields[2][3];
double fx, fy, fz, tx, ty, tz;

int main() {
    // Create a socket
    int socket_can = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    if (socket_can < 0) {
        std::cerr << "Error while opening socket" << std::endl;
        return -1;
    }

    // Specify can0 interface
    struct ifreq ifr;
    std::strcpy(ifr.ifr_name, "can0");
    ioctl(socket_can, SIOCGIFINDEX, &ifr); // Get interface index for can0

    // Bind the socket to can0
    struct sockaddr_can addr;
    std::memset(&addr, 0, sizeof(addr));
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    if (bind(socket_can, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        std::cerr << "Error in socket bind" << std::endl;
        return -2;
    }

    // Prepare to receive CAN messages
    struct can_frame frame;
    while (true) {
        // canbus contains 2 frames : force and torque
        for (size_t i = 0; i < 2; i++) {
            int nbytes = read(socket_can, &frame, sizeof(struct can_frame));

            if (nbytes < 0) {
                std::cerr << "CAN read error" << std::endl;
                break;
            }

            if (frame.can_id == 0x01a) { // force
                datafields[0][0] = (unsigned int)frame.data[0] * 256 + (unsigned int)frame.data[1];
                datafields[0][1] = (unsigned int)frame.data[2] * 256 + (unsigned int)frame.data[3];
                datafields[0][2] = (unsigned int)frame.data[4] * 256 + (unsigned int)frame.data[5];
            }

            if (frame.can_id == 0x01b) { // torque
                datafields[1][0] = (unsigned int)frame.data[0] * 256 + (unsigned int)frame.data[1];
                datafields[1][1] = (unsigned int)frame.data[2] * 256 + (unsigned int)frame.data[3];
                datafields[1][2] = (unsigned int)frame.data[4] * 256 + (unsigned int)frame.data[5];
            }

            // for (int i = 0; i < frame.can_dlc; i++) {
            //     std::cout << std::hex << (int)frame.data[i] << " ";
            // }
            // std::cout << std::endl;
        }
        fx = (datafields[0][0] / 1000.0) - 30.0;
        fy = (datafields[0][1] / 1000.0) - 30.0;
        fz = (datafields[0][2] / 1000.0) - 30.0;

        tx = (datafields[1][0] / 100000.0) - 0.3;
        ty = (datafields[1][1] / 100000.0) - 0.3;
        tz = (datafields[1][2] / 100000.0) - 0.3;

        printf("%f, %f, %f, %f, %f, %f \n", fx, fy, fz, tx, ty, tz);
    }

    close(socket_can);
    return 0;
}
