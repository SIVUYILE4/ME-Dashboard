# Quick Start Guide - Commission Dashboard

## ✅ System Status
Your Python Flask Commission Dashboard is **RUNNING** and ready to use!

## 🚀 Accessing the Dashboard

The dashboard is currently running at:
- **URL**: http://localhost:5000
- **Server**: CL-JHB-SQL-01
- **Database**: Quill
- **Authentication**: Windows Authentication

## 📊 Available Pages

1. **Home Dashboard** - http://localhost:5000
   - Welcome page with quick navigation
   - Feature overview
   - Getting started guide

2. **Trends Analysis** - http://localhost:5000/trends
   - Historical commission trends
   - Interactive line and bar charts
   - Monthly comparison data

3. **Gross Commission** - http://localhost:5000/gross-commission
   - Performance by sales representative
   - Top performers leaderboard
   - Commission distribution charts

4. **Net Commission** - http://localhost:5000/net-commission
   - Net vs Gross comparison
   - Commission efficiency metrics
   - Breakdown analysis

## 🔧 Current Session

The Flask development server is running with these settings:
- Debug mode: **ON**
- Host: 0.0.0.0 (accessible from any network interface)
- Port: 5000
- Auto-reload: Enabled (changes will automatically restart server)

## 📝 Next Steps

### 1. Customize Database Queries
The current dashboard uses **placeholder queries**. Update them with your actual Quill database schema:

Open `app.py` and modify these functions:
- Line 42: `get_trends_data()` 
- Line 72: `get_gross_commission_data()`
- Line 97: `get_net_commission_data()`

Replace the sample SQL with queries that match your actual table and column names.

### 2. Test Database Connectivity
Once you update the queries, test the API endpoints:
- http://localhost:5000/api/trends-data
- http://localhost:5000/api/gross-commission-data
- http://localhost:5000/api/net-commission-data

### 3. Verify Data Display
After successful database queries, verify the data appears correctly in:
- Charts (should populate with real data)
- Tables (should show actual records)
- Metrics cards (should display calculated values)

## ⚠️ Important Notes

### Database Connection
- Ensure you're on the network where CL-JHB-SQL-01 is accessible
- Windows Authentication should use your current Windows credentials
- If connection fails, check firewall rules and SQL Server permissions

### Dependencies
Some packages (pandas, pyodbc) may need manual installation:
```bash
pip install Flask
pip install pyodbc --only-binary :all:
pip install pandas --only-binary :all:
```

## 🛑 Stopping the Server

To stop the dashboard:
1. Find the terminal running `python app.py`
2. Press `Ctrl+C`

To restart:
```bash
python app.py
```

## 📁 Project Files

```
ME Dashboard/
├── app.py                    # Main application (UPDATE SQL QUERIES HERE)
├── requirements.txt          # Dependencies
├── README.md                # Full documentation
├── QUICKSTART.md            # This file
├── templates/               # HTML pages (all working)
│   ├── base.html
│   ├── dashboard.html
│   ├── trends.html
│   ├── gross_commission.html
│   └── net_commission.html
└── static/                  # CSS and JavaScript (all loading)
    ├── css/dashboard.css
    └── js/dashboard.js
```

## ✨ Features Working

- ✅ Professional corporate design
- ✅ Responsive layout
- ✅ Side panel navigation
- ✅ All pages loading correctly
- ✅ Static assets (CSS, JS) serving properly
- ✅ Chart.js integration ready
- ✅ Font Awesome icons
- ✅ Windows Authentication configured

## 🎯 Ready to Use!

Your commission dashboard is fully functional and ready to display data once you customize the SQL queries to match your Quill database schema.

Open http://localhost:5000 in your browser to get started!
