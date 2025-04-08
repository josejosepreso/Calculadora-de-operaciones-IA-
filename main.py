from flask import Flask, render_template, request, jsonify, redirect
from TestV2 import main as predict

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return jsonify(predict(request.json['img_name']))
    
    return render_template("test.html")
