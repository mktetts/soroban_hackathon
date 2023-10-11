import sys
sys.dont_write_bytecode = True

from flask import Flask
import os
from flask_cors import CORS
from pythonSDK.utils.error import Error



from pythonSDK.routes.userRoute import user


app = Flask(__name__)

app.config['JSON_SORT_KEYS'] = False

app.register_blueprint(user, url_prefix = '/api')

CORS(app)

@app.errorhandler(404)
def handle_404(e):
    return Error("Failed", "URL not found", 404)

@app.route('/')
def index():
    return "Welcome to Flask"

if __name__ == '__main__':
    app.debug = True
    app.run()