"""
Enhanced Engagement Analysis System
Analyzes social media engagement patterns to detect viral anti-India campaigns
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json
import re

class EngagementAnalyzer:
    def __init__(self, db_path=None):
        # Default to canonical DATABASE_PATH if available
        if db_path is None:
            try:
                from database import DATABASE_PATH
                self.db_path = DATABASE_PATH
            except Exception:
                self.db_path = "campaign_data.db"
        else:
            self.db_path = db_path
        self.init_engagement_tables()
    
    def init_engagement_tables(self):
        """Initialize engagement tracking tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Engagement metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS engagement_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id INTEGER,
                platform TEXT NOT NULL,
                likes INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                retweets INTEGER DEFAULT 0,
                views INTEGER DEFAULT 0,
                reach INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0.0,
                virality_score REAL DEFAULT 0.0,
                collected_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (content_id) REFERENCES articles (id)
            )
        ''')
        
        # Influencer tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS influencers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                platform TEXT NOT NULL,
                display_name TEXT,
                follower_count INTEGER DEFAULT 0,
                verified BOOLEAN DEFAULT 0,
                account_created DATE,
                bio TEXT,
                location TEXT,
                influence_score REAL DEFAULT 0.0,
                anti_india_activity_count INTEGER DEFAULT 0,
                last_activity DATETIME,
                threat_level TEXT DEFAULT 'LOW',
                UNIQUE(username, platform)
            )
        ''')
        
        # Network connections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS network_connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_influencer_id INTEGER,
                target_influencer_id INTEGER,
                connection_type TEXT,  -- follows, mentions, retweets, etc.
                strength REAL DEFAULT 1.0,
                first_observed DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_observed DATETIME DEFAULT CURRENT_TIMESTAMP,
                interaction_count INTEGER DEFAULT 1,
                FOREIGN KEY (source_influencer_id) REFERENCES influencers (id),
                FOREIGN KEY (target_influencer_id) REFERENCES influencers (id)
            )
        ''')
        
        # Campaign coordination table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaign_coordination (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_name TEXT,
                hashtag TEXT,
                start_time DATETIME,
                end_time DATETIME,
                participant_count INTEGER DEFAULT 0,
                total_posts INTEGER DEFAULT 0,
                coordination_score REAL DEFAULT 0.0,
                geographic_spread TEXT,  -- JSON array of countries
                platform_spread TEXT,   -- JSON array of platforms
                threat_level TEXT DEFAULT 'LOW',
                status TEXT DEFAULT 'ACTIVE'
            )
        ''')
        
        # Trending patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trending_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword_or_hashtag TEXT NOT NULL,
                platform TEXT NOT NULL,
                hour_timestamp DATETIME NOT NULL,
                mention_count INTEGER DEFAULT 0,
                engagement_sum INTEGER DEFAULT 0,
                unique_users INTEGER DEFAULT 0,
                growth_rate REAL DEFAULT 0.0,
                anomaly_score REAL DEFAULT 0.0,
                UNIQUE(keyword_or_hashtag, platform, hour_timestamp)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def calculate_engagement_score(self, metrics: Dict) -> float:
        """Calculate comprehensive engagement score"""
        likes = metrics.get('likes', 0)
        shares = metrics.get('shares', 0)
        comments = metrics.get('comments', 0)
        retweets = metrics.get('retweets', 0)
        views = metrics.get('views', 1)  # Avoid division by zero
        
        # Weighted engagement calculation
        weighted_engagement = (
            likes * 1.0 +
            shares * 3.0 +  # Shares are more valuable
            comments * 2.0 +
            retweets * 2.5
        )
        
        engagement_rate = weighted_engagement / max(views, 1)
        
        # Virality calculation
        virality_score = 0.0
        if shares > 0 or retweets > 0:
            virality_score = np.log1p(shares + retweets) * engagement_rate
        
        return {
            'engagement_rate': engagement_rate,
            'virality_score': virality_score,
            'total_engagement': weighted_engagement
        }
    
    def add_engagement_data(self, content_id: int, platform: str, metrics: Dict):
        """Add engagement data for content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        engagement_scores = self.calculate_engagement_score(metrics)
        
        cursor.execute('''
            INSERT OR REPLACE INTO engagement_metrics 
            (content_id, platform, likes, shares, comments, retweets, views, reach, 
             engagement_rate, virality_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            content_id, platform,
            metrics.get('likes', 0),
            metrics.get('shares', 0), 
            metrics.get('comments', 0),
            metrics.get('retweets', 0),
            metrics.get('views', 0),
            metrics.get('reach', 0),
            engagement_scores['engagement_rate'],
            engagement_scores['virality_score']
        ))
        
        conn.commit()
        conn.close()
        
        return engagement_scores
    
    def track_influencer(self, username: str, platform: str, profile_data: Dict):
        """Track influencer profile and activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate influence score based on followers and engagement
        follower_count = profile_data.get('follower_count', 0)
        influence_score = np.log1p(follower_count) * (1.0 if profile_data.get('verified', False) else 0.8)
        
        cursor.execute('''
            INSERT OR REPLACE INTO influencers 
            (username, platform, display_name, follower_count, verified, bio, location, 
             influence_score, last_activity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            username, platform,
            profile_data.get('display_name', ''),
            follower_count,
            profile_data.get('verified', False),
            profile_data.get('bio', ''),
            profile_data.get('location', ''),
            influence_score
        ))
        
        conn.commit()
        conn.close()
        
        return influence_score
    
    def detect_coordinated_campaigns(self, time_window_hours: int = 24) -> List[Dict]:
        """Detect coordinated campaigns based on timing and content patterns"""
        conn = sqlite3.connect(self.db_path)
        
        # Query for potential coordinated activity
        query = '''
            SELECT 
                a.keywords_found,
                a.published_date,
                a.source,
                COUNT(*) as post_count,
                GROUP_CONCAT(a.url) as urls,
                AVG(em.engagement_rate) as avg_engagement,
                SUM(em.virality_score) as total_virality
            FROM articles a
            LEFT JOIN engagement_metrics em ON a.id = em.content_id
            WHERE a.published_date >= datetime('now', '-{} hours')
            AND a.keywords_found IS NOT NULL
            GROUP BY 
                a.keywords_found,
                DATE(a.published_date),
                ROUND(julianday(a.published_date) * 24) -- Group by hour
            HAVING post_count >= 3  -- At least 3 posts with same keywords in same hour
            ORDER BY post_count DESC, total_virality DESC
        '''.format(time_window_hours)
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        campaigns = []
        for _, row in df.iterrows():
            # Parse keywords
            try:
                keywords = json.loads(row['keywords_found']) if row['keywords_found'] else []
            except:
                keywords = []
            
            # Calculate coordination score
            coordination_score = (
                row['post_count'] * 0.3 +  # Volume
                (row['avg_engagement'] or 0) * 0.4 +  # Engagement
                (row['total_virality'] or 0) * 0.3  # Virality
            )
            
            # Determine threat level
            threat_level = "LOW"
            if coordination_score > 10:
                threat_level = "HIGH"
            elif coordination_score > 5:
                threat_level = "MEDIUM"
            
            campaigns.append({
                'keywords': keywords,
                'post_count': row['post_count'],
                'time_period': row['published_date'],
                'platforms': [row['source']],
                'coordination_score': coordination_score,
                'threat_level': threat_level,
                'avg_engagement': row['avg_engagement'] or 0,
                'total_virality': row['total_virality'] or 0,
                'sample_urls': row['urls'].split(',')[:5] if row['urls'] else []
            })
        
        return campaigns
    
    def identify_key_influencers(self, min_influence_score: float = 5.0) -> List[Dict]:
        """Identify key influencers spreading anti-India content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                username, platform, display_name, follower_count, verified,
                influence_score, anti_india_activity_count, threat_level, last_activity
            FROM influencers
            WHERE influence_score >= ? AND anti_india_activity_count > 0
            ORDER BY influence_score DESC, anti_india_activity_count DESC
            LIMIT 50
        ''', (min_influence_score,))
        
        results = cursor.fetchall()
        conn.close()
        
        influencers = []
        for row in results:
            influencers.append({
                'username': row[0],
                'platform': row[1],
                'display_name': row[2],
                'follower_count': row[3],
                'verified': bool(row[4]),
                'influence_score': row[5],
                'activity_count': row[6],
                'threat_level': row[7],
                'last_activity': row[8]
            })
        
        return influencers
    
    def analyze_network_connections(self, influencer_username: str, platform: str) -> Dict:
        """Analyze network connections for an influencer"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                i2.username, i2.platform, i2.influence_score,
                nc.connection_type, nc.strength, nc.interaction_count
            FROM network_connections nc
            JOIN influencers i1 ON nc.source_influencer_id = i1.id
            JOIN influencers i2 ON nc.target_influencer_id = i2.id
            WHERE i1.username = ? AND i1.platform = ?
            ORDER BY nc.strength DESC, i2.influence_score DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=(influencer_username, platform))
        conn.close()
        
        if df.empty:
            return {'connections': [], 'network_strength': 0.0, 'reach_potential': 0}
        
        connections = df.to_dict('records')
        network_strength = df['strength'].sum()
        reach_potential = df['influence_score'].sum()
        
        return {
            'connections': connections,
            'network_strength': network_strength,
            'reach_potential': reach_potential,
            'connection_count': len(connections)
        }
    
    def detect_trending_anomalies(self, lookback_hours: int = 48) -> List[Dict]:
        """Detect unusual trending patterns that might indicate campaigns"""
        conn = sqlite3.connect(self.db_path)
        
        # Calculate average baseline and detect anomalies
        # Simplified approach - calculate standard deviation in Python instead of SQL
        # First get the baseline data
        baseline_query = '''
            SELECT 
                keyword_or_hashtag,
                platform,
                mention_count,
                AVG(mention_count) OVER (PARTITION BY keyword_or_hashtag, platform) as avg_mentions
            FROM trending_patterns
            WHERE hour_timestamp >= datetime('now', '-{} hours')
        '''.format(lookback_hours)
        
        recent_query = '''
            SELECT 
                keyword_or_hashtag,
                platform,
                mention_count,
                hour_timestamp,
                engagement_sum,
                unique_users
            FROM trending_patterns
            WHERE hour_timestamp >= datetime('now', '-6 hours')
        '''
        
        try:
            baseline_df = pd.read_sql_query(baseline_query, conn)
            recent_df = pd.read_sql_query(recent_query, conn)
            
            # Calculate standard deviation in pandas
            baseline_stats = baseline_df.groupby(['keyword_or_hashtag', 'platform']).agg({
                'mention_count': ['mean', 'std', 'count']
            }).reset_index()
            
            # Flatten column names
            baseline_stats.columns = ['keyword_or_hashtag', 'platform', 'avg_mentions', 'std_mentions', 'count']
            
            # Filter for sufficient data points
            baseline_stats = baseline_stats[baseline_stats['count'] >= 12]
            
            # Merge with recent data
            merged_df = recent_df.merge(
                baseline_stats[['keyword_or_hashtag', 'platform', 'avg_mentions', 'std_mentions']], 
                on=['keyword_or_hashtag', 'platform'], 
                how='inner'
            )
            
            # Calculate z-score
            merged_df['z_score'] = (merged_df['mention_count'] - merged_df['avg_mentions']) / merged_df['std_mentions'].replace(0, 1)
            
            # Filter for anomalies
            df = merged_df[abs(merged_df['z_score']) > 2.0].sort_values('z_score', key=abs, ascending=False)
            
        except Exception as e:
            print(f"Error in anomaly detection query: {e}")
            # Return empty dataframe if query fails
            df = pd.DataFrame(columns=['keyword_or_hashtag', 'platform', 'mention_count', 'hour_timestamp', 
                                     'engagement_sum', 'unique_users', 'avg_mentions', 'std_mentions', 'z_score'])
        conn.close()
        
        anomalies = []
        for _, row in df.iterrows():
            anomaly_strength = abs(row['z_score']) if pd.notna(row['z_score']) else 0
            
            threat_level = "LOW"
            if anomaly_strength > 4:
                threat_level = "HIGH"
            elif anomaly_strength > 3:
                threat_level = "MEDIUM"
            
            anomalies.append({
                'keyword_or_hashtag': row['keyword_or_hashtag'],
                'platform': row['platform'],
                'current_mentions': row['mention_count'],
                'average_mentions': row['avg_mentions'],
                'anomaly_strength': anomaly_strength,
                'threat_level': threat_level,
                'timestamp': row['hour_timestamp'],
                'engagement_sum': row['engagement_sum'],
                'unique_users': row['unique_users']
            })
        
        return anomalies
    
    def generate_engagement_report(self, days: int = 7) -> Dict:
        """Generate comprehensive engagement analysis report"""
        conn = sqlite3.connect(self.db_path)
        
        # Top engaging content
        top_content_query = '''
            SELECT 
                a.title, a.source, a.url, a.published_date,
                em.engagement_rate, em.virality_score,
                em.likes, em.shares, em.comments, em.retweets
            FROM articles a
            JOIN engagement_metrics em ON a.id = em.content_id
            WHERE a.published_date >= datetime('now', '-{} days')
            ORDER BY em.virality_score DESC
            LIMIT 20
        '''.format(days)
        
        # Platform performance
        platform_query = '''
            SELECT 
                em.platform,
                COUNT(*) as content_count,
                AVG(em.engagement_rate) as avg_engagement,
                SUM(em.virality_score) as total_virality,
                SUM(em.likes + em.shares + em.comments + em.retweets) as total_interactions
            FROM engagement_metrics em
            JOIN articles a ON em.content_id = a.id
            WHERE a.published_date >= datetime('now', '-{} days')
            GROUP BY em.platform
            ORDER BY total_virality DESC
        '''.format(days)
        
        # Trending keywords
        trending_query = '''
            SELECT 
                tp.keyword_or_hashtag,
                tp.platform,
                SUM(tp.mention_count) as total_mentions,
                AVG(tp.engagement_sum) as avg_engagement,
                MAX(tp.anomaly_score) as max_anomaly
            FROM trending_patterns tp
            WHERE tp.hour_timestamp >= datetime('now', '-{} days')
            GROUP BY tp.keyword_or_hashtag, tp.platform
            ORDER BY total_mentions DESC
            LIMIT 30
        '''.format(days)
        
        top_content = pd.read_sql_query(top_content_query, conn).to_dict('records')
        platform_performance = pd.read_sql_query(platform_query, conn).to_dict('records')
        trending_keywords = pd.read_sql_query(trending_query, conn).to_dict('records')
        
        conn.close()
        
        # Get coordinated campaigns and influencers
        coordinated_campaigns = self.detect_coordinated_campaigns(days * 24)
        key_influencers = self.identify_key_influencers()
        trending_anomalies = self.detect_trending_anomalies(days * 24)
        
        return {
            'report_period_days': days,
            'generated_at': datetime.now().isoformat(),
            'top_viral_content': top_content,
            'platform_performance': platform_performance,
            'trending_keywords': trending_keywords,
            'coordinated_campaigns': coordinated_campaigns,
            'key_influencers': key_influencers[:10],  # Top 10
            'trending_anomalies': trending_anomalies,
            'summary': {
                'total_campaigns_detected': len(coordinated_campaigns),
                'high_threat_campaigns': len([c for c in coordinated_campaigns if c['threat_level'] == 'HIGH']),
                'active_influencers': len(key_influencers),
                'trending_anomalies_count': len(trending_anomalies)
            }
        }
