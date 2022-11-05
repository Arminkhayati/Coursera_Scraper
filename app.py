from flask import Flask
from flask import jsonify, url_for, render_template, redirect, request, make_response, send_from_directory
import uuid
from config import SAVE_DIR
from util import fetch_courses_by, course_category_decoder
import multiprocessing
from flask_executor import Executor
import json
from datetime import datetime
import os



app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
NUM_WORKERS = multiprocessing.cpu_count()
app.config['EXECUTOR_TYPE'] = 'thread'
app.config['EXECUTOR_MAX_WORKERS'] = NUM_WORKERS
executor = Executor(app)



@app.route('/', methods=['GET','POST'])
def index():
    if "courses_download_list" not in request.cookies.keys():
        resp = make_response(render_template('home.html'))
        resp.set_cookie("courses_download_list", json.dumps([]))
        return resp
    return render_template('home.html')

@app.route("/fetch_courses", methods=["GET", "POST"])
def fetch_courses():
    if request.method == "GET":
        if "courses_download_list" not in request.cookies.keys():
            resp = make_response(render_template('home.html'))
            resp.set_cookie("courses_download_list", json.dumps([]))
            return resp
    category = request.form["formCustomSelectCat"]
    if category == "Choose...":
        return render_template("not_selected.html")
    category = course_category_decoder(category)
    csv_file_name = str(uuid.uuid4())
    csv_file = csv_file_name + ".csv"
    executor.submit_stored(csv_file_name, fetch_courses_by, category, csv_file)
    csv_file_url = f"{request.host_url}download/" + csv_file

    courses_download_list = json.loads(request.cookies.get('courses_download_list'))
    course_download_item = {
        "category": category,
        "date": datetime.now().strftime("%d/%m/%y %H:%M:%S"),
        "csv_id": csv_file_name,
        "download_url": csv_file_url
    }
    courses_download_list.append(course_download_item)
    resp = make_response(redirect(url_for("download_list")))
    resp.set_cookie("courses_download_list", json.dumps(courses_download_list))
    return resp



@app.route('/downloadlist', methods=['GET'])
def download_list():
    courses_download_list = json.loads(request.cookies.get('courses_download_list'))
    json_resp = []
    for i in range(len(courses_download_list)):
        item = courses_download_list[i]
        csv_file = item["csv_id"] + ".csv"
        csv_file_path = os.path.join(SAVE_DIR, csv_file)
        if (not executor.futures.done(item["csv_id"])) and (not os.path.isfile(csv_file_path)):
            item["message"] = "Refresh again few minutes later, Still processing...."
            item["status"] = executor.futures._state(item["csv_id"])
            item.pop("download_url", 0)
        else:
            item["message"] = "Finished...."
            item["status"] = executor.futures._state(item["csv_id"])

        json_resp.append(item)

    return jsonify(json_resp), 200


@app.route('/download/<filename>', methods=['GET', 'POST'])
def download(filename):
    return send_from_directory(SAVE_DIR, filename)

@app.route('/restorecookies', methods=['GET'])
def restore_cookies():
    resp = make_response(render_template('home.html'))
    resp.set_cookie("courses_download_list", json.dumps([]))
    return resp

if __name__ == '__main__':
    app.run()





