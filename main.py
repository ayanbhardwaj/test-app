from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from PIL import Image
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG"]


def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb


def color_pct_check(file_name):
    path = os.path.join('static', 'images', f'{file_name}')
    np_image = cv2.imread(path)
    counter = {}
    for i in np_image[0]:
        if str(i) not in counter:
            counter[str(i)] = 1
        else:
            counter[str(i)] += 1
    sorted_counter = {k: v for k, v in sorted(counter.items(), key=lambda item: item[1], reverse=True)}
    colors_list = [list(sorted_counter.keys())[:20], list(sorted_counter.values())[:20]]

    top_20_colors = []
    for n in range(len(colors_list[0])):
        x = colors_list[0][n][1:-1].split(' ')
        while '' in x:
            x.remove('')
        for i in range(len(x)):
            x[i] = int(x[i])
        top_20_colors.append([f'#{rgb_to_hex(tuple(x))}',
                              round((colors_list[1][n]) * 100 / (sum(sorted_counter.values())), 6)])
    data = {}
    for n in range(0, len(top_20_colors)):
        data[top_20_colors[n][0]] = top_20_colors[n][1]
    return data


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
    data_dict = color_pct_check(file_name="home.jpg")
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
    data_dict = color_pct_check(file_name=file)
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