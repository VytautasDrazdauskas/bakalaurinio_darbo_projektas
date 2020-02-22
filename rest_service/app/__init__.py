#!/usr/bin/python3
from flask import Flask
from flask import Blueprint
from flask_restful import Api
from app.resources.mqtt_service import MQTTPublishWithResponse

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Route
api.add_resource(MQTTPublishWithResponse, '/mqtt/publish-response')

app = Flask(__name__)

app.config['DEBUG'] = False
app.config['SECRET_KEY'] = '8a1wf-a846afw-vxxvf8-asfaf854'

app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=433)