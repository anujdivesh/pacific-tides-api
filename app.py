from flask import Flask, Blueprint, jsonify, request
import controller
from app_service import AppService
import json
import os
app = Flask(__name__)
appService = AppService()

# Create a Blueprint with prefix `/tide`
tide_bp = Blueprint('tide', __name__, url_prefix='/tide')

# --- Define routes on the Blueprint (NOT directly on `app`) ---

@tide_bp.route('/<string:id>/<string:date>/<string:token>', methods=["GET"])
def get_game_by_id(id, date, token):
    game = controller.get_by_id(id, date, token)
    return jsonify(game)

@tide_bp.route('/countries', methods=["GET"])
def get_game_by_id2():
    game = controller.get_by_country()
    return jsonify(game)

@tide_bp.route('/TON/<string:id>/<string:date>/<string:token>', methods=["GET"])
def get_game_by_id3(id, date, token):
    game = controller.get_by_id_tonga(id, date, token)
    return jsonify(game)

@tide_bp.route('/VU/<string:id>/<string:date>/<string:token>', methods=["GET"])
def get_game_by_id4(id, date, token):
    game = controller.get_by_id_vanuatu(id, date, token)
    return jsonify(game)

@tide_bp.route('/WSM/<string:id>/<string:date>/<string:token>', methods=["GET"])
def get_game_by_id5(id, date, token):
    game = controller.get_by_id_samoa(id, date, token)
    return jsonify(game)

@tide_bp.route('/all/<string:id>/<string:date>/<string:enddate>/<string:token>', methods=["GET"])
def get_game_by_id_all(id, date, enddate, token):
    game = controller.get_by_id_all(id, date, enddate, token)
    return jsonify(game)
@tide_bp.route('/tidegauges', methods=["GET"])
def get_tide_gauges():
    json_path = os.path.join(os.path.dirname(__file__), 'tide_gauge.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
    return jsonify(data)
# --- Register the Blueprint ---
app.register_blueprint(tide_bp)

# --- Root route ---
@app.route('/')
def home():
    return "Internal Server Error Oceanx"

# --- CORS Handling ---
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@app.after_request
def after_request(response):
    return add_cors_headers(response)
