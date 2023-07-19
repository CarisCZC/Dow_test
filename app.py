import os
from flask import Flask, jsonify, render_template, request, url_for, send_from_directory, redirect
from werkzeug.utils import secure_filename
import zipfile

app = Flask(__name__)
IS_SERVERLESS = bool(os.environ.get('SERVERLESS'))


# 初始化上传临时目录
def init_upload_dir():
    UPLOAD_DIR = '/tmp/uploads' if IS_SERVERLESS else os.getcwd() + '/uploads'
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    app.config['UPLOAD_DIR'] = UPLOAD_DIR


init_upload_dir()


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def get_file():
    file = request.files['avatar']
    if file:
        filename = file.filename
        filePath = os.path.join(app.config['UPLOAD_DIR'], filename)
        file.save(filePath)
        ret = url_for("extract_files", filename=filePath)
        # return render_template('/extract', filename)
        return redirect(ret)


@app.route('/extract', methods=['GET'])
def extract_files():
    zip_filename = request.args.get('filename')
    if zip_filename:
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            zip_ref.extractall(path=app.config['UPLOAD_DIR'])
        extracted_files = zip_ref.namelist()
        return jsonify(extracted_files)
    else:
        return 'No filename provided.'


# 启动服务，监听 9000 端口，监听地址为 0.0.0.0
app.run(debug=IS_SERVERLESS != True, port=9000, host='0.0.0.0')