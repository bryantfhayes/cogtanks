import os, copy, uuid, json, threading, sys, signal, queue, shutil
from subprocess import Popen, PIPE, STDOUT
from flask import Flask, request, redirect, url_for, render_template, Response, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from tinydb import TinyDB, Query

app = Flask(__name__)
db = TinyDB('db.json')
q = queue.Queue()
db_writer = None

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
TANK_DIR = "uploads"

#
# Helpers
#

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    if db_writer is not None:
        db_writer.running = False
        db_writer.join()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

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
class DBWriter(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True

    def run(self):
        while self.running:
            try:
                entry = q.get(timeout=1)
            except queue.Empty:
                pass
            else:
                db.insert(entry)

db_writer = DBWriter()
db_writer.setName('DBWriter Thread')
db_writer.start()

#
# End Point Implementations
#

def _upload_tank(request, id=None):
    """
    @brief Upload new tank
    """
    print(request.get_data().decode("utf-8"))
    if 'file' not in request.files or request.files['file'].filename == "":
        return HTTP_ERROR("missing file")

    if 'author' not in request.form or request.form['author'] == "":
        return HTTP_ERROR("missing author")

    file = request.files['file']
    author = request.form['author']

    if file:
        filename = secure_filename(file.filename)
        if filename.startswith("tank_") and filename.endswith(".py"):
            name = filename[5:-3].capitalize()
            path = os.path.join(TANK_DIR, filename)
            if id is None:
                id = str(uuid.uuid4())

            # If a file at this path already exists, fail
            if len(db.search(Query().path == path)):
                return HTTP_ERROR("that tank already exisits, try PUT instead")
            
            file.save(path)
            tank = {"id" : id, "author" : author, "path" : path, "name" : name}
            q.put(tank)
            return jsonify(tank)
        else:
            return HTTP_ERROR("bad file type")

    return HTTP_ERROR("unknown error")

def _get_tank(tank_id, request):
    """
    @brief Get message for a specific tank by id
    """
    Tank = Query()
    result = db.search(Tank.id == tank_id)
    if len(result) > 0:
        return jsonify(result[0]), 200
    return HTTP_ERROR("tank not found")

def _get_all_tanks(request):
    """
    @brief Return a list of all tanks
    """
    return jsonify(db.all()), 200

def _delete_tank(tank_id, request):
    """
    @brief Delete tank
    """
    Tank = Query()
    result = db.search(Tank.id == tank_id)
    if len(result) > 0:
        db.remove(Tank.id == tank_id)
        return jsonify(result[0]), 200
    else:
        return HTTP_ERROR("no tank with that id")

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

    # Make a staging directory for battling tanks
    tmpdir = "/tmp/{}".format(uuid.uuid4())
    os.makedirs(tmpdir)

    runs = request.form["runs"]
    tanks = request.form["tanks"].strip('][').split(', ') 

    # For each indicated Tank, copy file to tmpdir
    Tank = Query()
    for tank_id in tanks:
        results = db.search(Tank.id == tank_id)
        if len(results) <= 0:
            # Tank not found!
            return HTTP_ERROR("no tank with id: {}".format(tank_id))
        else:
            shutil.copy(results[0]["path"], tmpdir)

    # Run simulation
    cmd = 'python cogtanks.py --runs {0} --tank_dir {1}'.format(runs, tmpdir)
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, cwd="../engine")
    output = p.stdout.read()

    tickdata_path = os.path.join(tmpdir, "tickdata.json")
    if os.path.exists(tickdata_path) == False:
        return HTTP_ERROR("no tick data found")

    with open(tickdata_path) as fp:
        tickdata = json.load(fp)

    # Remove temporary working directory
    shutil.rmtree(tmpdir)

    # Add stats to normal game data
    tickdata["stats"] = json.loads(output)

    return jsonify(tickdata), 200

def _put_tank(tank_id, request):
    """
    @brief Update an existing tank
    """
    if len(db.search(Query().id == tank_id)) <= 0:
        return HTTP_ERROR("tank not found")
    else:
        _delete_tank(tank_id, request)
        return _upload_tank(request, tank_id)

#
# Endpoints
#

@app.route('/api/tank/<tank_id>', methods=['DELETE'])
def delete_tank(tank_id):
    return _delete_tank(tank_id, request)

@app.route('/api/tank/<tank_id>', methods=['GET'])
def get_tank(tank_id):
    return _get_tank(tank_id, request)

@app.route('/api/tank/<tank_id>', methods=['PUT'])
def put_tank(tank_id):
    return _put_tank(tank_id, request)

@app.route('/api/tank', methods=['POST'])
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
