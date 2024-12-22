from ultralytics import YOLO
from glob import glob

# Load a model
model = YOLO("./runs/detect/train28/weights/best.pt")  # pretrained YOLO11n model

# Run batched inference on a list of images
results = model(
    glob("/tmp2/img/12-21-01-11-36/*.png"), conf=0.6
)  # return a list of Results objects

# Process results list
for i, result in enumerate(results):
    boxes = result.boxes  # Boxes object for bounding box outputs
    # masks = result.masks  # Masks object for segmentation masks outputs
    # keypoints = result.keypoints  # Keypoints object for pose outputs
    probs = result.probs  # Probs object for classification outputs

    # obb = result.obb  # Oriented boxes object for OBB outputs
    # result.show()  # display to screen
    result.save(filename=f"result/{i}.png")  # save to disk
