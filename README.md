# Digital Anti India Campaign Problem Statement Solution

## Overview
This project is designed to detect, analyze, and collect data related to anti-India campaigns, particularly focusing on online articles and social media content. It includes tools for keyword management, data collection, campaign detection, engagement analysis, and database management.

## Project Structure
- `add_kashmir_keywords.py`: Script to add Kashmir-related keywords to the database.
- `ai_analyzer.py`: AI-based analyzer for campaign data.
- `campaign_data.db`: SQLite database storing campaign data.
- `campaign_detector.py`: Detects anti-India campaigns in collected data.
- `collect_real_data.py`: Collects real-world data (articles, posts, etc.).
- `config.py`: Configuration settings for the project.
- `database.py`: Database utility functions.
- `db_check_runner.py`: Runs database checks.
- `db_diag_out.py`: Outputs database diagnostics.
- `diag_out.json`, `kw_diag_out.json`, `kw_added_out.json`: Diagnostic and output files.
- `engagement_analyzer.py`: Analyzes engagement metrics.
- `enhanced_collected_articles.csv`: CSV of collected articles with enhanced data.
- `enhanced_dashboard.py`: Dashboard for visualizing data.
- `enhanced_data_collector.py`: Enhanced data collection script.
- `enhanced_keyword_database.py`: Enhanced keyword management.
- `found_urls_enhanced.txt`: List of found URLs.
- `kw_diag.py`: Keyword diagnostics script.
- `parse_check.py`: Parsing checks and validation.

## Setup Instructions

### 1. Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### 2. Install Dependencies
Run the following command in the project directory:

```powershell
pip install -r requirements.txt
```

### 3. Database Initialization
The project uses an SQLite database (`campaign_data.db`). Most scripts will create or update the database as needed. No manual setup is required unless you want to inspect or modify the schema.

### 4. Running Scripts
**Data Collection (Must Run):**
  - You must run either `collect_real_data.py` or `enhanced_data_collector.py` to gather articles/posts. These scripts are essential for collecting the data that powers all further analysis and detection in the project.
- **Keyword Management:**
  - `add_kashmir_keywords.py` to add new keywords.
  - `enhanced_keyword_database.py` for advanced keyword operations.
- **Campaign Detection:**
  - `campaign_detector.py` to identify anti-India campaigns.
- **Engagement Analysis:**
  - `engagement_analyzer.py` to analyze engagement metrics.
- **AI Analysis:**
  - `ai_analyzer.py` for AI-based insights.
- **Dashboard:**
  - `enhanced_dashboard.py` to visualize data (may require additional setup; see script for details).

Run any script using:

```powershell
python script_name.py
```

Replace `script_name.py` with the desired script (for example, `enhanced_data_collector.py` for data collection).

### 5. Configuration
Edit `config.py` to adjust settings such as data sources, thresholds, or API keys.

### 6. Diagnostics
- Run `db_check_runner.py`, `db_diag_out.py`, or `kw_diag.py` for database and keyword diagnostics.
- Output files like `diag_out.json`, `kw_diag_out.json`, and `kw_added_out.json` contain diagnostic results.

## Notes
- Ensure all dependencies are installed before running scripts.
- For any issues, check the output and diagnostic files for troubleshooting.
- For more details on each script, refer to the comments within the script files.

## License
This project is for research and educational purposes only.
