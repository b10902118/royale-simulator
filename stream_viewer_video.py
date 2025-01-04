import subprocess
import os
import cv2
import time
import numpy as np
import random
import scrcpy
import signal
import sys
from datetime import datetime
from ultralytics import YOLO
import tkinter as tk
from PIL import Image, ImageTk

# Ensure this module is installed and properly configured

# Paths and configurations
EMULATOR_PATH = "C://Users/CYB/AppData/Local/Android/Sdk/emulator/emulator.exe"
# ADB_PATH = "C://Users/CYB/AppData/Local/Android/Sdk/platform-tools/adb.exe"
ADB_PATH = "C:/Users/CYB/tst_py/py-android-viewer/scrcpy/adb.exe"
SCRCPY_JAR = "C://Users/CYB/py-android-viewer/scrcpy-server.jar"
VIDEO_OUTPUT_PATH = "C://Users/CYB/emulator_screen_recording.mp4"
AVD_NAME = "Pixel_7_Pro_API_30"


def perform_swipe(f_x, f_y, t_x, t_y, device_id):
    """Performs a swipe gesture on the emulator screen."""
    print(f"Performing swipe from ({f_x}, {f_y}) to ({t_x}, {t_y})...")
    swipe_cmd = [
        ADB_PATH,
        "-s",
        device_id,
        "shell",
        "input",
        "swipe",
        str(f_x),
        str(f_y),
        str(t_x),
        str(t_y),
    ]
    subprocess.run(swipe_cmd, check=True, text=True)
    print("Swipe gesture performed.")


def perform_tap(x, y, device_id):
    """Performs a tap gesture on the emulator screen."""
    print(f"Performing tap at ({x}, {y})...")
    tap_cmd = [ADB_PATH, "-s", device_id, "shell", "input", "tap", str(x), str(y)]
    subprocess.run(tap_cmd, check=True, text=True)
    print("Tap gesture performed.")


def detect_resolution():
    """Detects the screen resolution."""
    print("Detecting screen resolution...")
    try:
        result = subprocess.run(
            [ADB_PATH, "shell", "wm", "size"], stdout=subprocess.PIPE, text=True
        )
        resolution = result.stdout.strip().split(": ")[1]
        return map(int, resolution.split("x"))
    except Exception as e:
        print(f"Failed to detect resolution: {e}")
        return (1920, 1080)


ADB_PATH = "C://Users/CYB/AppData/Local/Android/Sdk/platform-tools/adb.exe"
tensor_cards = [[400, 2500], [700, 2500], [1000, 2500], [1300, 2500]]
x = [
    146,
    218,
    290,
    360,
    434,
    506,
    578,
    650,
    722,
    794,
    866,
    938,
    1010,
    1082,
    1154,
    1226,
    1298,
    1370,
]
y = [
    352,
    409,
    467,
    524,
    582,
    639,
    697,
    754,
    812,
    869,
    927,
    984,
    1042,
    1099,
    1157,
    1157,
    1342,
    1342,
    1400,
    1457,
    1515,
    1572,
    1630,
    1687,
    1745,
    1802,
    1860,
    1917,
    1975,
    2032,
    2090,
    2147,
]
spell_on_tower = [
    [[360, 697]],
    [[1082, 697]],
    [[722, 467], [722, 524], [794, 467], [794, 524]],
]

recording = False
# output_dir = f"./img/{datetime.now().strftime('%m-%d-%H-%M-%S')}"
# os.makedirs(output_dir)


def put_card(n, gx, gy, device_id):
    perform_tap(tensor_cards[n][0], tensor_cards[n][1], device_id)
    perform_tap(x[gx], y[gy], device_id)


