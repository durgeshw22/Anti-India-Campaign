# 🛡️ Anti-India Campaign Monitor - START HERE

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start Dashboard
```bash
python quick_start.py
```
**OR**
```bash
streamlit run dashboard.py
```

### Step 3: Open Browser
The dashboard will automatically open at: http://localhost:8501

## 🎯 First Time Usage

1. **🏠 Go to Home Tab** - Check system status
2. **📝 Click "Add Sample Data"** - Get test articles immediately  
3. **🤖 Click "Analyze Articles"** - Run AI analysis
4. **📊 Check Overview Tab** - View dashboard metrics
5. **🔄 Click "News Only"** - Collect real data from NewsAPI

## 🔧 Troubleshooting

### If packages fail to install:
```bash
pip install streamlit requests pandas beautifulsoup4 --no-cache-dir
```

### If database errors occur:
```bash
python reset_database.py
```

### If dashboard won't start:
```bash
python -m streamlit run dashboard.py --server.port 8502
```

## 📊 Data Collection

- **📝 Sample Data**: Instant test articles for demo
- **🔄 News Only**: Real articles from NewsAPI  
- **🌐 All Sources**: News + Reddit + Twitter data
- **💾 Auto-save**: Everything saved to CSV files

## 🎉 You're Ready!

The dashboard monitors anti-India campaigns in real-time with:
- ✅ Live data collection
- ✅ AI sentiment analysis  
- ✅ Interactive visualizations
- ✅ CSV export functionality
- ✅ Multi-source monitoring

**Need help?** Check the Home tab for system status and guides.
