from flask import Flask
from flask_cors import CORS
from app.routes.counselor_routes import counselor_init_routes

def create_app():
    app = Flask(__name__)
    CORS(app)
    counselor_init_routes(app)
    return app