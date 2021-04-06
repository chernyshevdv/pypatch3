import os
import sqlite3
from types import resolve_bases
from flask import Flask, jsonify, request, redirect, g
from requests.api import get
import json

deployment = Flask(__name__)

def get_db():
    """
    Opens DB connection if it's not open yet
    """
    if not hasattr(g, 'db_conn'):
        g.db_conn = sqlite3.connect("pypatch.sqlite")
        g.db_conn.row_factory = sqlite3.Row
    
    return g.db_conn

@deployment.route('/deployment/<id>', methods=['GET'])
def read(id):
    """ Retrieve a deployment by ID
    ---
    get:
        summary: retrieve a deployment by ID
        parameters:
            - name: id
              in: path
              description: deployment ID
              type: integer
              required: true
        responses:
            200:
                description: OK. record found
                schenma:
                    success: true
                    deployment:
                        id: 4
                        title: "my deployment"
                        excel_columns: "A,B,C"
                        excel_header_row: 0
            404:
                description: Error. Deployment with this ID is not found
                schema:
                    - success: False
                    - error: Deployment 1 is not found
    """
    m_sql = "SELECT * FROM deployment WHERE id=:id"
    m_rs = get_db().execute(m_sql, {"id": id}).fetchone()
    if m_rs is None:
        return jsonify(success=False, error=f"Deployment {id} is not found"), 404
    else:
        m_ret = {'success': True}
        m_ret['deployment'] = dict(m_rs)
        return jsonify(m_ret)

@deployment.route('/deployment', methods=['PUT'])
def create():
    """ Create a new deployment
    ---
    put:
        parameters:
            json:
                - name: title
                  type: string
                  required: true
                - name: excel_columns
                  description: a list of columns to use in import.
                  type: string
                  required: false
                - name: excel_header_row
                  description: number of excel row where data header is located
                  type: string
                  required: false
        responses:
            200:
                description: OK. record found
                schenma:
                    success: true
                    deployment:
                        id: 4
                        title: "my deployment"
                        excel_columns: "A,B,C"
                        excel_header_row: 0
            501:
                description: Error. No JSON found in the request
                schema:
                    success: False
                    error: No JSON found in the request
            503:
                description: Integrity error. Record with this title exists already.
                schema:
                    success: False
                    error: Deployment my title exists already
            504:
                description: Error - a record has not been created.
                schema:
                    success: False
                    error: Deployment my title has not been created
    """
    if not request.json:
        return jsonify(success=False, error="No JSON found in the request"), 501

    m_sql = "INSERT INTO deployment (title, excel_columns, excel_header_row) VALUES (:title, :excel_columns, :excel_header_row)"
    l_json = json.loads(request.json)
    print(f"JSON got: {request.json}")
    m_deployment_data = {
        'title': l_json['title'],
        'excel_columns': l_json['excel_columns'],
        'excel_header_row': l_json['excel_header_row']
    }
    conn = get_db()
    try:
        conn.execute(m_sql, m_deployment_data)
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify(success=False, error=f"Deployment {m_deployment_data['title']} exists already"), 503
    m_rs = conn.execute("SELECT id FROM deployment WHERE title=:title", {"title": m_deployment_data['title']}).fetchone()
    if m_rs is None:
        return jsonify(success=False, error=f"Deployment {m_deployment_data['title']} has not been created"), 504
    else:
        m_id = m_rs[0]
        return redirect(f"/deployment/{m_id}")

@deployment.route('/deployment', methods=['POST'])
def update():
    """ Update an existing deployment
    ---
    post:
        parameters:
            json:
                - name: id
                  type: integer
                  required: true
                - name: title
                  type: string
                  required: false
                - name: excel_columns
                  description: a list of columns to use in import.
                  type: string
                  required: false
                - name: excel_header_row
                  description: number of excel row where data header is located
                  type: string
                  required: false
        responses:
            200:
                description: OK. record updated
                schenma:
                    - id (just a number)
            404:
                description: Error - a record to update has not been found.
                schema:
                    - success: False
                    - error: 0 records has been updated instead of 1.
            501:
                description: Error. No JSON found in the request
                schema:
                    - success: False
                    - error: No JSON found in the request
            502:
                description: Error. JSON format is incorrect
                schema:
                    - success: False
                    - error: JSON format is incorrect: no id and/or title
    """
    if not request.json:
        return jsonify(success=False, error="No JSON found in the request"), 501
    
    l_json = json.loads(request.json)
    print(f"Got the following JSON: {l_json}")
    m_id = l_json['id']
    if m_id is None:
        return jsonify(success=False, error="JSON format is incorrect: no id and/or title"), 502
    
    UPDATE_PREFIX = "UPDATE deployment SET "
    
    COLUMNS_BODY = ""
    m_deployment_data = {}
    for m_column in ['title', 'excel_columns', 'excel_header_row']:
        if l_json[m_column]:
            if len(m_deployment_data) > 0:
                COLUMNS_BODY += ", "
            COLUMNS_BODY += f"{m_column}=:{m_column}"
            m_deployment_data[m_column] = l_json[m_column]

    WHERE_SUFFIX = " WHERE id=:id"
    m_deployment_data['id'] = m_id

    m_sql = UPDATE_PREFIX + COLUMNS_BODY + WHERE_SUFFIX
    m_conn = get_db()

    try:
        m_cursor = m_conn.cursor()
        m_cursor.execute(m_sql, m_deployment_data)
        m_conn.commit()
        m_rows_updated = m_cursor.rowcount
        if m_rows_updated != 1:
            return jsonify(success=False, error=f"{m_rows_updated} rows updated instead of 1"), 404
        else:
            return redirect(f"/deployment/{m_id}")
    except sqlite3.Error as m_error:
        return jsonify(success=False, error=m_error)

@deployment.route('/deployment/<id>', methods=['DELETE'])
def delete(id):
    m_sql = "DELETE FROM deployment WHERE id=:id"
    try:
        m_conn = get_db()
        m_cursor = m_conn.cursor()
        m_cursor.execute(m_sql, {'id': id})
        m_conn.commit()
        m_rows_updated = m_cursor.rowcount
        if m_rows_updated != 1:
            return jsonify(success=False, error=f"{m_rows_updated} rows deteled instead of 1"), 404
        else:
            return jsonify(success=True, id=m_id)
    except sqlite3.Error as m_error:
        return jsonify(success=False, error=m_error)

@deployment.route('/deployment/list', methods=['GET'])
def list():
    m_sql = "SELECT id, title, excel_columns, excel_header_row FROM deployment"
    try:
        m_conn = get_db()
        m_cursor = m_conn.cursor()
        m_rs = m_cursor.execute(m_sql).fetchall()
        m_data = []
        for m_row in m_rs:
            m_data.append({
                'id': m_row['id'],
                'title': m_row['title'],
                'excel_columns': m_row['excel_columns'],
                'excel_header_row': m_row['excel_header_row']
                })
        m_ret = {'success': True}
        m_ret['deployments'] = m_data
        return json.dumps(m_ret)
    except sqlite3.Error as m_error:
        return json.dumps({'success': False, 'error': m_error})


if __name__ == "__main__":
    deployment.run(
        host=os.environ.get("HTTP_HOST", "0.0.0.0"),
        port=os.environ.get("HTTP_PORT", "5000"),
        debug=os.environ.get("HTTP_DEBUG", True) 
    )
