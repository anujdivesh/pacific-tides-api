from flask import Flask, jsonify, request
import controller
from app_service import AppService

app = Flask(__name__)
appService = AppService();

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'  # Allow all origins (you can specify a particular origin here)
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'  # Allowable HTTP methods
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'  # Allowed headers
    return response

@app.route('/')
def home():
    return "Internal Server Error"

@app.route("/tide/<string:id>/<string:date>/<string:token>", methods=["GET"])
def get_game_by_id(id,date,token):
    game = controller.get_by_id(id,date,token)
    return jsonify(game)


@app.route("/tide/countries", methods=["GET"])
def get_game_by_id2():
    game = controller.get_by_country()
    return jsonify(game)


@app.route("/tide/TON/<string:id>/<string:date>/<string:token>", methods=["GET"])
def get_game_by_id3(id,date,token):
    game = controller.get_by_id_tonga(id,date,token)
    return jsonify(game)

@app.route("/tide/VU/<string:id>/<string:date>/<string:token>", methods=["GET"])
def get_game_by_id4(id,date,token):
    game = controller.get_by_id_vanuatu(id,date,token)
    return jsonify(game)

@app.route("/tide/WSM/<string:id>/<string:date>/<string:token>", methods=["GET"])
def get_game_by_id5(id,date,token):
    game = controller.get_by_id_samoa(id,date,token)
    return jsonify(game)

@app.route("/tide/all/<string:id>/<string:date>/<string:enddate>/<string:token>", methods=["GET"])
def get_game_by_id_all(id,date,enddate,token):
    game = controller.get_by_id_all(id,date,enddate,token)
    return jsonify(game)

@app.after_request
def after_request(response):
    # Apply CORS headers to all responses
    return add_cors_headers(response)
