"""
Enhanced Keyword Database Management System
Dynamic keyword database with categories, weights, and learning capabilities
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Set
import re

class KeywordDatabase:
    def __init__(self, db_path=None):
        # Use canonical DATABASE_PATH if not provided to avoid multiple DB files
        if db_path is None:
            try:
                from database import DATABASE_PATH
                self.db_path = DATABASE_PATH
            except Exception:
                self.db_path = "campaign_data.db"
        else:
            self.db_path = db_path
        self.init_keyword_tables()
        self.load_default_keywords()
    
    def init_keyword_tables(self):
        """Initialize keyword database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Keywords table with categories and weights
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                language TEXT DEFAULT 'en',
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_detected DATETIME,
                detection_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Hashtags table for social media monitoring
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hashtags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hashtag TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                platform TEXT,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_used DATETIME,
                usage_count INTEGER DEFAULT 0,
                is_trending BOOLEAN DEFAULT 0
            )
        ''')
        
        # Phrase patterns for complex detection
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS phrase_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT NOT NULL,
                regex_pattern TEXT NOT NULL,
                category TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                description TEXT,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                detection_count INTEGER DEFAULT 0
            )
        ''')
        
        # Keyword effectiveness tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keyword_effectiveness (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword_id INTEGER,
                true_positives INTEGER DEFAULT 0,
                false_positives INTEGER DEFAULT 0,
                precision_score REAL DEFAULT 0.0,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (keyword_id) REFERENCES keywords (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_default_keywords(self):
        """Load default keyword sets if database is empty"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM keywords")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Core anti-India keywords with categories and weights
        default_keywords = [
            # Direct Anti-India Terms (High Weight)
            ("anti India", "direct_hate", 3.0),
            ("boycott India", "boycott_campaign", 2.8),
            ("hate India", "direct_hate", 2.9),
            ("down with India", "direct_hate", 2.7),
            ("India terrorist state", "propaganda", 2.5),
            ("India genocide", "disinformation", 2.6),
            
            # Kashmir-related (High Weight)
            ("Kashmir boycott India", "kashmir_campaign", 2.4),
            ("Kashmir liberation from India", "separatist", 2.3),
            ("free Kashmir from India", "separatist", 2.2),
            ("India occupation Kashmir", "political_criticism", 2.1),
            # Hindi keywords for Kashmir (ensure unicode support and visibility)
            ("कश्मीर", "kashmir_term", 2.5),
            ("कश्मीर आज़ादी", "separatist", 2.3),
            ("कश्मीर स्वतंत्रता", "separatist", 2.3),
            
            # Government/Political (Medium-High Weight)
            ("Modi fascist", "political_attack", 2.0),
            ("BJP terrorist", "political_attack", 1.9),
            ("India fascism", "political_criticism", 1.8),
            ("Hindutva terrorism", "religious_hate", 2.2),
            
            # Human Rights (Medium Weight)
            ("India human rights abuse", "human_rights", 1.7),
            ("India war crimes", "accusations", 1.6),
            ("India ethnic cleansing", "accusations", 1.8),
            ("India apartheid", "accusations", 1.5),
            
            # Economic/Trade (Medium Weight)
            ("boycott Indian products", "economic_campaign", 1.4),
            ("ban Indian goods", "economic_campaign", 1.3),
            ("economic sanctions India", "economic_campaign", 1.2),
            
            # Disinformation (Medium Weight)
            ("fake news India", "disinformation", 1.1),
            ("India propaganda", "disinformation", 1.2),
            ("Indian lies", "disinformation", 1.0),
        ]
        
        for keyword, category, weight in default_keywords:
            cursor.execute('''
                INSERT OR IGNORE INTO keywords (keyword, category, weight)
                VALUES (?, ?, ?)
            ''', (keyword, category, weight))
        
        # Default hashtags
        default_hashtags = [
            ("#BoycottIndia", "boycott_campaign", 2.5, "twitter"),
            ("#AntiIndia", "direct_hate", 2.8, "twitter"),
            ("#KashmirBleeds", "kashmir_campaign", 2.2, "twitter"),
            ("#ModiFascist", "political_attack", 2.0, "twitter"),
            ("#IndiaExposed", "propaganda", 1.8, "twitter"),
            ("#FreeKashmir", "separatist", 2.1, "twitter"),
            ("#IndianTerrorism", "propaganda", 2.4, "twitter"),
            ("#HatePropaganda", "general_hate", 1.5, "general"),
        ]
        
        for hashtag, category, weight, platform in default_hashtags:
            cursor.execute('''
                INSERT OR IGNORE INTO hashtags (hashtag, category, weight, platform)
                VALUES (?, ?, ?, ?)
            ''', (hashtag, category, weight, platform))
        
        # Phrase patterns for complex detection
        phrase_patterns = [
            ("India should be destroyed", r"india\s+should\s+be\s+(destroyed|eliminated|wiped)", "direct_threat", 3.0),
            ("Death to India", r"death\s+to\s+india", "direct_threat", 3.0),
            ("India is terrorist nation", r"india\s+is\s+(a\s+)?terrorist\s+(nation|state|country)", "propaganda", 2.5),
            ("Break India movement", r"break\s+india\s+(movement|campaign|agenda)", "separatist", 2.3),
            ("India behind terrorism", r"india\s+(behind|funding|supporting)\s+terrorism", "conspiracy", 2.1),
        ]
        
        for pattern, regex, category, weight in phrase_patterns:
            cursor.execute('''
                INSERT OR IGNORE INTO phrase_patterns (pattern, regex_pattern, category, weight)
                VALUES (?, ?, ?, ?)
            ''', (pattern, regex, category, weight))
        
        conn.commit()
        conn.close()
    
    def add_keyword(self, keyword: str, category: str, weight: float = 1.0, language: str = 'en'):
        """Add new keyword to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO keywords (keyword, category, weight, language)
                VALUES (?, ?, ?, ?)
            ''', (keyword.lower(), category, weight, language))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def add_hashtag(self, hashtag: str, category: str, weight: float = 1.0, platform: str = 'general'):
        """Add new hashtag to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        hashtag = hashtag if hashtag.startswith('#') else f"#{hashtag}"
        
        try:
            cursor.execute('''
                INSERT INTO hashtags (hashtag, category, weight, platform)
                VALUES (?, ?, ?, ?)
            ''', (hashtag.lower(), category, weight, platform))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_active_keywords(self, category: str = None, min_weight: float = 0.0) -> List[Dict]:
        """Get active keywords with optional filtering"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT keyword, category, weight, detection_count
            FROM keywords 
            WHERE is_active = 1 AND weight >= ?
        '''
        params = [min_weight]
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY weight DESC, detection_count DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'keyword': row[0],
                'category': row[1], 
                'weight': row[2],
                'detection_count': row[3]
            }
            for row in results
        ]
    
    def get_active_hashtags(self, platform: str = None) -> List[Dict]:
        """Get active hashtags for monitoring"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT hashtag, category, weight, platform, usage_count FROM hashtags"
        params = []
        
        if platform:
            query += " WHERE platform = ? OR platform = 'general'"
            params.append(platform)
        
        query += " ORDER BY weight DESC, usage_count DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'hashtag': row[0],
                'category': row[1],
                'weight': row[2],
                'platform': row[3],
                'usage_count': row[4]
            }
            for row in results
        ]
    
    def detect_keywords_in_text(self, text: str) -> Dict:
        """Detect keywords and calculate threat score"""
        text_lower = text.lower()
        detected_keywords = []
        detected_hashtags = []
        detected_patterns = []
        total_score = 0.0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check keywords
        keywords = self.get_active_keywords()
        for kw in keywords:
            if kw['keyword'] in text_lower:
                detected_keywords.append(kw)
                total_score += kw['weight']
                
                # Update detection count
                cursor.execute('''
                    UPDATE keywords 
                    SET detection_count = detection_count + 1, last_detected = CURRENT_TIMESTAMP
                    WHERE keyword = ?
                ''', (kw['keyword'],))
        
        # Check hashtags
        hashtags = self.get_active_hashtags()
        for ht in hashtags:
            if ht['hashtag'] in text_lower:
                detected_hashtags.append(ht)
                total_score += ht['weight']
                
                # Update usage count
                cursor.execute('''
                    UPDATE hashtags 
                    SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
                    WHERE hashtag = ?
                ''', (ht['hashtag'],))
        
        # Check phrase patterns
        cursor.execute("SELECT pattern, regex_pattern, category, weight FROM phrase_patterns")
        patterns = cursor.fetchall()
        
        for pattern, regex_pattern, category, weight in patterns:
            if re.search(regex_pattern, text_lower, re.IGNORECASE):
                detected_patterns.append({
                    'pattern': pattern,
                    'category': category,
                    'weight': weight
                })
                total_score += weight
                
                cursor.execute('''
                    UPDATE phrase_patterns 
                    SET detection_count = detection_count + 1
                    WHERE pattern = ?
                ''', (pattern,))
        
        conn.commit()
        conn.close()
        
        # Calculate threat level
        threat_level = "NONE"
        if total_score >= 5.0:
            threat_level = "HIGH"
        elif total_score >= 3.0:
            threat_level = "MEDIUM"
        elif total_score >= 1.0:
            threat_level = "LOW"
        
        return {
            'detected_keywords': detected_keywords,
            'detected_hashtags': detected_hashtags,
            'detected_patterns': detected_patterns,
            'total_score': total_score,
            'threat_level': threat_level,
            'categories': list(set([kw['category'] for kw in detected_keywords] + 
                                 [ht['category'] for ht in detected_hashtags] +
                                 [pt['category'] for pt in detected_patterns]))
        }
    
    def update_keyword_effectiveness(self, keyword: str, is_true_positive: bool):
        """Update keyword effectiveness based on manual review"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get keyword ID
        cursor.execute("SELECT id FROM keywords WHERE keyword = ?", (keyword,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return
        
        keyword_id = result[0]
        
        # Update effectiveness
        if is_true_positive:
            cursor.execute('''
                INSERT INTO keyword_effectiveness (keyword_id, true_positives)
                VALUES (?, 1)
                ON CONFLICT(keyword_id) DO UPDATE SET
                true_positives = true_positives + 1,
                last_updated = CURRENT_TIMESTAMP
            ''', (keyword_id,))
        else:
            cursor.execute('''
                INSERT INTO keyword_effectiveness (keyword_id, false_positives)
                VALUES (?, 1)
                ON CONFLICT(keyword_id) DO UPDATE SET
                false_positives = false_positives + 1,
                last_updated = CURRENT_TIMESTAMP
            ''', (keyword_id,))
        
        # Recalculate precision
        cursor.execute('''
            UPDATE keyword_effectiveness 
            SET precision_score = CASE 
                WHEN (true_positives + false_positives) > 0 
                THEN CAST(true_positives AS REAL) / (true_positives + false_positives)
                ELSE 0.0
            END
            WHERE keyword_id = ?
        ''', (keyword_id,))
        
        conn.commit()
        conn.close()
    
    def get_keyword_analytics(self) -> Dict:
        """Get keyword performance analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Top performing keywords
        cursor.execute('''
            SELECT k.keyword, k.category, k.weight, k.detection_count,
                   COALESCE(ke.precision_score, 0) as precision
            FROM keywords k
            LEFT JOIN keyword_effectiveness ke ON k.id = ke.keyword_id
            WHERE k.is_active = 1
            ORDER BY k.detection_count DESC, precision DESC
            LIMIT 20
        ''')
        top_keywords = cursor.fetchall()
        
        # Category distribution
        cursor.execute('''
            SELECT category, COUNT(*) as count, AVG(weight) as avg_weight
            FROM keywords
            WHERE is_active = 1
            GROUP BY category
            ORDER BY count DESC
        ''')
        category_stats = cursor.fetchall()
        
        # Recent detections
        cursor.execute('''
            SELECT keyword, category, last_detected
            FROM keywords
            WHERE last_detected IS NOT NULL
            ORDER BY last_detected DESC
            LIMIT 10
        ''')
        recent_detections = cursor.fetchall()
        
        conn.close()
        
        return {
            'top_keywords': [
                {
                    'keyword': row[0],
                    'category': row[1],
                    'weight': row[2],
                    'detection_count': row[3],
                    'precision': row[4]
                }
                for row in top_keywords
            ],
            'category_stats': [
                {
                    'category': row[0],
                    'count': row[1],
                    'avg_weight': row[2]
                }
                for row in category_stats
            ],
            'recent_detections': [
                {
                    'keyword': row[0],
                    'category': row[1],
                    'last_detected': row[2]
                }
                for row in recent_detections
            ]
        }
