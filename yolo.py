from ultralytics import YOLO

# Load a model
model = YOLO("last_50.pt")  # load a pretrained model (recommended for training)

# Train the model
results = model.train(data="./data.yaml", epochs=2000, imgsz=640, batch=64, lr0=3e-5)
