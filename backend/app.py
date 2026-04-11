from flask import Flask, send_from_directory
from config import Config
from database.db import db
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dash_bp
from flask_cors import CORS
import os

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)
from flask_cors import CORS
CORS(app)

app.register_blueprint(auth_bp)
app.register_blueprint(dash_bp)

@app.route('/')
def index():
    return send_from_directory('../frontend', 'login.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('../frontend', filename)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)