from flask import Flask, render_template, jsonify, request
import pyodbc
import pandas as pd
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

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

@app.route('/')
def dashboard():
    """Main dashboard homepage"""
    return render_template('dashboard.html')

@app.route('/trends')
def trends():
    """Trends page with historical policy data"""
    return render_template('trends.html')

@app.route('/gross-commission')
def gross_commission():
    """Gross commission page"""
    return render_template('gross_commission.html')

@app.route('/net-commission')
def net_commission():
    """Net commission page"""
    return render_template('net_commission.html')

# API Routes for data
@app.route('/api/trends-data')
def get_trends_data():
    """Get trends data for charts - Sales, Reinstatements, and Lapses from vw_dashboard_month_end"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        # Query to get monthly totals for the last 6 months from vw_dashboard_month_end
        trends_query = """
        SELECT 
            FORMAT(run_date, 'yyyy-MM') as Period,
            SUM(sales) as total_sales,
            SUM(lapses) as total_lapses,
            SUM(reinstatements) as total_reinstatements
        FROM vw_dashboard_month_end 
        WHERE run_date IS NOT NULL
        AND run_date >= DATEADD(month, -6, GETDATE())
        GROUP BY FORMAT(run_date, 'yyyy-MM')
        ORDER BY Period
        """
        
        df = pd.read_sql(trends_query, conn)
        
        # Prepare chart data
        periods = df['Period'].tolist() if not df.empty else []
        sales_data = df['total_sales'].fillna(0).tolist() if not df.empty else []
        reinstatements_data = df['total_reinstatements'].fillna(0).tolist() if not df.empty else []
        lapses_data = df['total_lapses'].fillna(0).tolist() if not df.empty else []
        
        # Calculate policy count by month (sales + reinstatements)
        policy_count_by_month = [sales + reinstatements for sales, reinstatements in zip(sales_data, reinstatements_data)]
        
        chart_data = {
            'periods': periods,
            'sales': sales_data,
            'reinstatements': reinstatements_data,
            'lapses': lapses_data,
            'policy_count_by_month': policy_count_by_month
        }
        
        conn.close()
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in get_trends_data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/policy-count-by-month')
def get_policy_count_by_month():
    """Get policy count breakdown by month (sales + reinstatements) from vw_dashboard_month_end"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        # Query to get monthly data for the last 6 months from vw_dashboard_month_end
        monthly_query = """
        SELECT 
            FORMAT(run_date, 'yyyy-MM') as period,
            SUM(sales) as sales_counts,
            SUM(lapses) as lapses_counts,
            SUM(reinstatements) as reinstatements_counts
        FROM vw_dashboard_month_end 
        WHERE run_date IS NOT NULL
        AND run_date >= DATEADD(month, -6, GETDATE())
        GROUP BY FORMAT(run_date, 'yyyy-MM')
        ORDER BY period
        """
        
        df = pd.read_sql(monthly_query, conn)
        
        if not df.empty:
            periods = df['period'].tolist()
            sales_counts = df['sales_counts'].fillna(0).tolist()
            reinstatements_counts = df['reinstatements_counts'].fillna(0).tolist()
            lapses_counts = df['lapses_counts'].fillna(0).tolist()
            
            # Calculate policy counts (sales + reinstatements)
            policy_counts = [sales + reinstatements for sales, reinstatements in zip(sales_counts, reinstatements_counts)]
            
            # Calculate month-over-month changes
            monthly_changes = []
            for i, count in enumerate(policy_counts):
                if i == 0:
                    monthly_changes.append(0)  # No change for first month
                else:
                    prev_count = policy_counts[i-1]
                    change_percent = ((count - prev_count) / prev_count * 100) if prev_count > 0 else 0
                    monthly_changes.append(round(change_percent, 1))
        else:
            periods = []
            sales_counts = []
            reinstatements_counts = []
            lapses_counts = []
            policy_counts = []
            monthly_changes = []
        
        data = {
            'periods': periods,
            'policy_counts': policy_counts,
            'sales_counts': sales_counts,
            'reinstatements_counts': reinstatements_counts,
            'lapses_counts': lapses_counts,
            'monthly_changes': monthly_changes,
            'total_policies': sum(policy_counts),
            'total_sales': sum(sales_counts),
            'total_reinstatements': sum(reinstatements_counts),
            'total_lapses': sum(lapses_counts)
        }
        
        conn.close()
        return jsonify(data)
        
    except Exception as e:
        print(f"Error in get_policy_count_by_month: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/policy-count-yoy')
def get_policy_count_yoy():
    """Get year-over-year policy count data for trends analysis from vw_dashboard_month_end"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        # Query to get monthly data for the last 6 months from vw_dashboard_month_end
        yoy_query = """
        SELECT 
            FORMAT(run_date, 'yyyy-MM') as period,
            SUM(sales) as total_sales,
            SUM(lapses) as total_lapses,
            SUM(reinstatements) as total_reinstatements
        FROM vw_dashboard_month_end 
        WHERE run_date IS NOT NULL
        AND run_date >= DATEADD(month, -6, GETDATE())
        GROUP BY FORMAT(run_date, 'yyyy-MM')
        ORDER BY period
        """
        
        df = pd.read_sql(yoy_query, conn)
        
        # Get the last 6 months periods (most recent 6 months)
        if not df.empty:
            periods = df['period'].tolist()
            sales_current = df['total_sales'].fillna(0).tolist()
            lapses_current = df['total_lapses'].fillna(0).tolist()
            reinstatements_current = df['total_reinstatements'].fillna(0).tolist()
        else:
            periods = []
            sales_current = []
            lapses_current = []
            reinstatements_current = []
        
        # For previous year data, we'll use the same months from last year
        # Since the new view may not have complete historical data, we'll use zeros for comparison
        sales_previous = [0] * len(periods)
        lapses_previous = [0] * len(periods)
        reinstatements_previous = [0] * len(periods)
        
        data = {
            'periods': periods,
            'sales_current': sales_current,
            'sales_previous': sales_previous,
            'reinstatements_current': reinstatements_current,
            'reinstatements_previous': reinstatements_previous,
            'lapses_current': lapses_current,
            'lapses_previous': lapses_previous
        }
        
        conn.close()
        return jsonify(data)
        
    except Exception as e:
        print(f"Error in get_policy_count_yoy: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/reinstatements-data')
def get_reinstatements_data():
    """Get reinstatements data from vw_dashboard_month_end"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        query = """
        SELECT 
            product_category_description as ProductType,
            SUM(reinstatements) as PolicyCount,
            FORMAT(run_date, 'yyyy-MM') as Period
        FROM vw_dashboard_month_end 
        WHERE run_date IS NOT NULL
        AND run_date >= DATEADD(month, -6, GETDATE())
        AND reinstatements > 0
        GROUP BY product_category_description, FORMAT(run_date, 'yyyy-MM')
        ORDER BY Period DESC, PolicyCount DESC
        """
        
        df = pd.read_sql(query, conn)
        
        data = {
            'product_types': df['ProductType'].tolist() if not df.empty else [],
            'policy_counts': df['PolicyCount'].fillna(0).tolist() if not df.empty else [],
            'periods': df['Period'].tolist() if not df.empty else []
        }
        
        conn.close()
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lapses-data')
def get_lapses_data():
    """Get lapses data from vw_dashboard_month_end"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        query = """
        SELECT 
            product_category_description as ProductType,
            'Lapse' as Status,
            SUM(lapses) as PolicyCount,
            FORMAT(run_date, 'yyyy-MM') as Period
        FROM vw_dashboard_month_end 
        WHERE run_date IS NOT NULL
        AND run_date >= DATEADD(month, -6, GETDATE())
        AND lapses > 0
        GROUP BY product_category_description, FORMAT(run_date, 'yyyy-MM')
        ORDER BY Period DESC, PolicyCount DESC
        """
        
        df = pd.read_sql(query, conn)
        
        data = {
            'product_types': df['ProductType'].tolist() if not df.empty else [],
            'policy_counts': df['PolicyCount'].fillna(0).tolist() if not df.empty else [],
            'status': df['Status'].tolist() if not df.empty else [],
            'periods': df['Period'].tolist() if not df.empty else []
        }
        
        conn.close()
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Policy Performance Dashboard...")
    print("Database Server: CL-JHB-SQL-01")
    print("Database: Quill")
    print("Authentication: Windows Authentication")
    app.run(debug=True, host='0.0.0.0', port=5000)
