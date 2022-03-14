from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.utils import secure_filename
import numpy as np
import pandas as pd
import cv2
import os
from hexcodes import colors


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG"]


def color_pct_check(file_name):
    path = os.path.join('static', 'images', f'{file_name}')
    img = cv2.imread(path)
    diff = 20
    keys = {}
    for (key, value) in colors.items():
        boundaries = [([value[2] - diff, value[1] - diff, value[0] - diff],
                       [value[2] + diff, value[1] + diff, value[0] + diff])]

        for (lower, upper) in boundaries:
            lower = np.array(lower, dtype=np.uint8)
            upper = np.array(upper, dtype=np.uint8)
            mask = cv2.inRange(img, lower, upper)
            output = cv2.bitwise_and(img, img, mask=mask)

            ratio_col = cv2.countNonZero(mask) / (img.size / 3)
            keys[key] = np.round(ratio_col * 100, 6)
    df = pd.DataFrame.from_dict(data=keys, orient='index')
    new_df = df.sort_values(0, ascending=False)
    new_df.rename(columns={0:'percentage'}, inplace=True)
    return new_df[:10]


def allowed_image(file_name):
    if not "." in file_name:
        return False
    ext = file_name.split(".")[1]
    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


@app.route("/", methods=['GET', 'POST'])
def home():
    data = color_pct_check(file_name="home.jpg")
    data_dict = data.to_dict()['percentage']
    if request.method == 'POST':
        if request.files:
            # get file item
            image = request.files['image']
            # get base filename
            name = image.filename
            if name == '':
                flash("No Filename")
            if allowed_image(name):
                filename = secure_filename(name)
                ext = ext = filename.split(".")[1]
                new_filename = f'photo.{ext}'
                # save image in static folder
                image.save(os.path.join('static', 'images', new_filename))
                return redirect(url_for('result', file=new_filename))
            else:
                flash("File extension is not allowed")
    return render_template("index.html", data=data_dict)


@app.route("/result/<file>", methods=['GET', 'POST'])
def result(file):
    data = color_pct_check(file_name=file)
    data_dict = data.to_dict()['percentage']
    path = f'images/{file}'
    if request.method == 'POST':
        if request.files:
            # get file item
            image = request.files['image']
            # get base filename
            name = image.filename
            if name == '':
                flash("No Filename")
            if allowed_image(name):
                filename = secure_filename(name)
                ext = ext = filename.split(".")[1]
                new_filename = f'photo.{ext}'
                # save image in static folder
                image.save(os.path.join('static', 'images', new_filename))
                return redirect(url_for('result', file=new_filename))
            else:
                flash("File extension is not allowed")
    return render_template("result.html", path=path, data=data_dict)


if __name__ == '__main__':
    app.run(debug=True)