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
    """Get trends data for charts - Sales, Reinstatements, and Lapses"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        # Sales query
        sales_query = """
        SELECT 
          Count(distinct PM.PolicyMasterID) as Policies, 
          ProductionPeriod as Period, 
          ProductCategoryDescription as ProductType
        FROM 
          vw_ssrs_sales_1 SV 
          INNER JOIN PolicyMaster PM ON PM.PolicyMasterID = SV.PolicyMasterID 
        WHERE 
          NewBusinessWithUpgradeSale = 1 
          AND ProductCategoryID NOT IN (8, 11) 
          AND ProductionPeriod IS NOT NULL
          AND ProductionPeriod >= '2024-1' 
        GROUP BY 
          ProductionPeriod, 
          ProductCategoryDescription
        ORDER BY
          ProductionPeriod DESC,
          ProductCategoryDescription
        """
        
        # Execute queries
        sales_df = pd.read_sql(sales_query, conn)
        
        # Reinstatements query
        reinstatements_query = """
        select 
          Count(distinct PM.PolicyMasterID) as Policies, 
          CONCAT(YEAR(PM.Reinstdate), '-', MONTH(PM.Reinstdate)) as Period, 
          ProductCategoryDescription ProductType 
        from 
          vw_ssrs_sales_1 SV 
          inner join PolicyMaster PM on PM.PolicyMasterID = SV.PolicyMasterID 
        where productcategoryid not in (8, 11) 
        AND SV.ProductionPeriod >= '2024-1' 
        AND PM.Reinstdate IS NOT NULL
        group by 
          CONCAT(
            YEAR(PM.Reinstdate), 
            '-', 
            MONTH(PM.Reinstdate)
          ), 
          ProductCategoryDescription
        """
        
        # Lapses query
        lapses_query = """
        SELECT 
          COUNT(DISTINCT PM.PolicyMasterID) AS Policies, 
          PM.Status, 
          CONCAT(
            YEAR(PM.StatusDate), 
            '-', 
            RIGHT('0' + CAST(MONTH(PM.StatusDate) AS VARCHAR(2)), 2)
          ) AS Period, 
          ProductCategoryDescription AS ProductType 
        FROM 
          vw_ssrs_sales_1 SV 
          INNER JOIN PolicyMaster PM ON PM.PolicyMasterID = SV.PolicyMasterID 
        WHERE 
          PM.Status IN ('Auto-Lapse', 'Cancelled') 
          AND ProductCategoryID NOT IN (8, 11) 
          AND sv.newbusinesswithupgradesale = 1
        GROUP BY 
          PM.Status, 
          CONCAT(
            YEAR(PM.StatusDate), 
            '-', 
            RIGHT('0' + CAST(MONTH(PM.StatusDate) AS VARCHAR(2)), 2)
          ), 
          ProductCategoryDescription
        ORDER BY
          Period DESC,
          PM.Status,
          ProductCategoryDescription
        """
        
        # Execute queries
        sales_df = pd.read_sql(sales_query, conn)
        reinstatements_df = pd.read_sql(reinstatements_query, conn)
        lapses_df = pd.read_sql(lapses_query, conn)
        
        # Process data for charts
        # Sales data
        sales_data = {}
        for _, row in sales_df.iterrows():
            period = row['Period']
            policies = row['Policies']
            product_type = row['ProductType']
            
            if period not in sales_data:
                sales_data[period] = {'total': 0, 'products': {}}
            sales_data[period]['total'] += policies
            sales_data[period]['products'][product_type] = policies
        
        # Reinstatements data
        reinstatements_data = {}
        for _, row in reinstatements_df.iterrows():
            period = row['Period']
            policies = row['Policies']
            product_type = row['ProductType']
            
            if period not in reinstatements_data:
                reinstatements_data[period] = {'total': 0, 'products': {}}
            reinstatements_data[period]['total'] += policies
            reinstatements_data[period]['products'][product_type] = policies
        
        # Lapses data
        lapses_data = {}
        for _, row in lapses_df.iterrows():
            period = row['Period']
            policies = row['Policies']
            status = row['Status']
            product_type = row['ProductType']
            
            if period not in lapses_data:
                lapses_data[period] = {'total': 0, 'products': {}}
            lapses_data[period]['total'] += policies
            lapses_data[period]['products'][product_type] = policies
        
        # Combine all periods
        all_periods = set()
        all_periods.update(sales_data.keys())
        all_periods.update(reinstatements_data.keys())
        all_periods.update(lapses_data.keys())
        
        # Sort periods
        sorted_periods = sorted(all_periods)
        
        # Prepare chart data with policy count by month
        chart_data = {
            'periods': sorted_periods,
            'sales': [],
            'reinstatements': [],
            'lapses': [],
            'policy_count_by_month': []
        }
        
        for period in sorted_periods:
            sales_count = sales_data.get(period, {}).get('total', 0)
            reinstatements_count = reinstatements_data.get(period, {}).get('total', 0)
            lapses_count = lapses_data.get(period, {}).get('total', 0)
            
            chart_data['sales'].append(sales_count)
            chart_data['reinstatements'].append(reinstatements_count)
            chart_data['lapses'].append(lapses_count)
            chart_data['policy_count_by_month'].append(sales_count + reinstatements_count)
        
        conn.close()
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error in get_trends_data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/policy-count-by-month')
def get_policy_count_by_month():
    """Get policy count breakdown by month (sales + reinstatements)"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        # Sales query for monthly policy count
        sales_query = """
        SELECT 
          ProductionPeriod as Period,
          COUNT(distinct PM.PolicyMasterID) as Policies
        FROM 
          vw_ssrs_sales_1 SV 
          INNER JOIN PolicyMaster PM ON PM.PolicyMasterID = SV.PolicyMasterID 
        WHERE 
          NewBusinessWithUpgradeSale = 1 
          AND ProductCategoryID NOT IN (8, 11) 
          AND ProductionPeriod IS NOT NULL
          AND ProductionPeriod >= '2024-1' 
        GROUP BY 
          ProductionPeriod
        ORDER BY ProductionPeriod
        """
        
        # Reinstatements query for monthly policy count
        reinstatements_query = """
        select 
          CONCAT(YEAR(PM.Reinstdate), '-', MONTH(PM.Reinstdate)) as Period,
          Count(distinct PM.PolicyMasterID) as Policies
        from 
          vw_ssrs_sales_1 SV 
          inner join PolicyMaster PM on PM.PolicyMasterID = SV.PolicyMasterID 
        where productcategoryid not in (8, 11) 
        AND SV.ProductionPeriod >= '2024-1' 
        AND PM.Reinstdate IS NOT NULL
        group by 
          CONCAT(YEAR(PM.Reinstdate), '-', MONTH(PM.Reinstdate))
        ORDER BY Period
        """
        
        # Execute queries
        sales_df = pd.read_sql(sales_query, conn)
        reinstatements_df = pd.read_sql(reinstatements_query, conn)
        
        # Process sales data by period
        sales_data = {}
        for _, row in sales_df.iterrows():
            period = row['Period']
            sales_data[period] = row['Policies']
        
        # Process reinstatements data by period
        reinstatements_data = {}
        for _, row in reinstatements_df.iterrows():
            period = row['Period']
            reinstatements_data[period] = row['Policies']
        
        # Get lapses data for context - use same logic as trends-data
        lapses_query = """
        SELECT 
          COUNT(DISTINCT PM.PolicyMasterID) AS Policies,
          CONCAT(
            YEAR(PM.StatusDate), 
            '-', 
            RIGHT('0' + CAST(MONTH(PM.StatusDate) AS VARCHAR(2)), 2)
          ) AS Period
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
        lapses_data = {}
        for _, row in lapses_df.iterrows():
            period = row['Period']
            lapses_data[period] = row['Policies']
        
        # CRITICAL FIX: Combine ALL periods from ALL data sources (just like in get_trends_data)
        all_periods = set()
        all_periods.update(sales_data.keys())
        all_periods.update(reinstatements_data.keys())
        all_periods.update(lapses_data.keys())
        
        # Sort all periods
        periods = sorted(all_periods)
        
        # Build arrays for all periods
        policy_counts = []
        sales_counts = []
        reinstatements_counts = []
        lapses_counts = []
        
        for period in periods:
            sales_count = sales_data.get(period, 0)
            reinstatements_count = reinstatements_data.get(period, 0)
            total_count = sales_count + reinstatements_count
            lapses_count = lapses_data.get(period, 0)
            
            sales_counts.append(sales_count)
            reinstatements_counts.append(reinstatements_count)
            policy_counts.append(total_count)
            lapses_counts.append(lapses_count)
        
        # Calculate month-over-month changes
        monthly_changes = []
        for i, count in enumerate(policy_counts):
            if i == 0:
                monthly_changes.append(0)  # No change for first month
            else:
                prev_count = policy_counts[i-1]
                change_percent = ((count - prev_count) / prev_count * 100) if prev_count > 0 else 0
                monthly_changes.append(round(change_percent, 1))
        
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

@app.route('/api/reinstatements-data')
def get_reinstatements_data():
    """Get reinstatements data"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        query = """
        select 
          ProductCategoryDescription as ProductType,
          Count(distinct PM.PolicyMasterID) as PolicyCount,
          CONCAT(YEAR(PM.Reinstdate), '-', MONTH(PM.Reinstdate)) as Period
        from 
          vw_ssrs_sales_1 SV 
          inner join PolicyMaster PM on PM.PolicyMasterID = SV.PolicyMasterID 
        where productcategoryid not in (8, 11) 
        AND SV.ProductionPeriod >= '2024-1'
        AND PM.Reinstdate IS NOT NULL
        group by 
          ProductCategoryDescription,
          CONCAT(YEAR(PM.Reinstdate), '-', MONTH(PM.Reinstdate))
        ORDER BY Period DESC, PolicyCount DESC
        """
        
        df = pd.read_sql(query, conn)
        
        data = {
            'product_types': df['ProductType'].tolist(),
            'policy_counts': df['PolicyCount'].tolist(),
            'periods': df['Period'].tolist()
        }
        
        conn.close()
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lapses-data')
def get_lapses_data():
    """Get lapses data"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        query = """
        SELECT 
          ProductCategoryDescription as ProductType,
          PM.Status as Status,
          COUNT(DISTINCT PM.PolicyMasterID) AS PolicyCount,
          CONCAT(
            YEAR(PM.StatusDate), 
            '-', 
            RIGHT('0' + CAST(MONTH(PM.StatusDate) AS VARCHAR(2)), 2)
          ) AS Period
        FROM 
          vw_ssrs_sales_1 SV 
          INNER JOIN PolicyMaster PM ON PM.PolicyMasterID = SV.PolicyMasterID 
        WHERE 
          PM.Status IN ('Auto-Lapse', 'Cancelled') 
          AND ProductCategoryID NOT IN (8, 11) 
          AND sv.newbusinesswithupgradesale = 1
        GROUP BY 
          ProductCategoryDescription,
          PM.Status,
          CONCAT(
            YEAR(PM.StatusDate), 
            '-', 
            RIGHT('0' + CAST(MONTH(PM.StatusDate) AS VARCHAR(2)), 2)
          )
        ORDER BY Period DESC, PolicyCount DESC
        """
        
        df = pd.read_sql(query, conn)
        
        data = {
            'product_types': df['ProductType'].tolist(),
            'policy_counts': df['PolicyCount'].tolist(),
            'status': df['Status'].tolist(),
            'periods': df['Period'].tolist()
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
