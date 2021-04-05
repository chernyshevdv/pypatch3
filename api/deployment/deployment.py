import os
import sqlite3
from types import resolve_bases
from flask import Flask, json, jsonify, request, redirect, g

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
    m_sql = "SELECT * FROM deployment WHERE id=:id"
    m_rs = get_db().execute(m_sql, {"id": id}).fetchone()
    if m_rs is None:
        return jsonify(success=False, error=f"Deployment {id} is not found"), 404
    else:
        m_dict = dict(m_rs)
        m_dict['success'] = True
        return jsonify(m_dict)

@deployment.route('/deployment', methods=['PUT'])
def create():
    if not request.json:
        return jsonify(success=False, error="No JSON found in the request"), 51

    m_sql = "INSERT INTO deployment (title, excel_columns, excel_header_row) VALUES (:title, :excel_columns, :excel_header_row)"
    m_deployment_data = {
        'title': request.json.get('title', ''),
        'excel_columns': request.json.get('excel_columns', ''),
        'excel_header_row': request.json.get('excel_header_row', '0')
    }
    conn = get_db()
    try:
        conn.execute(m_sql, m_deployment_data)
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify(success=False, error=f"Deployment {m_deployment_data['title']} exists already"), 503
    m_rs = conn.execute("SELECT id FROM deployment WHERE title=:title", {"title": m_deployment_data['title']}).fetchone()
    if m_rs is None:
        return jsonify(success=False, error=f"Deployment {title} has not been created")
    else:
        m_id = m_rs[0]
        return redirect(f"/deployment/{m_id}")

@deployment.route('/deployment', methods=['POST'])
def update():
    if not request.json:
        return jsonify(success=False, error="No JSON found in the request"), 501
    m_id = request.json.get('id')
    m_title = request.json.get('title')
    if m_title is None or m_id is None:
        return jsonify(success=False, error="JSON format is incorrect: no id and/or title"), 502
    
    UPDATE_PREFIX = "UPDATE deployment SET title=:title"
    m_deployment_data = {'title': m_title}
    
    COLUMNS_BODY = ""
    for m_column in ['excel_columns', 'excel_header_rows']:
        if request.json.get(m_column):
            COLUMNS_BODY += f", {m_column}=:{m_column}"
            m_deployment_data[m_column] = request.json.get(m_column)

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


if __name__ == "__main__":
    deployment.run(
        host=os.environ.get("HTTP_HOST", "0.0.0.0"),
        port=os.environ.get("HTTP_PORT", "5000"),
        debug=os.environ.get("HTTP_DEBUG", True) 
    )
