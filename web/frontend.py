import os
from flask.helpers import make_response
import requests
from flask import Flask, request, render_template, jsonify, json, redirect
from werkzeug.datastructures import Headers

JSON_HEADERS = {"Content-type": "application/json"}
DEPLOYMENT_HOST = os.environ.get("DEPLOYMENT_HOST", "localhost")
DEPLOYMENT_PORT = os.environ.get("DEPLOYMENT_PORT", "5000")
DEPLOYMENT_URL_BASE = f"http://{DEPLOYMENT_HOST}:{DEPLOYMENT_PORT}"
DEPLOYMENT_URL_CREATE = f"{DEPLOYMENT_URL_BASE}/deployment"
DEPLOYMENT_URL_UPDATE = DEPLOYMENT_URL_CREATE
DEPLOYMENT_URL_LIST = f"{DEPLOYMENT_URL_BASE}/deployment/list"

frontend = Flask(__name__)

@frontend.route("/")
def home():
    return 'Hello world'

@frontend.route("/deployment/new", methods=['GET'])
def show_new_deployment_form():
    return render_template('new_deployment.j2')

@frontend.route("/deployment/new", methods=['POST'])
def deployment_create():
    l_data = {}
    for key in ['title', 'excel_columns', 'excel_header_row']:
        l_data[key] = request.form[key]
    l_data_json = json.dumps(l_data)
    print(f"JSON data: {l_data_json}")
    l_creation_response = requests.put(DEPLOYMENT_URL_CREATE, json=l_data_json, headers=JSON_HEADERS)
    l_resp_json = l_creation_response.json()
    l_id = l_resp_json['id']

    return redirect(f"/deployment/{l_id}")


@frontend.route("/deployment/<id>", methods=['GET'])
def show_deployment_view(id):
    l_url = f"{DEPLOYMENT_URL_BASE}/deployment/{id}"
    l_api_response = requests.get(l_url)
    
    return render_template('view_deployment.j2', obj=l_api_response.json())

@frontend.route("/deployment/edit/<id>", methods=['GET'])
def show_deployment_form(id):
    l_url = f"{DEPLOYMENT_URL_BASE}/deployment/{id}"
    l_api_response = requests.get(l_url)

    return render_template('edit_deployment.j2', obj=l_api_response.json())

@frontend.route("/deployment/update", methods=['POST'])
def update_deployment():
    l_data = {}
    for key in ['id', 'title', 'excel_columns', 'excel_header_row']:
        l_data[key] = request.form[key]
    l_data_json = json.dumps(l_data)
    print(f"Going to send the following JSON: {l_data_json}")
    l_update_response = requests.post(DEPLOYMENT_URL_UPDATE, json=l_data_json, headers=JSON_HEADERS)
    l_resp_json = l_update_response.json()
    print(l_resp_json)
    if l_resp_json['success']:
        l_id = l_resp_json['id']
        return redirect(f"/deployment/{l_id}")
    else:
        return f"Error {l_resp_json['error']}"    

@frontend.route("/deployment/delete/<id>", methods=['POST'])
def delete_deployment():
    pass

@frontend.route("/deployment/list", methods=['GET'])
def list_deployments():
    l_api_reponse = requests.get(DEPLOYMENT_URL_LIST)
    l_resp_json = l_api_reponse.json()
    # l_obj = json.loads(l_resp_json)
    return render_template('deployment_list.j2', obj=l_resp_json)

if __name__ == "__main__":
    frontend.run(
        host=os.environ.get("FRONTEND_HOST", "0.0.0.0"),
        port=os.environ.get("FRONTEND_PORT", "8080"),
        debug=os.environ.get("FRONTEND_DEBUG", True)
    )