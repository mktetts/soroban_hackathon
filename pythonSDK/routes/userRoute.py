import sys
sys.dont_write_bytecode = True

from flask import Blueprint

from pythonSDK.controllers.userController import borrow, check, deploy, initialize, get_balance, chat, lend
 

user = Blueprint('user', __name__)

user.route("/check", methods = ["POST"])(check)
user.route("/deploy", methods = ["POST"])(deploy)
user.route("/initialize", methods = ["POST"])(initialize)
user.route("/getBalance", methods = ["POST"])(get_balance)
user.route("/chat", methods = ["POST"])(chat)
user.route("/borrow", methods = ["POST"])(borrow)
user.route("/lend", methods = ["POST"])(lend)






