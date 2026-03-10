from flask import Blueprint, jsonify

api_blueprint = Blueprint("api", __name__)

@api_blueprint.route("/hello")
def hello():
    return jsonify({
        "message": "Hello from Flask API!"
    })
