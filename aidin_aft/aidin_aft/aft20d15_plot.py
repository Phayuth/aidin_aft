import can
import threading
import queue
import time

import matplotlib.pyplot as plt
from collections import deque


class AFT20D15:

    def __init__(self):
        self.bus = can.Bus(
            interface="robotell",
            channel="/dev/ttyUSB0@115200",
            rtscts=False,
            bitrate=1000000,
        )

        self.forceid = 0x01A
        self.torqueid = 0x01B

    def byte_to_output(self, b):
        return [b[0] * 256 + b[1], b[2] * 256 + b[3], b[4] * 256 + b[5]]

    def get_force(self, d):
        return [d[0] / 1000 - 30, d[1] / 1000 - 30, d[2] / 1000 - 30]

    def get_torque(self, d):
        return [d[0] / 100000 - 0.3, d[1] / 100000 - 0.3, d[2] / 100000 - 0.3]

    def receive(self):
        force = None
        torque = None

        while True:
            msg = self.bus.recv(timeout=1)
            if msg is None:
                continue

            data = self.byte_to_output(list(msg.data))

            if msg.arbitration_id == self.forceid:
                force = self.get_force(data)

            if msg.arbitration_id == self.torqueid:
                torque = self.get_torque(data)

            if force is not None and torque is not None:
                return force + torque

    def shutdown(self):
        self.bus.shutdown()


def low_pass_filter(prev, new, alpha=0.5):
    if prev is None:
        return new
    return alpha * prev + (1 - alpha) * new


# -----------------------------
# 전역 상태
# -----------------------------
stop_flag = False


# -----------------------------
# Thread
# -----------------------------
def data_thread(sensor, q):
    global stop_flag

    start = time.time()

    buffer = []
    bias = None

    while not stop_flag:
        ft = sensor.receive()
        t = time.time() - start

        # -----------------------------
        # bias 수집 (3~4초)
        # -----------------------------
        if 3.0 < t < 4.0:
            buffer.append(ft)

        if t >= 4.0 and bias is None and len(buffer) > 0:
            bias = [sum(x[i] for x in buffer) / len(buffer) for i in range(6)]
            print("Bias:", bias)

        # -----------------------------
        # bias 적용
        # -----------------------------
        if bias is not None:
            ft = [ft[i] - bias[i] for i in range(6)]

        q.put((t, ft))


if __name__ == "__main__":
    sensor = AFT20D15()
    q = queue.Queue()

    # -----------------------------
    # 그래프
    # -----------------------------
    N = 200
    buffers = [deque([0] * N, maxlen=N) for _ in range(6)]

    # Low-pass filter settings
    LOWPASS_ALPHA = 0.95  # smoothing factor: higher -> smoother (0..1)
    buffers_lowpass = [deque([0] * N, maxlen=N) for _ in range(6)]
    prev_filtered = [None] * 6

    plt.ion()
    fig, axs = plt.subplots(2, 3, figsize=(12, 6))

    titles = ["Fx", "Fy", "Fz", "Tx", "Ty", "Tz"]
    lines = []
    lines_lowpass = []

    force_ylim = (-5, 5)
    torque_ylim = (-0.1, 0.1)

    for i in range(6):
        ax = axs[i // 3][i % 3]
        (line,) = ax.plot(buffers[i], color="tab:blue", label="raw")
        (line_lp,) = ax.plot(
            buffers_lowpass[i], color="tab:red", linewidth=1, label="lowpass"
        )
        ax.set_title(titles[i])

        if i < 3:
            ax.set_ylim(force_ylim)
        else:
            ax.set_ylim(torque_ylim)

        lines.append(line)
        lines_lowpass.append(line_lp)

    # -----------------------------
    # Thread 시작
    # -----------------------------
    t = threading.Thread(target=data_thread, args=(sensor, q))
    t.daemon = True
    t.start()

    # -----------------------------
    # 루프
    # -----------------------------
    while not stop_flag:

        while not q.empty():
            _, ft = q.get()

            for i in range(6):
                # append raw
                buffers[i].append(ft[i])

                # compute and append low-pass filtered value
                prev = prev_filtered[i]
                filtered = low_pass_filter(prev, ft[i], alpha=LOWPASS_ALPHA)
                prev_filtered[i] = filtered
                buffers_lowpass[i].append(filtered)

        for i in range(6):
            lines[i].set_ydata(buffers[i])
            lines_lowpass[i].set_ydata(buffers_lowpass[i])

        plt.pause(0.001)

    # -----------------------------
    # 종료 처리
    # -----------------------------
    stop_flag = True  # ← 혹시 몰라서 한번 더
    t.join()  # 🔥 thread 완전히 종료 대기
    sensor.shutdown()
