import sqlite3
import json
import re
import requests
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import hashlib
import threading
from dataclasses import dataclass
from textblob import TextBlob
import networkx as nx

@dataclass
class CampaignContent:
    """Data structure for campaign content"""
    id: str
    platform: str
    content: str
    author: str
    timestamp: datetime
    engagement: Dict[str, int]
    hashtags: List[str]
    mentions: List[str]
    url: str
    sentiment_score: float
    threat_level: str
    keywords_matched: List[str]

class KeywordDatabase:
    """Dynamic keyword and phrase database for anti-India sentiment detection"""
    
    def __init__(self, db_path: str = "keyword_database.db"):
        self.db_path = db_path
        self.init_database()
        self.load_initial_keywords()
    
    def init_database(self):
        """Initialize the keyword database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Keywords table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                severity INTEGER NOT NULL,
                detection_count INTEGER DEFAULT 0,
                last_detected TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Phrase patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS phrase_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT NOT NULL,
                description TEXT,
                severity INTEGER NOT NULL,
                detection_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Hashtags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hashtags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hashtag TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                severity INTEGER NOT NULL,
                detection_count INTEGER DEFAULT 0,
                last_detected TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Campaign signatures table (for coordinated campaign detection)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaign_signatures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signature_hash TEXT UNIQUE NOT NULL,
                content_template TEXT NOT NULL,
                detection_count INTEGER DEFAULT 0,
                first_detected TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_detected TIMESTAMP,
                accounts_involved TEXT  -- JSON array of account IDs
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_initial_keywords(self):
        """Load initial comprehensive keyword set"""
        initial_keywords = [
            # Direct anti-India terms
            ("anti India", "direct_hate", 9),
            ("hate India", "direct_hate", 9),
            ("India terrorist", "disinformation", 8),
            ("fascist India", "political_hate", 8),
            ("boycott India", "economic_warfare", 7),
            ("India occupation", "territorial_dispute", 7),
            ("Modi dictator", "political_hate", 6),
            ("BJP terrorist", "political_hate", 8),
            ("Hindu terrorism", "religious_hate", 9),
            ("India genocide", "disinformation", 9),
            ("Hindutva fascism", "religious_hate", 8),
            
            # Kashmir-related anti-India terms
            ("Kashmir freedom", "separatist", 6),
            ("Kashmir liberation", "separatist", 7),
            ("Indian occupied Kashmir", "territorial_dispute", 8),
            ("Kashmir resistance", "separatist", 6),
            ("Free Kashmir from India", "separatist", 8),
            
            # Economic warfare terms
            ("boycott Indian products", "economic_warfare", 6),
            ("ban Indian goods", "economic_warfare", 6),
            ("India economic terrorism", "disinformation", 7),
            
            # Disinformation terms
            ("India fake news", "meta_disinformation", 5),
            ("Indian propaganda", "meta_disinformation", 5),
            ("Bollywood propaganda", "cultural_warfare", 4),
            
            # Regional tensions
            ("India Pakistan war", "conflict_incitement", 6),
            ("India China conflict", "conflict_incitement", 6),
            ("India Bangladesh tension", "regional_destabilization", 5),
            
            # Religious hatred
            ("Islamophobia India", "religious_hate", 7),
            ("persecution Muslims India", "religious_hate", 8),
            ("minority oppression India", "religious_hate", 7)
        ]
        
        initial_hashtags = [
            ("#AntiIndia", "direct_hate", 8),
            ("#BoycottIndia", "economic_warfare", 7),
            ("#KashmirFreedom", "separatist", 6),
            ("#ModiTerrorist", "political_hate", 8),
            ("#IndianTerrorism", "disinformation", 9),
            ("#HindutvaFascism", "religious_hate", 8),
            ("#FreeKashmir", "separatist", 7),
            ("#IndianOccupation", "territorial_dispute", 8),
            ("#BJPTerrorism", "political_hate", 8),
            ("#StopIndianTerror", "disinformation", 8)
        ]
        
        initial_patterns = [
            (r"India (is|are) (terrorist|terrorism)", "India terrorism accusation", 9),
            (r"boycott (all )?Indian? (products?|goods?)", "Economic boycott call", 7),
            (r"(free|liberate) Kashmir from India", "Kashmir separatism", 8),
            (r"Modi (is|the) (dictator|fascist|terrorist)", "Political character assassination", 7),
            (r"Hindu(tva)? (terrorism|terrorist|fascis)", "Religious hatred", 9),
            (r"India commit(s|ted|ting) genocide", "Genocide accusation", 9),
            (r"Pakistan (will )?defeat India", "Conflict incitement", 6),
            (r"India (fake|false) (news|propaganda)", "Meta disinformation", 5)
        ]
        
        # Insert initial data
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert keywords
        for keyword, category, severity in initial_keywords:
            cursor.execute('''
                INSERT OR IGNORE INTO keywords (keyword, category, severity)
                VALUES (?, ?, ?)
            ''', (keyword, category, severity))
        
        # Insert hashtags
        for hashtag, category, severity in initial_hashtags:
            cursor.execute('''
                INSERT OR IGNORE INTO hashtags (hashtag, category, severity)
                VALUES (?, ?, ?)
            ''', (hashtag, category, severity))
        
        # Insert patterns
        for pattern, description, severity in initial_patterns:
            cursor.execute('''
                INSERT OR IGNORE INTO phrase_patterns (pattern, description, severity)
                VALUES (?, ?, ?)
            ''', (pattern, description, severity))
        
        conn.commit()
        conn.close()
    
    def add_keyword(self, keyword: str, category: str, severity: int):
        """Add new keyword to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO keywords (keyword, category, severity)
            VALUES (?, ?, ?)
        ''', (keyword.lower(), category, severity))
        
        conn.commit()
        conn.close()
    
    def get_active_keywords(self) -> List[Tuple[str, str, int]]:
        """Get all active keywords"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT keyword, category, severity 
            FROM keywords 
            WHERE is_active = 1
            ORDER BY severity DESC
        ''')
        
        keywords = cursor.fetchall()
        conn.close()
        return keywords
    
    def get_hashtags(self) -> List[Tuple[str, str, int]]:
        """Get all monitored hashtags"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT hashtag, category, severity 
            FROM hashtags 
            ORDER BY severity DESC
        ''')
        
        hashtags = cursor.fetchall()
        conn.close()
        return hashtags
    
    def get_patterns(self) -> List[Tuple[str, str, int]]:
        """Get all phrase patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT pattern, description, severity 
            FROM phrase_patterns 
            ORDER BY severity DESC
        ''')
        
        patterns = cursor.fetchall()
        conn.close()
        return patterns
    
    def update_detection_count(self, keyword: str, keyword_type: str = "keyword"):
        """Update detection count for keyword/hashtag"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        table = "keywords" if keyword_type == "keyword" else "hashtags"
        column = "keyword" if keyword_type == "keyword" else "hashtag"
        
        cursor.execute(f'''
            UPDATE {table} 
            SET detection_count = detection_count + 1,
                last_detected = CURRENT_TIMESTAMP
            WHERE {column} = ?
        ''', (keyword.lower(),))
        
        conn.commit()
        conn.close()

class NLPProcessor:
    """Natural Language Processing for content analysis"""
    
    def __init__(self, keyword_db: KeywordDatabase):
        self.keyword_db = keyword_db
        self.load_nlp_resources()
    
    def load_nlp_resources(self):
        """Load NLP resources and patterns"""
        self.keywords = self.keyword_db.get_active_keywords()
        self.hashtags = self.keyword_db.get_hashtags()
        self.patterns = self.keyword_db.get_patterns()
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = [(re.compile(pattern, re.IGNORECASE), desc, severity) 
                                 for pattern, desc, severity in self.patterns]
    
    def extract_features(self, content: str) -> Dict[str, Any]:
        """Extract comprehensive features from content"""
        features = {
            'matched_keywords': [],
            'matched_hashtags': [],
            'matched_patterns': [],
            'sentiment_score': 0.0,
            'threat_level': 'LOW',
            'total_severity': 0,
            'hashtags_found': [],
            'mentions_found': [],
            'urls_found': []
        }
        
        content_lower = content.lower()
        
        # Extract hashtags and mentions
        features['hashtags_found'] = re.findall(r'#\w+', content)
        features['mentions_found'] = re.findall(r'@\w+', content)
        features['urls_found'] = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        
        # Keyword matching
        for keyword, category, severity in self.keywords:
            if keyword.lower() in content_lower:
                features['matched_keywords'].append({
                    'keyword': keyword,
                    'category': category,
                    'severity': severity
                })
                features['total_severity'] += severity
                self.keyword_db.update_detection_count(keyword, "keyword")
        
        # Hashtag matching
        for hashtag, category, severity in self.hashtags:
            if hashtag.lower() in content_lower:
                features['matched_hashtags'].append({
                    'hashtag': hashtag,
                    'category': category,
                    'severity': severity
                })
                features['total_severity'] += severity
                self.keyword_db.update_detection_count(hashtag, "hashtag")
        
        # Pattern matching
        for pattern, description, severity in self.compiled_patterns:
            matches = pattern.findall(content)
            if matches:
                features['matched_patterns'].append({
                    'pattern': description,
                    'matches': matches,
                    'severity': severity
                })
                features['total_severity'] += severity
        
        # Sentiment analysis
        try:
            blob = TextBlob(content)
            features['sentiment_score'] = blob.sentiment.polarity
        except:
            features['sentiment_score'] = 0.0
        
        # Determine threat level
        if features['total_severity'] >= 25:
            features['threat_level'] = 'CRITICAL'
        elif features['total_severity'] >= 15:
            features['threat_level'] = 'HIGH'
        elif features['total_severity'] >= 8:
            features['threat_level'] = 'MEDIUM'
        else:
            features['threat_level'] = 'LOW'
        
        return features
    
    def is_anti_india_content(self, content: str) -> Tuple[bool, Dict[str, Any]]:
        """Determine if content is anti-India and return analysis"""
        features = self.extract_features(content)
        
        # Content is anti-India if:
        # 1. Has matched keywords/hashtags/patterns
        # 2. Negative sentiment with matched terms
        # 3. Total severity above threshold
        
        is_anti_india = (
            len(features['matched_keywords']) > 0 or 
            len(features['matched_hashtags']) > 0 or 
            len(features['matched_patterns']) > 0 or
            (features['sentiment_score'] < -0.3 and features['total_severity'] > 3)
        )
        
        return is_anti_india, features

class EngagementAnalyzer:
    """Analyze user engagement metrics to identify viral anti-India content"""
    
    def __init__(self):
        self.engagement_thresholds = {
            'viral_likes': 1000,
            'viral_shares': 500,
            'viral_comments': 200,
            'suspicious_growth_rate': 10.0,  # 10x normal growth
            'bot_like_ratio': 0.3  # 30% bot-like engagement
        }
    
    def analyze_engagement(self, content: CampaignContent) -> Dict[str, Any]:
        """Analyze engagement metrics for suspicious patterns"""
        engagement = content.engagement
        
        analysis = {
            'total_engagement': sum(engagement.values()),
            'engagement_velocity': 0.0,
            'is_viral': False,
            'is_suspicious': False,
            'bot_score': 0.0,
            'amplification_factor': 1.0,
            'engagement_ratio': {}
        }
        
        # Calculate engagement ratios
        total = max(sum(engagement.values()), 1)
        for metric, count in engagement.items():
            analysis['engagement_ratio'][metric] = count / total
        
        # Check for viral content
        analysis['is_viral'] = (
            engagement.get('likes', 0) > self.engagement_thresholds['viral_likes'] or
            engagement.get('shares', 0) > self.engagement_thresholds['viral_shares'] or
            engagement.get('comments', 0) > self.engagement_thresholds['viral_comments']
        )
        
        # Detect suspicious engagement patterns
        likes_to_shares = engagement.get('likes', 0) / max(engagement.get('shares', 1), 1)
        comments_to_likes = engagement.get('comments', 0) / max(engagement.get('likes', 1), 1)
        
        # Suspicious if too many likes compared to shares (bot behavior)
        if likes_to_shares > 20:
            analysis['bot_score'] += 0.3
        
        # Suspicious if very few comments compared to likes
        if comments_to_likes < 0.01 and engagement.get('likes', 0) > 100:
            analysis['bot_score'] += 0.2
        
        analysis['is_suspicious'] = analysis['bot_score'] > self.engagement_thresholds['bot_like_ratio']
        
        return analysis
    
    def identify_influencers(self, contents: List[CampaignContent]) -> List[Dict[str, Any]]:
        """Identify key influencers spreading anti-India content"""
        author_metrics = defaultdict(lambda: {
            'post_count': 0,
            'total_engagement': 0,
            'avg_engagement': 0,
            'viral_posts': 0,
            'threat_score': 0,
            'platforms': set(),
            'content_samples': []
        })
        
        for content in contents:
            metrics = author_metrics[content.author]
            metrics['post_count'] += 1
            metrics['total_engagement'] += sum(content.engagement.values())
            metrics['platforms'].add(content.platform)
            metrics['content_samples'].append(content.content[:100])
            
            # Add threat score based on content severity
            if content.threat_level == 'CRITICAL':
                metrics['threat_score'] += 10
            elif content.threat_level == 'HIGH':
                metrics['threat_score'] += 5
            elif content.threat_level == 'MEDIUM':
                metrics['threat_score'] += 2
            
            # Check if post is viral
            engagement_analysis = self.analyze_engagement(content)
            if engagement_analysis['is_viral']:
                metrics['viral_posts'] += 1
        
        # Calculate averages and create influencer list
        influencers = []
        for author, metrics in author_metrics.items():
            metrics['avg_engagement'] = metrics['total_engagement'] / metrics['post_count']
            metrics['platforms'] = list(metrics['platforms'])
            
            # Influencer score based on multiple factors
            influence_score = (
                metrics['total_engagement'] * 0.4 +
                metrics['viral_posts'] * 100 +
                metrics['threat_score'] * 10 +
                len(metrics['platforms']) * 50
            )
            
            influencers.append({
                'author': author,
                'influence_score': influence_score,
                'metrics': metrics
            })
        
        return sorted(influencers, key=lambda x: x['influence_score'], reverse=True)

class CoordinatedCampaignDetector:
    """Detect coordinated anti-India campaigns"""
    
    def __init__(self, keyword_db: KeywordDatabase):
        self.keyword_db = keyword_db
        self.similarity_threshold = 0.8
        self.time_window = timedelta(hours=24)
    
    def detect_coordinated_campaigns(self, contents: List[CampaignContent]) -> List[Dict[str, Any]]:
        """Detect coordinated campaigns using various signals"""
        campaigns = []
        
        # Group by time windows
        time_grouped = defaultdict(list)
        for content in contents:
            time_key = content.timestamp.replace(hour=0, minute=0, second=0)
            time_grouped[time_key].append(content)
        
        for time_key, time_contents in time_grouped.items():
            if len(time_contents) < 3:  # Need at least 3 posts for coordination
                continue
            
            # Detect hashtag coordination
            hashtag_campaigns = self._detect_hashtag_coordination(time_contents)
            campaigns.extend(hashtag_campaigns)
            
            # Detect content similarity coordination
            similarity_campaigns = self._detect_content_similarity(time_contents)
            campaigns.extend(similarity_campaigns)
            
            # Detect timing coordination
            timing_campaigns = self._detect_timing_coordination(time_contents)
            campaigns.extend(timing_campaigns)
        
        return campaigns
    
    def _detect_hashtag_coordination(self, contents: List[CampaignContent]) -> List[Dict[str, Any]]:
        """Detect coordination through synchronized hashtag usage"""
        hashtag_usage = defaultdict(list)
        
        for content in contents:
            for hashtag in content.hashtags:
                hashtag_usage[hashtag.lower()].append(content)
        
        campaigns = []
        for hashtag, hashtag_contents in hashtag_usage.items():
            if len(hashtag_contents) >= 5:  # Same hashtag used by 5+ accounts
                # Check if these are different accounts
                unique_authors = set(c.author for c in hashtag_contents)
                if len(unique_authors) >= 3:
                    campaigns.append({
                        'type': 'hashtag_coordination',
                        'hashtag': hashtag,
                        'accounts_involved': list(unique_authors),
                        'post_count': len(hashtag_contents),
                        'time_span': self._calculate_time_span(hashtag_contents),
                        'platforms': list(set(c.platform for c in hashtag_contents)),
                        'threat_level': self._calculate_campaign_threat_level(hashtag_contents)
                    })
        
        return campaigns
    
    def _detect_content_similarity(self, contents: List[CampaignContent]) -> List[Dict[str, Any]]:
        """Detect coordination through similar content"""
        campaigns = []
        processed = set()
        
        for i, content1 in enumerate(contents):
            if i in processed:
                continue
            
            similar_contents = [content1]
            for j, content2 in enumerate(contents[i+1:], i+1):
                if j in processed:
                    continue
                
                similarity = self._calculate_content_similarity(content1.content, content2.content)
                if similarity > self.similarity_threshold:
                    similar_contents.append(content2)
                    processed.add(j)
            
            if len(similar_contents) >= 3:
                unique_authors = set(c.author for c in similar_contents)
                if len(unique_authors) >= 2:
                    campaigns.append({
                        'type': 'content_similarity',
                        'similar_posts': len(similar_contents),
                        'accounts_involved': list(unique_authors),
                        'content_template': content1.content[:200],
                        'platforms': list(set(c.platform for c in similar_contents)),
                        'threat_level': self._calculate_campaign_threat_level(similar_contents)
                    })
                    processed.add(i)
        
        return campaigns
    
    def _detect_timing_coordination(self, contents: List[CampaignContent]) -> List[Dict[str, Any]]:
        """Detect coordination through synchronized timing"""
        campaigns = []
        
        # Group by 1-hour windows
        hour_groups = defaultdict(list)
        for content in contents:
            hour_key = content.timestamp.replace(minute=0, second=0, microsecond=0)
            hour_groups[hour_key].append(content)
        
        for hour, hour_contents in hour_groups.items():
            if len(hour_contents) >= 5:  # 5+ posts in same hour
                unique_authors = set(c.author for c in hour_contents)
                if len(unique_authors) >= 3:  # Different accounts
                    campaigns.append({
                        'type': 'timing_coordination',
                        'time_window': hour.isoformat(),
                        'posts_in_window': len(hour_contents),
                        'accounts_involved': list(unique_authors),
                        'platforms': list(set(c.platform for c in hour_contents)),
                        'threat_level': self._calculate_campaign_threat_level(hour_contents)
                    })
        
        return campaigns
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two pieces of content"""
        # Simple Jaccard similarity on words
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_time_span(self, contents: List[CampaignContent]) -> str:
        """Calculate time span of coordinated activity"""
        timestamps = [c.timestamp for c in contents]
        time_span = max(timestamps) - min(timestamps)
        return str(time_span)
    
    def _calculate_campaign_threat_level(self, contents: List[CampaignContent]) -> str:
        """Calculate overall threat level for campaign"""
        threat_scores = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
        avg_score = sum(threat_scores.get(c.threat_level, 1) for c in contents) / len(contents)
        
        if avg_score >= 3.5:
            return 'CRITICAL'
        elif avg_score >= 2.5:
            return 'HIGH'
        elif avg_score >= 1.5:
            return 'MEDIUM'
        else:
            return 'LOW'

class RealTimeMonitor:
    """Real-time monitoring system for multiple platforms"""
    
    def __init__(self, keyword_db: KeywordDatabase, nlp_processor: NLPProcessor):
        self.keyword_db = keyword_db
        self.nlp_processor = nlp_processor
        self.engagement_analyzer = EngagementAnalyzer()
        self.campaign_detector = CoordinatedCampaignDetector(keyword_db)
        self.monitoring_active = False
        self.detected_contents = []
        self.alerts = []
        
        # Platform APIs (would need real API keys)
        self.platform_configs = {
            'twitter': {'api_key': None, 'enabled': False},
            'facebook': {'api_key': None, 'enabled': False},
            'instagram': {'api_key': None, 'enabled': False},
            'reddit': {'api_key': None, 'enabled': True},  # Can use public API
            'youtube': {'api_key': None, 'enabled': False}
        }
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        self.monitoring_active = True
        
        # Start monitoring threads for each platform
        threads = []
        for platform, config in self.platform_configs.items():
            if config['enabled']:
                thread = threading.Thread(
                    target=self._monitor_platform, 
                    args=(platform,),
                    daemon=True
                )
                threads.append(thread)
                thread.start()
        
        print(f"Started monitoring {len(threads)} platforms")
        return threads
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.monitoring_active = False
    
    def _monitor_platform(self, platform: str):
        """Monitor specific platform for anti-India content"""
        while self.monitoring_active:
            try:
                if platform == 'reddit':
                    self._monitor_reddit()
                elif platform == 'twitter':
                    self._monitor_twitter()
                # Add other platforms as APIs become available
                
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Error monitoring {platform}: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _monitor_reddit(self):
        """Monitor Reddit for anti-India content"""
        # Simulate Reddit monitoring (would use actual Reddit API)
        keywords = [kw[0] for kw in self.keyword_db.get_active_keywords()[:5]]
        
        for keyword in keywords:
            try:
                # Simulate finding posts
                simulated_posts = self._simulate_reddit_posts(keyword)
                
                for post_data in simulated_posts:
                    is_anti_india, features = self.nlp_processor.is_anti_india_content(post_data['content'])
                    
                    if is_anti_india:
                        content = CampaignContent(
                            id=post_data['id'],
                            platform='reddit',
                            content=post_data['content'],
                            author=post_data['author'],
                            timestamp=datetime.now(),
                            engagement=post_data['engagement'],
                            hashtags=features.get('hashtags_found', []),
                            mentions=features.get('mentions_found', []),
                            url=post_data['url'],
                            sentiment_score=features['sentiment_score'],
                            threat_level=features['threat_level'],
                            keywords_matched=[kw['keyword'] for kw in features['matched_keywords']]
                        )
                        
                        self.detected_contents.append(content)
                        self._check_alert_conditions(content, features)
                
            except Exception as e:
                print(f"Error monitoring Reddit for '{keyword}': {e}")
    
    def _simulate_reddit_posts(self, keyword: str) -> List[Dict[str, Any]]:
        """Simulate Reddit posts (replace with actual API calls)"""
        import random
        
        posts = []
        for i in range(random.randint(1, 3)):
            posts.append({
                'id': f"reddit_{int(time.time())}_{i}",
                'content': f"Post discussing {keyword} and related anti-India sentiment",
                'author': f"user_{random.randint(1000, 9999)}",
                'engagement': {
                    'upvotes': random.randint(1, 500),
                    'comments': random.randint(0, 50),
                    'shares': random.randint(0, 20)
                },
                'url': f"https://reddit.com/r/example/post_{i}"
            })
        
        return posts
    
    def _check_alert_conditions(self, content: CampaignContent, features: Dict[str, Any]):
        """Check if content meets alert conditions"""
        alert_triggered = False
        alert_reasons = []
        
        # High threat level content
        if content.threat_level in ['HIGH', 'CRITICAL']:
            alert_triggered = True
            alert_reasons.append(f"High threat level: {content.threat_level}")
        
        # High engagement
        engagement_analysis = self.engagement_analyzer.analyze_engagement(content)
        if engagement_analysis['is_viral']:
            alert_triggered = True
            alert_reasons.append("Viral engagement detected")
        
        # Multiple severe keywords
        if features['total_severity'] > 20:
            alert_triggered = True
            alert_reasons.append(f"High severity score: {features['total_severity']}")
        
        if alert_triggered:
            alert = {
                'timestamp': datetime.now(),
                'content_id': content.id,
                'platform': content.platform,
                'author': content.author,
                'threat_level': content.threat_level,
                'reasons': alert_reasons,
                'content_preview': content.content[:200],
                'url': content.url
            }
            self.alerts.append(alert)
            print(f"ALERT: {content.threat_level} threat detected on {content.platform}")
    
    def get_recent_detections(self, hours: int = 24) -> List[CampaignContent]:
        """Get recent detections within specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [c for c in self.detected_contents if c.timestamp >= cutoff_time]
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts within specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [a for a in self.alerts if a['timestamp'] >= cutoff_time]
    
    def generate_threat_report(self) -> Dict[str, Any]:
        """Generate comprehensive threat report"""
        recent_contents = self.get_recent_detections(24)
        recent_alerts = self.get_recent_alerts(24)
        
        # Detect coordinated campaigns
        campaigns = self.campaign_detector.detect_coordinated_campaigns(recent_contents)
        
        # Identify influencers
        influencers = self.engagement_analyzer.identify_influencers(recent_contents)
        
        # Platform breakdown
        platform_stats = defaultdict(int)
        for content in recent_contents:
            platform_stats[content.platform] += 1
        
        # Threat level breakdown
        threat_stats = defaultdict(int)
        for content in recent_contents:
            threat_stats[content.threat_level] += 1
        
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'summary': {
                'total_detections_24h': len(recent_contents),
                'total_alerts_24h': len(recent_alerts),
                'coordinated_campaigns': len(campaigns),
                'top_influencers': len([i for i in influencers if i['influence_score'] > 1000])
            },
            'platform_breakdown': dict(platform_stats),
            'threat_level_breakdown': dict(threat_stats),
            'coordinated_campaigns': campaigns[:10],  # Top 10 campaigns
            'top_influencers': influencers[:20],  # Top 20 influencers
            'recent_alerts': recent_alerts,
            'trending_keywords': self._get_trending_keywords(recent_contents),
            'recommendations': self._generate_recommendations(recent_contents, campaigns, influencers)
        }
        
        return report
    
    def _get_trending_keywords(self, contents: List[CampaignContent]) -> List[Dict[str, Any]]:
        """Get trending keywords from recent detections"""
        keyword_counts = defaultdict(int)
        
        for content in contents:
            for keyword in content.keywords_matched:
                keyword_counts[keyword] += 1
        
        trending = []
        for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            trending.append({
                'keyword': keyword,
                'mentions': count,
                'trend_score': count * 10  # Simple trend score
            })
        
        return trending
    
    def _generate_recommendations(self, contents: List[CampaignContent], 
                                 campaigns: List[Dict[str, Any]], 
                                 influencers: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # High threat content recommendations
        critical_content = [c for c in contents if c.threat_level == 'CRITICAL']
        if critical_content:
            recommendations.append(f"Immediate action required: {len(critical_content)} critical threat posts detected")
        
        # Coordinated campaign recommendations
        high_threat_campaigns = [c for c in campaigns if c.get('threat_level') in ['HIGH', 'CRITICAL']]
        if high_threat_campaigns:
            recommendations.append(f"Investigate {len(high_threat_campaigns)} high-threat coordinated campaigns")
        
        # Influencer monitoring recommendations
        high_influence = [i for i in influencers if i['influence_score'] > 5000]
        if high_influence:
            recommendations.append(f"Monitor {len(high_influence)} high-influence accounts spreading anti-India content")
        
        # Platform-specific recommendations
        platform_stats = defaultdict(int)
        for content in contents:
            platform_stats[content.platform] += 1
        
        if platform_stats:
            top_platform = max(platform_stats.items(), key=lambda x: x[1])
            recommendations.append(f"Focus monitoring efforts on {top_platform[0]} ({top_platform[1]} detections)")
        
        return recommendations

# Example usage and testing
if __name__ == "__main__":
    # Initialize components
    keyword_db = KeywordDatabase()
    nlp_processor = NLPProcessor(keyword_db)
    monitor = RealTimeMonitor(keyword_db, nlp_processor)
    
    # Test content analysis
    test_content = "India is a terrorist state and should be boycotted by all nations #BoycottIndia #IndianTerrorism"
    is_anti_india, features = nlp_processor.is_anti_india_content(test_content)
    
    print(f"Content: {test_content}")
    print(f"Is Anti-India: {is_anti_india}")
    print(f"Threat Level: {features['threat_level']}")
    print(f"Matched Keywords: {features['matched_keywords']}")
    print(f"Total Severity: {features['total_severity']}")
