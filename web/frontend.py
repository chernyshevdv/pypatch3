import os
from flask import Flask, request

frontend = Flask(__name__)

@frontend.route("/")
def home():
    return 'Hello world'

@frontend.route("/deployment/new", methods=['GET'])
def show_new_deployment_form(id):
    pass

@frontend.route("/deployment", methods=['PUT'])
def deployment_create():
    pass

@frontend.route("/deployment/<id>", methods=['GET'])
def show_deployment_view(id):
    pass

@frontend.route("/deployment/edit/<id>", methods=['GET'])
def show_deployment_form(id):
    pass

@frontend.route("/deployment/update", methods=['POST'])
def update_deployment():
    pass

@frontend.route("/deployment/<id>", methods=['DELETE'])
def delete_deployment():
    pass


if __name__ == "__main__":
    frontend.run(
        host=os.environ.get("FRONTEND_HOST", "0.0.0.0"),
        port=os.environ.get("FRONTEND_PORT", "8080"),
        debug=os.environ.get("FRONTEND_DEBUG", True)
    )