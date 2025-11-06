from flask import Flask, jsonify
import pyodbc
import pandas as pd

app = Flask(__name__)
app.secret_key = 'debug-test-key'

# Database configuration
DB_CONFIG = {
    'server': 'CL-JHB-SQL-01',
    'database': 'Quill',
    'trusted_connection': 'yes'  # Windows Authentication
}

def get_db_connection():
    """Establish database connection using Windows Authentication"""
    try:
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_CONFIG['server']};DATABASE={DB_CONFIG['database']};Trusted_Connection=yes;"
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/debug/lapses')
def debug_lapses():
    """Debug endpoint to test lapses query directly"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        # Simple lapses query
        lapses_query = """
        SELECT 
          CONCAT(
            YEAR(PM.StatusDate), 
            '-', 
            RIGHT('0' + CAST(MONTH(PM.StatusDate) AS VARCHAR(2)), 2)
          ) AS Period,
          COUNT(DISTINCT PM.PolicyMasterID) AS Policies
        FROM 
          vw_ssrs_sales_1 SV 
          INNER JOIN PolicyMaster PM ON PM.PolicyMasterID = SV.PolicyMasterID 
        WHERE 
          PM.Status IN ('Auto-Lapse', 'Cancelled') 
          AND ProductCategoryID NOT IN (8, 11)
        GROUP BY 
          CONCAT(
            YEAR(PM.StatusDate), 
            '-', 
            RIGHT('0' + CAST(MONTH(PM.StatusDate) AS VARCHAR(2)), 2)
          )
        ORDER BY Period
        """
        
        lapses_df = pd.read_sql(lapses_query, conn)
        
        result = {
            'total_rows': len(lapses_df),
            'raw_data': lapses_df.to_dict('records') if not lapses_df.empty else [],
            'query': lapses_query
        }
        
        conn.close()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
