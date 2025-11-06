from flask import Flask, request, jsonify
from flask_cors import CORS
import pyodbc
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database configuration for Windows Authentication
DB_CONFIG = {
    'server': 'CL-JHB-SQL-01',
    'database': 'Quill Database',
    'driver': '{ODBC Driver 17 for SQL Server}'
}

def get_connection():
    """Create database connection with Windows Authentication"""
    conn_str = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        "Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'ok',
            'databaseConnected': True,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/test-connection', methods=['GET'])
def test_connection():
    """Test database connection"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Database connection successful',
            'serverInfo': {
                'server': DB_CONFIG['server'],
                'database': DB_CONFIG['database']
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/execute-query', methods=['POST'])
def execute_query():
    """Execute SQL query"""
    try:
        data = request.get_json()
        query = data.get('query')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'No query provided'
            }), 400
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        
        # Get column names
        columns = [column[0] for column in cursor.description]
        
        # Fetch all rows
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        results = []
        for row in rows:
            row_dict = {}
            for i, value in enumerate(row):
                # Handle different data types
                if isinstance(value, datetime):
                    row_dict[columns[i]] = value.isoformat()
                elif value is None:
                    row_dict[columns[i]] = None
                else:
                    row_dict[columns[i]] = value
            results.append(row_dict)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': results,
            'rowCount': len(results),
            'columns': columns,
            'metadata': {
                'query': query,
                'executedAt': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Query execution failed: {str(e)}'
        }), 500

@app.route('/api/tables', methods=['GET'])
def get_tables():
    """Get list of database tables"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                TABLE_NAME as name,
                TABLE_SCHEMA as schema
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        tables = [{'name': row.name, 'schema': row.schema} for row in rows]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'tables': tables
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print('Python Server starting...')
    print(f'Database: {DB_CONFIG["database"]} on {DB_CONFIG["server"]}')
    print('Using Windows Authentication')
    print('Server running at http://localhost:5001')
    print('-' * 50)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
