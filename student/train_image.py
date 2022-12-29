import json
import os
from json import JSONEncoder

import cv2 as cv
import face_recognition as fr
import numpy as np
from django.conf import settings

from student.models import Student


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


def get_student(user_id):
    return Student.objects.filter(user_id=user_id)


def encode_image(img_dir):
    face = fr.load_image_file(img_dir)
    encoding = fr.face_encodings(face)
    if len(encoding):
        img = img_dir.split('\\')[-1]
        without_ext = img.split('.')[0]
        user_id = without_ext.split('_')[0]
        data = {user_id: encoding[0]}

        info = os.path.join(
            settings.BASE_DIR,
            'static\json',
            f'{user_id}.json'
        )

        with open(info, 'w') as out:
            json.dump(data, out, cls=NumpyArrayEncoder)

        # jsonFile = open(info, 'r')
        # inp = json.load(jsonFile)
        # print(inp.get(user_id, []))
        # print(inp[user_id])

def get_encoded_faces(user_id):
    info = os.path.join(
        settings.BASE_DIR, 'static\json', f'{user_id}.json')
    jsonFile = open(info, 'r')
    return json.load(jsonFile)


