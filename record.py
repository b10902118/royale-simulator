import cv2
from viewer import AndroidViewer

ADB_PATH = "/mnt/c/Users/CYB/AppData/Local/Android/Sdk/platform-tools/adb.exe"
# This will deploy and run server on android device connected to USB
android = AndroidViewer(adb_path=ADB_PATH)



while True:
    frames = android.get_next_frames()
    if frames is None:
        continue
    
    for frame in frames:
        cv2.imshow('game', frame)
        cv2.waitKey(1)