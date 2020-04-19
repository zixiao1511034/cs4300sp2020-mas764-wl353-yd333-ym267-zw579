# Gevent needed for sockets
from gevent import monkey
monkey.patch_all()

# Imports
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_cors import CORS
import os
import sys
dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(dir, '../connect_api')))
from api_combined import IRApi

# Configure app
socketio = SocketIO()
app = Flask(__name__)
CORS(app)
app.config.from_object(os.environ["APP_SETTINGS"])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# DB
db = SQLAlchemy(app)

# Import + Register Blueprints
from app.accounts import accounts as accounts
app.register_blueprint(accounts)
from app.irsystem import irsystem as irsystem
app.register_blueprint(irsystem)

# Initialize app w/SocketIO
socketio.init_app(app)

# Our search route. It returns JSON and is called by the front-end
# TODO: add filters as an arg
# Example search- http://localhost:5000/search?city=Tampa&topics=park
@app.route('/search', methods=['GET'])
def get_results():
    city = request.args.get('city') if 'city' in request.args else "Tampa"
    topic = request.args.get('topics') if 'topics' in request.args else "garden"
    IR = IRApi(city, topic)
    places_JSON = IR.get_rank_places()
    return jsonify(places_JSON)

# HTTP error handling
@app.errorhandler(404)
def not_found(error):
  return render_template("404.html"), 404
