import sqlite3, os
from flask import Flask, g, request
from flask.helpers import get_flashed_messages
from flask_restful import Resource, Api, reqparse, abort
from werkzeug.exceptions import BadRequest

app = Flask(__name__)
api = Api(app)

def get_db():
    """
    Opens DB connection if it's not open yet
    """
    if not hasattr(g, 'db_conn'):
        g.db_conn = sqlite3.connect("pypatch.sqlite")
        g.db_conn.row_factory = sqlite3.Row
    
    return g.db_conn

dep_parser = reqparse.RequestParser()
dep_parser.add_argument('title', type=str, help='Deployment title', required=True)
dep_parser.add_argument('excel_columns', type=str, help='List of columns to use. E.g.: A,C,H-K', required=False)
dep_parser.add_argument('excel_header_row', type=int, help='ID of excel row containing report header', required=False)

def get_deployment(id):
    "Retrieve deployment from DB. The method is to be re-used."
    m_sql = "SELECT * FROM deployment WHERE id=:id"
    m_rs = get_db().execute(m_sql, {"id": id}).fetchone()
        
    return m_rs 

class Deployment(Resource):
    """
    Single Deployment: RUD (read, update, delete)
    """
    def get(self, id):
        "Retrieve deployment by ID"
        m_dep = get_deployment(id)
        
        return dict(m_dep) if m_dep else {'success': False, 'error': f"No deployment found with ID: {id}"}

    def put(self, id):
        "Update an existing deployment"
        m_args = dep_parser.parse_args()
        m_sql = """
                    UPDATE deployment 
                    SET title=:title, 
                        excel_columns=:excel_columns, 
                        excel_header_row=:excel_header_row 
                    WHERE id=:id
                """
        try:
            m_conn = get_db()
            m_cur = m_conn.cursor()
            m_cur.execute(m_sql, {
                                'id': id, 
                                'title': m_args['title'],
                                'excel_columns': m_args['excel_columns'],
                                'excel_header_row': m_args['excel_header_row']
                                })
            m_conn.commit()
            if m_cur.rowcount == 0:
                abort(404, message=f"Deployment {id} not found")
            elif m_cur.rowcount != 1:
                abort(404, message=f"Updated {m_cur.rowcount} rows instead of 1")
            else:
                return m_args, 200
        except sqlite3.Error as error:
            abort(500, error)

    def delete(self, id):
        "Delete deployment by ID"
        m_sql = "DELETE FROM deployment WHERE id=:id"
        try:
            m_conn = get_db()
            m_cur = m_conn.cursor()
            m_cur.execute(m_sql, {'id': id})
            m_conn.commit()
            if m_cur.rowcount != 1:
                abort(404, message=f"{m_cur.rowcount} deleted while 1 expected")
        except sqlite3.Error as error:
            abort(500, message=error)
        return "", 204

class DeploymentList(Resource):
    """
    List of Deployments: List and Create
    """
    def get(self):
        "List deployments"
        m_sql = "SELECT * FROM deployment"
        m_rs = get_db().execute(m_sql).fetchall()

        return [dict(row) for row in m_rs]

    def post(self):
        "Create a deployment"
        m_args = dep_parser.parse_args()
        m_sql = """
        INSERT INTO deployment (title, excel_columns, excel_header_row)
        VALUES (:title, :excel_columns, :excel_header_row)
        """
        try:
            m_conn = get_db()
            m_cur = m_conn.cursor()
            m_cur.execute(m_sql, m_args)
            m_conn.commit()
            m_id = m_cur.lastrowid
            m_dep = get_deployment(m_id)
            return (dict(m_dep), 201) if m_dep else ({'success': False, 'error': f"No deployment found with ID: {id}"}, 404)
        except sqlite3.Error as error:
            abort(501, message=error)


api.add_resource(Deployment, '/deployment/<int:id>')
api.add_resource(DeploymentList, '/deployments')

if __name__ == "__main__":
    app.run(
        host=os.environ.get("DEPLOYMENT_HOST", "0.0.0.0"),
        port=os.environ.get("DEPLOYMENT_PORT", 5000),
        debug=os.environ.get("DEPLOYMENT_DEBUG", True)
    )