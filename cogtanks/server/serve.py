import waitress
import app

waitress.serve(app.app, port=5000, threads=4)
