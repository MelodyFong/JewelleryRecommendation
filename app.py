from flask import Flask, request, render_template, send_from_directory

from werkzeug.utils import secure_filename

from fastai.vision import *
from fastai.callbacks.hooks import *

from scipy.spatial.distance import cosine

import os

import pandas as pd
import numpy as np

UPLOAD_FOLDER = 'static/upload_images/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# define function to hook into the fastai training process and save predictions
# for selected image after the bottleneck block (conv. before pooling)
# and after the second last linear layer (first layer with flattened 512
# outputs to 4 outputs in final linear layer)
def hooked_backward(image, model):
    m = model.model.eval()

    xb, _ = model.data.one_item(image)

    cat = int(model.predict(image)[1])

    with hook_output(m[-1][-5]) as hook_l:
        preds = m(xb)
        preds[0, int(cat)].backward()
    return hook_l


# define function to compute cosine similarity
def cosine_similarity(image, mejuri_products_data, model):
    # evaluate image and get output feature vector
    image_output = np.array(hooked_backward(image, model).stored[0])

    # compute cosine similarity for each image in dataframe
    similarity = mejuri_products_data.output.apply(lambda x: cosine(x, image_output))
    return similarity


@app.route('/', methods=('GET', 'POST'))
def home_page():
    # if server request pull, render form
    if request.method == 'GET':
        return render_template("extend1.html")  # render a template

    # if server request push, do this:
    if request.method == 'POST':
        # if submitted image not found in pushed files, return 'File not uploaded.'
        if 'fileToUpload' not in request.files:
            print('File not uploaded.')
            return
        # else, request submitted image, save submitted image and classify
        file = request.files['fileToUpload']

        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image = open_image(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # get Mejuri feature vectors
        mejuri_products_data = pd.read_csv('mejuri_products_data.csv')
        mejuri_products_data['output'] = mejuri_products_data.output.apply(lambda x: np.fromstring(x[1:-1],
                                                                                                   sep=' '))

        # load model
        model = load_learner('.','cnn50.pkl')

        # compute similarity for image
        mejuri_products_data['similarity'] = cosine_similarity(image,
                                                               mejuri_products_data,
                                                               model)

        # get top 3 most similar items in Mejuri product catalogue
        mejuri_products_data = mejuri_products_data.sort_values(by='similarity',
                                                                ascending=False).reset_index(drop=True)

        # render results page
        return render_template("extend2.html",
                               filename=filename,
                               similarimages=mejuri_products_data)


@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)