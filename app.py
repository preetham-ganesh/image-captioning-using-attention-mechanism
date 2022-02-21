# authors_name = 'Preetham Ganesh'
# project_title = 'Captioning of Images using Attention Mechanism'
# email = 'preetham.ganesh2015@gmail.com'


import os
import logging

import tensorflow as tf
import numpy as np
import cv2
from flask import Flask
from flask import request
from flask import render_template
from flask import send_from_directory

from codes.sentence_prediction import predict_caption
from codes.data_preprocessing import preprocess_image
from codes.utils import load_json_file


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.getLogger('tensorflow').setLevel(logging.FATAL)
physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_visible_devices(physical_devices[0], 'GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], enable=True)

app = Flask(__name__)
app_root_directory = os.path.dirname(os.path.abspath(__file__))


@app.route('/upload/<filename>')
def send_image(filename: str):
    """Sends saved image from directory using uploaded image filename.

    Args:
        filename: A string which contains the filename for the uploaded image.

    Returns:
        Saved image from directory.
    """
    return send_from_directory('data/images', filename)


@app.route("/")
def index():
    """Renders template for index page.

    Args:
        None.

    Returns:
        Rendered template for the index page.
    """
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
