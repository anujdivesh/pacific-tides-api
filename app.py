from flask import Flask, Blueprint, jsonify, request
import controller
import api
from app_service import AppService
import json
import os
app = Flask(__name__)
# Preserve dict insertion order in JSON responses (don't sort keys alphabetically).
app.config['JSON_SORT_KEYS'] = False
app.json.sort_keys = False
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

@tide_bp.route('/countries/updates', methods=["GET"])
def get_countries_with_updates():
    game = controller.get_countries_with_updates()
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

@tide_bp.route('/NU/<string:id>/<string:date>/<string:token>', methods=["GET"])
def get_game_by_id6(id, date, token):
    game = controller.get_by_id_niue(id, date, token)
    return jsonify(game)

@tide_bp.route('/all/<string:id>/<string:date>/<string:enddate>/<string:token>', methods=["GET"])
def get_game_by_id_all(id, date, enddate, token):
    game = controller.get_by_id_all(id, date, enddate, token)
    return jsonify(game)

@tide_bp.route('/predictions', methods=["GET"])
def get_tide_predictions():
    station_no = request.args.get('stn_num')
    start = request.args.get('start_time')
    end = request.args.get('end_time')
    if not station_no or not start or not end:
        return jsonify({"Error": "stn_num, start_time and end_time are required"}), 400
    predictions = controller.get_tide_predictions(station_no, start, end)
    return jsonify(predictions)

@tide_bp.route('/tidegauges', methods=["GET"])
def get_tide_gauges():
    json_path = os.path.join(os.path.dirname(__file__), 'tide_gauge.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
    return jsonify(data)

@tide_bp.route('/country_mapper', methods=["POST"])
def add_country_mapper():
    if not api.verify_token(request.headers.get('X-Secret-Token')):
        return jsonify({"Error": "Unauthorized"}), 401
    result, status = api.add_country_mapper(request.get_json(silent=True) or {})
    return jsonify(result), status

@tide_bp.route('/country_mapper/<string:station_id>', methods=["PUT"])
def update_country_mapper(station_id):
    if not api.verify_token(request.headers.get('X-Secret-Token')):
        return jsonify({"Error": "Unauthorized"}), 401
    result, status = api.update_country_mapper(station_id, request.get_json(silent=True) or {})
    return jsonify(result), status

@tide_bp.route('/tides', methods=["POST"])
def add_tide():
    if not api.verify_token(request.headers.get('X-Secret-Token')):
        return jsonify({"Error": "Unauthorized"}), 401
    result, status = api.add_tide(request.get_json(silent=True) or {})
    return jsonify(result), status

@tide_bp.route('/tides/<string:station_id>', methods=["DELETE"])
def delete_tide(station_id):
    if not api.verify_token(request.headers.get('X-Secret-Token')):
        return jsonify({"Error": "Unauthorized"}), 401
    result, status = api.delete_tide(
        station_id,
        request.args.get('end_date'),
        request.args.get('direction', 'before'),
    )
    return jsonify(result), status

@tide_bp.route('/realtime-endpoints', methods=["GET"])
def get_realtime_endpoints():
    return jsonify({
        "realtime-sealevel-station-api":
            "https://sea-level-dev.cosppac.cloud//api/stations/",
        "realtime-sealevel-predictions-api":
            "https://sea-level-dev.cosppac.cloud//api/tide_predictions/?start_time={date_time_start}&end_time={date_time_end}&stn_num={station_no}",
        "realtime-sealevel-data-api":
            "https://sea-level-dev.cosppac.cloud//api/get_obs?start_time={date_time_start}&end_time={date_time_end}&stn_num={station_no}&step=1",
    })

@tide_bp.route('/predictions', methods=["POST"])
def add_tide_prediction():
    if not api.verify_token(request.headers.get('X-Secret-Token')):
        return jsonify({"Error": "Unauthorized"}), 401
    result, status = api.add_tide_prediction(request.get_json(silent=True) or {})
    return jsonify(result), status

@tide_bp.route('/predictions/<string:station_no>', methods=["DELETE"])
def delete_tide_prediction(station_no):
    if not api.verify_token(request.headers.get('X-Secret-Token')):
        return jsonify({"Error": "Unauthorized"}), 401
    result, status = api.delete_tide_prediction(
        station_no,
        request.args.get('end_date'),
        request.args.get('direction', 'before'),
    )
    return jsonify(result), status

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
