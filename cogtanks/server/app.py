import os, copy, uuid, json
from subprocess import Popen, PIPE, STDOUT
from flask import Flask, request, redirect, url_for, render_template, Response, send_from_directory, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

TANK_DIR = "../engine/tanks"

#
# Helpers
#

def HTTP_SUCCESS(msg):
    return jsonify(
        {
            "message" : msg
        }
    ), 200

def HTTP_ERROR(msg, code="GENERIC_ERROR"):
    return jsonify(
        {
            "code" : code,
            "message" : msg
        }
    ), 400

#
# Classes
#
class TankEntry():
    def __init__(self, id=None):
        self.id = id
        
        if self.id is None:
            self.id = uuid.uuid4()
            self.new_entry()

        self.load_tank()

    def load_tank(self):
        """ Load tank data from database """
        pass

    def new_entry(self):
        """ Make a new entry in database """
        pass


#
# End Point Implementations
#

def _upload_tank(request):
    """
    @brief Upload new tank
    """
    if 'file' not in request.files or request.files['file'].filename == "":
        return HTTP_ERROR("missing file")

    if 'author' not in request.form or request.form['author'] == "":
        return HTTP_ERROR("missing author")

    file = request.files['file']
    author = request.form['author']

    if file:
        filename = secure_filename(file.filename)
        if filename.startswith("tank_") and filename.endswith(".py"):
            #file.save(os.path.join(TANK_DIR, filename))
            
            #cmd = 'python cogtanks.py --runs 10'
            #p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, cwd="../engine")
            #data = p.stdout.read()
            tank = {"id" : "12345"}
            return jsonify(tank)
        else:
            return HTTP_ERROR("bad file type")

    return HTTP_ERROR("unknown error")

def _get_tank(tank_id, request):
    """
    @brief Get message for a specific tank by id
    """
    tank = {}
    return jsonify(tank), 200

def _get_all_tanks(request):
    """
    @brief Return a list of all tanks
    """
    tanks = []
    return jsonify(tanks), 200

def _delete_tank(tank_id, request):
    """
    @brief Delete tank
    """
    tank = {}
    return jsonify(tank), 200

def _battle(request):
    """
    @brief Run a tank battle
    """

    # How many times to run?
    if 'runs' not in request.form or request.form['runs'] == "":
        return HTTP_ERROR("missing runs", "BAD_PARAM")
    
    # Which tanks to use?
    if 'tanks' not in request.form or request.form['tanks'] == "":
        return HTTP_ERROR("missing tank list", "BAD_PARAM")

    cmd = 'python cogtanks.py --runs 10'
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, cwd="../engine")
    output = p.stdout.read()

    return jsonify(json.loads(output)), 200

#
# Endpoints
#

@app.route('/api/tank/<tank_id>', methods=['DELETE'])
def delete_tank(tank_id):
    return _delete_tank(tank_id, request)

@app.route('/api/tank/<tank_id>', methods=['GET'])
def get_tank(tank_id):
    return _get_tank(tank_id, request)

@app.route('/api/upload/tank', methods=['POST'])
def upload_tank():
    return _upload_tank(request)

@app.route('/api/tanks', methods=['GET'])
def get_tanks():
    return _get_all_tanks(request)

@app.route('/api/battle', methods=['POST'])
def battle():
    return _battle(request)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return HTTP_ERROR("invalid endpoint")

if __name__ == "__main__":
    app.run(host="0.0.0.0")
