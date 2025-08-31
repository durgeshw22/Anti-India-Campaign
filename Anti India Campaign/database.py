import sqlite3
import pandas as pd
from datetime import datetime
import json
import os

# Database configuration
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'campaign_data.db')

def init_database():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create articles table with all required columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            url TEXT UNIQUE,
            source TEXT,
            published_date DATETIME,
            collected_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            sentiment_score REAL,
            relevance_score INTEGER,
            countries_mentioned TEXT,
            keywords_found TEXT,
            classification TEXT
        )
    ''')
    
    # Check if we need to add missing columns to existing table
    cursor.execute("PRAGMA table_info(articles)")
    columns = [column[1] for column in cursor.fetchall()]
    
    required_columns = [
        ('countries_mentioned', 'TEXT'),
        ('keywords_found', 'TEXT'), 
        ('classification', 'TEXT'),
        ('sentiment_score', 'REAL'),
        ('relevance_score', 'INTEGER')
    ]
    
    for column_name, column_type in required_columns:
        if column_name not in columns:
            try:
                cursor.execute(f'ALTER TABLE articles ADD COLUMN {column_name} {column_type}')
                print(f"Added column: {column_name}")
            except Exception as e:
                print(f"Column {column_name} already exists or error: {e}")
    
    # Create campaigns table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            source_country TEXT,
            target_country TEXT,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            severity_level INTEGER,
            article_ids TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def save_article(article_data):
    """Save article to database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    last_id = None
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO articles 
            (title, content, url, source, published_date, sentiment_score, 
             relevance_score, countries_mentioned, keywords_found, classification)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            article_data.get('title'),
            article_data.get('content'),
            article_data.get('url'),
            article_data.get('source'),
            article_data.get('published_date'),
            article_data.get('sentiment_score'),
            article_data.get('relevance_score'),
            json.dumps(article_data.get('countries_mentioned', [])),
            json.dumps(article_data.get('keywords_found', [])),
            article_data.get('classification')
        ))
        conn.commit()
        last_id = cursor.lastrowid
        try:
            print(f"✅ Saved article id={last_id} to {DATABASE_PATH}: {str(article_data.get('title'))[:80]}")
        except Exception:
            print(f"✅ Saved article id={last_id} to {DATABASE_PATH}")
        return last_id
    except Exception as e:
        print(f"❌ Failed to save article: {e}\nData: {json.dumps(article_data, default=str)[:500]}")
        return None
    finally:
        try:
            conn.commit()
        except Exception:
            pass
        conn.close()

def get_articles(limit=100, filters=None):
    """Retrieve articles from database with optional filters"""
    conn = sqlite3.connect(DATABASE_PATH)
    
    query = "SELECT * FROM articles WHERE 1=1"
    params = []
    
    if filters:
        if filters.get('start_date'):
            query += " AND collected_date >= ?"
            params.append(filters['start_date'])
        if filters.get('end_date'):
            query += " AND collected_date <= ?"
            params.append(filters['end_date'])
        if filters.get('country'):
            query += " AND countries_mentioned LIKE ?"
            params.append(f'%{filters["country"]}%')
    
    query += f" ORDER BY collected_date DESC LIMIT {limit}"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df

def get_statistics():
    """Get dashboard statistics with error handling for missing columns"""
    conn = sqlite3.connect(DATABASE_PATH)
    
    stats = {}
    
    try:
        # Total articles
        stats['total_articles'] = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM articles", conn
        ).iloc[0]['count']
        
        # Check if sentiment_score column exists
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(articles)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'sentiment_score' in columns:
            # Articles by sentiment
            sentiment_data = pd.read_sql_query(
                """SELECT 
                    CASE 
                        WHEN sentiment_score < -0.1 THEN 'Negative'
                        WHEN sentiment_score > 0.1 THEN 'Positive'
                        ELSE 'Neutral'
                    END as sentiment,
                    COUNT(*) as count
                FROM articles 
                WHERE sentiment_score IS NOT NULL
                GROUP BY sentiment""", conn
            )
            stats['sentiment_distribution'] = sentiment_data
        else:
            # Create empty DataFrame with expected structure
            stats['sentiment_distribution'] = pd.DataFrame({
                'sentiment': ['Negative', 'Neutral', 'Positive'],
                'count': [0, 0, 0]
            })
        
        if 'countries_mentioned' in columns:
            # Articles by country (only non-null values)
            country_data = pd.read_sql_query(
                """SELECT countries_mentioned, COUNT(*) as count 
                FROM articles 
                WHERE countries_mentioned IS NOT NULL 
                AND countries_mentioned != ''
                AND countries_mentioned != '[]'
                GROUP BY countries_mentioned""", conn
            )
            stats['country_distribution'] = country_data
        else:
            # Create empty DataFrame
            stats['country_distribution'] = pd.DataFrame({
                'countries_mentioned': [],
                'count': []
            })
        
        # Recent activity
        recent_data = pd.read_sql_query(
            """SELECT DATE(collected_date) as date, COUNT(*) as count 
            FROM articles 
            WHERE collected_date >= date('now', '-30 days')
            GROUP BY DATE(collected_date)
            ORDER BY date""", conn
        )
        stats['recent_activity'] = recent_data
        
    except Exception as e:
        print(f"Error getting statistics: {e}")
        # Return empty stats on error
        stats = {
            'total_articles': 0,
            'sentiment_distribution': pd.DataFrame({
                'sentiment': ['Negative', 'Neutral', 'Positive'],
                'count': [0, 0, 0]
            }),
            'country_distribution': pd.DataFrame({
                'countries_mentioned': [],
                'count': []
            }),
            'recent_activity': pd.DataFrame({
                'date': [],
                'count': []
            })
        }
    
    finally:
        conn.close()
    
    return stats


def debug_db_status():
    """Return basic debug info about the database file and article counts."""
    info = {}
    info['db_path'] = DATABASE_PATH
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM articles")
        info['article_count'] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM campaigns")
        info['campaign_count'] = cur.fetchone()[0]
        conn.close()
    except Exception as e:
        info['error'] = str(e)
    return info
