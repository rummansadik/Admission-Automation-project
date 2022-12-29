import os

import cv2
import numpy as np
from django.conf import settings
from PIL import Image

static_dir = os.path.join(
    settings.BASE_DIR, 'static', 'profile_pic', 'Student')

def generate(id):
    print("generating -------------")
    imgPath = os.path.join(static_dir, str(id))

    paths = []
    ids = []

    for image in os.listdir(imgPath):
        imgName = image.split('_')
        if(len(imgName) > 1):
            if(imgName[0] == str(id)):
                path = os.path.join(imgPath, image)
                paths.append(path)
                

    faces = []
    for path in paths:
        image = Image.open(path).convert("L")
        imgNp = np.array(image, 'uint8')
        faces.append(imgNp)
        ids.append(id)

    ids = np.array(ids)
    trainer = cv2.face.LBPHFaceRecognizer_create()
    trainer.train(faces, ids)

    training_file = os.path.join(
        imgPath,
        "training.yml"
    )
    
    trainer.write(training_file)