def main():
    global recording

    def signal_handler(sig, frame):
        print("Exiting...")
        client.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    device1 = "emulator-5554"
    device2 = "emulator-5556"
    client = scrcpy.Client(
        device=device1,
        # flip=self.ui.flip.isChecked(),
        bitrate=1000000000,
        # encoder_name=encoder_name,
        max_fps=10,
    )

    print("Loading model...")
    model = YOLO("../detector/last.pt")

    root = tk.Tk()
    root.title("Model Prediction")
    root.geometry("500x800")

    # Create a Label to display the image
    label = tk.Label(root)
    label.pack()

    def update_image(frame):
        # Convert the frame to an image
        image = Image.fromarray(frame)
        image_tk = ImageTk.PhotoImage(image)

        # Update the Label with the new image
        label.config(image=image_tk)
        label.image = image_tk

    def on_frame(frame):
        # global recording
        # if not hasattr(on_frame, "frame_count"):
        #    on_frame.frame_count = 0
        # if frame is not None:
        #    print(frame.shape) #(2560, 1152, 3)
        # print(recording)

        # if recording:
        #    # Save the frame as an image file
        #    try:
        #        cv2.imwrite(f"{output_dir}/frame_{on_frame.frame_count}.png", frame)
        #        on_frame.frame_count += 1
        #        if on_frame.frame_count >= 1800:
        #            recording = False
        #    except Exception as e:
        #        pass
        if frame is not None:
            try:
                input_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                input_img = input_img[120:1850, :]

                result = model(input_img, conf=0.8)
                # print(f"{type(result)=}")
                pred_img = result[0].plot()
                pred_img = cv2.resize(pred_img, (400, 600))
                # print(type(pred_img))
                update_image(pred_img)
            except Exception as e:
                print(f"Failed to process frame: {e}")
                pass

    client.add_listener(scrcpy.EVENT_FRAME, on_frame)
    client.start(threaded=True)

    # perform_swipe(540, 2000, 540, 500, device_id)
    # perform_tap(700, 1750, device_id)
    # time.sleep(18)
    # process = subprocess.Popen(
    #    ["python", "test.py"],  # Just run python test.py, no need for PowerShell and cd
    #    shell=True,
    #    stdin=subprocess.PIPE,
    #    text=True,
    #    cwd="C:/Users/CYB/tst_py/sq_CR_sim",  # Set the correct directory
    # )

    # perform_tap(700, 2500, device_id)
    perform_tap(700, 1750, device1)
    perform_tap(700, 1750, device2)
    time.sleep(7)

    start_time = time.time()
    interval = 0
    recording = False

    # process.communicate(input="Hello from script1!\n")
    # while time.time() - start_time < 180:

    # random_number = random.randint(0, 3)
    # rand_x = random.randint(0, len(x) - 1)
    # rand_y = random.randint(0, 15)
    put_card(0, 9, 25, device1)
    put_card(0, 9, 25, device2)

    input_data = "Giant 9 25 Musketeer 9 6\n"
    print(f"Sending input to subprocess: {input_data}")
    # process.stdin.write(input_data)
    # process.stdin.flush()

    # stdout_line = process.stdout.readline()
    # stderr_line = process.stderr.readline()
    # if stdout_line:
    #     print(f"Subprocess Output: {stdout_line}")
    # if stderr_line:
    #     print(f"Subprocess Error: {stderr_line}")

    # time.sleep(5)

    # interval += 1
    # time.sleep(5)

    # process frames

    print("Done")
    root.mainloop()
    time.sleep(180)
    # process.terminate()
    # process.wait()
    client.stop()
    exit(0)
    return


if __name__ == "__main__":
    main()

    # Auto chest opening
    # while True:
    #     perform_tap(200, 2700, device_id)
    #     perform_swipe(540, 2000, 540, 500, device_id)
    #     perform_tap(x[12], y[10], device_id)
    #     perform_tap(700, 1750, device_id)

    #     for i in range(0,15):
    #         perform_tap(x[12], y[10], device_id)
    #         # time.sleep(1)
    #         i+=1
    #     time.sleep(1)
    #     perform_tap(x[12], y[10], device_id)
