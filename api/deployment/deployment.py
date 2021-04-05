import sqlite3
from flask import Flask, json, jsonify, redirect, g

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
        return jsonify(dict(m_rs))

@deployment.route('/deployment/<title>', methods=['PUT'])
def create(title):
    m_sql = "INSERT INTO deployment (title) VALUES (:title)"
    conn = get_db()
    conn.execute(m_sql, {"title": title})
    conn.commit()
    m_rs = conn.execute("SELECT id FROM deployment WHERE title=:title", {"title": title}).fetchone()
    if m_rs is None:
        return jsonify(success=False, error=f"User {title} has not been created")
    else:
        m_id = m_rs[0]
        return redirect(f"/deployment/{m_id}")
    

if __name__ == "__main__":
    deployment.run(host="0.0.0.0")
