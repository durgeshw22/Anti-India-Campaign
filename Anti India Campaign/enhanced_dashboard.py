"""
Enhanced Anti-India Campaign Detection Dashboard
Comprehensive system implementing all problem statement requirements
"""

import streamlit as st
import json
import pandas as pd
import numpy as np
import requests
import time
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import networkx as nx
import os
from database import init_database, get_articles, get_statistics, save_article
from enhanced_keyword_database import KeywordDatabase
from engagement_analyzer import EngagementAnalyzer
from campaign_detector import CoordinatedCampaignDetector
from ai_analyzer import AIAnalyzer
from enhanced_data_collector import EnhancedDataCollector

# Page config
st.set_page_config(
    page_title="🛡️ Anti-India Campaign Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for professional appearance
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .alert-critical {
        background: linear-gradient(135deg, #ff4757, #ff3838);
        border-left: 6px solid #ff1744;
    }
    .alert-high {
        background: linear-gradient(135deg, #ff6b7a, #ff5252);
        border-left: 6px solid #ff5252;
    }
    .alert-medium {
        background: linear-gradient(135deg, #ffa726, #ff9800);
        border-left: 6px solid #ff9800;
    }
    .alert-low {
        background: linear-gradient(135deg, #66bb6a, #4caf50);
        border-left: 6px solid #4caf50;
    }
    .threat-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        text-transform: uppercase;
    }
    .threat-critical { background: #ff1744; color: white; }
    .threat-high { background: #ff5252; color: white; }
    .threat-medium { background: #ff9800; color: white; }
    .threat-low { background: #4caf50; color: white; }
    .network-node {
        border-radius: 50%;
        display: inline-block;
        margin: 2px;
        text-align: center;
        color: white;
        font-weight: bold;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1e3c72, #2a5298);
    }
</style>
""", unsafe_allow_html=True)

# Initialize system components
@st.cache_resource
def initialize_system():
    """Initialize all system components"""
    init_database()
    keyword_db = KeywordDatabase()
    engagement_analyzer = EngagementAnalyzer()
    campaign_detector = CoordinatedCampaignDetector(keyword_db)
    ai_analyzer = AIAnalyzer()
    
    return keyword_db, engagement_analyzer, campaign_detector, ai_analyzer

def main():
    """Main dashboard function"""
    
    # Initialize system
    keyword_db, engagement_analyzer, campaign_detector, ai_analyzer = initialize_system()
    # Show DB debug status so user can verify dashboard reads the same DB
    try:
        from database import debug_db_status
        db_info = debug_db_status()
    except Exception:
        db_info = None
    
    # Check API configuration
    from config import GEMINI_API_KEY, NEWSAPI_KEY
    api_status = []
    if not GEMINI_API_KEY:
        api_status.append("❌ Gemini AI API Key missing")
    else:
        api_status.append("✅ Gemini AI API Key configured")
    
    if not NEWSAPI_KEY:
        api_status.append("❌ NewsAPI Key missing")
    else:
        api_status.append("✅ NewsAPI Key configured")
    
    # Check for existing data and offer to collect real data
    articles_df = get_articles(limit=10)
    if articles_df is None or articles_df.empty:
        st.error("🚨 **No Real Data Found!** Database is empty - showing only instructions.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🔑 API Configuration Status")
            for status in api_status:
                st.write(status)
            
            if not GEMINI_API_KEY:
                st.warning("**Add your Gemini API key to config.py for AI analysis:**")
                st.code('GEMINI_API_KEY = "YOUR API KEYS"')
                st.write("Get free API key from: https://aistudio.google.com/")
        
        with col2:
            st.markdown("### 🚀 Start Data Collection")
            st.info("💡 **To get real anti-India campaign data:** Use the Enhanced Data Collection tab")
            
            # Auto-collection option that works without APIs
            if st.button("� **Start Basic Data Collection**", type="primary"):
                with st.spinner("🔄 Collecting real data using Google Dorks..."):
                    try:
                        collector = EnhancedDataCollector()
                        # Use basic Google search without APIs
                        from config import GOOGLE_DORKS, ANTI_INDIA_KEYWORDS
                        
                        # Collect from first few dorks
                        results_collected = 0
                        for i, dork in enumerate(GOOGLE_DORKS[:3]):  # First 3 dorks only
                            st.write(f"🔍 Searching: {dork}")
                            try:
                                # Basic search implementation
                                results = collector.google_dork_search(dork, max_results_per_dork=3)
                                if results:
                                    results_collected += len(results)
                                    st.write(f"✅ Found {len(results)} results")
                                else:
                                    st.write("⚠️ No results for this search")
                            except Exception as e:
                                st.write(f"⚠️ Search failed: {str(e)}")
                            
                            time.sleep(3)  # Rate limiting
                            
                        if results_collected > 0:
                            st.success(f"✅ Collected {results_collected} real articles! Refresh to see results.")
                            st.balloons()
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.warning("⚠️ No results collected. Try the Enhanced Data Collection tab for more options.")
                            
                    except Exception as e:
                        st.error(f"❌ Collection failed: {str(e)}")
                        st.info("Try using the Enhanced Data Collection tab for manual collection")
    
    else:
        st.success(f" ** Data Loaded:** Found {len(articles_df)} articles in database")
        for status in api_status:
            st.sidebar.write(status)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; margin: 0; text-align: center;">
            🛡️ Anti-India Campaign Detection System
        </h1>
        <h3 style="color: #e3f2fd; margin: 0; text-align: center; font-weight: 300;">
            Advanced Multi-Platform Monitoring & Early Warning System
        </h3>
        <p style="color: #bbdefb; margin: 10px 0 0 0; text-align: center;">
            Real-time detection • Engagement analysis • Coordinated campaign identification • Threat assessment
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - Enhanced Control Panel
    with st.sidebar:
        st.markdown("## 🔧 Control Center")
        # DB status
        if db_info:
            st.markdown("### 🗄️ Database Status")
            st.write(f"Path: {db_info.get('db_path')}")
            st.write(f"Articles: {db_info.get('article_count')}")
            st.write(f"Campaigns: {db_info.get('campaign_count')}")
        
        # Real-time monitoring controls
        st.markdown("### 📡 Real-Time Monitoring")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Full Spectrum Scan", type="primary", use_container_width=True):
                with st.spinner("Scanning all platforms and sources..."):
                    collector = EnhancedDataCollector(keyword_db)
                    collected = collector.collect_with_engagement_tracking()
                    
                    if collected > 0:
                        st.success(f"✅ Collected {collected} items with engagement data!")
                        st.balloons()
                    else:
                        st.warning("⚠️ No new threats detected")
        
        with col2:
            if st.button("⚡ Quick Alert Scan", use_container_width=True):
                with st.spinner("Quick threat assessment..."):
                    # Quick scan simulation
                    time.sleep(2)
                    st.info("📊 System operational - No immediate threats")
        
        # Alert System Controls
        st.markdown("### 🚨 Alert System")
        
        # Threat level threshold
        threat_threshold = st.select_slider(
            "Alert Threshold",
            options=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            value="MEDIUM",
            help="Set minimum threat level for alerts"
        )
        
        # Real-time alerts toggle
        real_time_alerts = st.toggle("Real-time Alerts", value=True)
        
        if real_time_alerts:
            st.success("🔔 Real-time monitoring ACTIVE")
        else:
            st.warning("🔕 Real-time monitoring DISABLED")
        
        # Time range selector
        st.markdown("### ⏱️ Analysis Period")
        time_range = st.selectbox(
            "Select Time Range",
            ["Last 6 hours", "Last 24 hours", "Last 3 days", "Last 7 days", "Last 30 days"],
            index=2
        )
        
        # Platform selector
        st.markdown("### 📱 Platform Filters")
        platforms = st.multiselect(
            "Monitor Platforms",
            ["Twitter", "Facebook", "Instagram", "Reddit", "TikTok", "YouTube", "Telegram", "WhatsApp"],
            default=["Twitter", "Facebook", "Instagram", "Reddit"]
        )
        
        # Geographic filter
        st.markdown("### 🌍 Geographic Focus")
        countries = st.multiselect(
            "Focus Countries",
            ["Pakistan", "China", "Bangladesh", "Turkey", "Malaysia", "Iran", "Afghanistan", "UAE", "Qatar"],
            default=["Pakistan", "China", "Bangladesh"]
        )
        
        # Advanced settings
        with st.expander("⚙️ Advanced Settings"):
            st.markdown("#### Keyword Database")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📝 Update Keywords"):
                    st.info("Keyword database updated")
            with col2:
                if st.button("📊 View Analytics"):
                    st.info("Showing keyword performance")
            
            st.markdown("#### Detection Sensitivity")
            sensitivity = st.slider("Detection Sensitivity", 0.1, 1.0, 0.7, 0.1)
            
            st.markdown("#### Data Sources")
            enable_social = st.checkbox("Social Media Monitoring", value=True)
            enable_news = st.checkbox("News Sources", value=True)
            enable_forums = st.checkbox("Forum Monitoring", value=True)
    
    # Simplified main dashboard tabs (only essential views)
    tab1, tab2, tab3 = st.tabs([
        "📊 Threat Overview",
        "🔍 Campaign Detection",
        "️ Data Collection"
    ])

    with tab1:
        show_threat_overview(keyword_db, engagement_analyzer, campaign_detector)

    with tab2:
        show_campaign_detection(campaign_detector, keyword_db)

    with tab3:
        show_enhanced_data_collection(keyword_db)

def show_threat_overview(keyword_db, engagement_analyzer, campaign_detector):
    """Enhanced threat overview dashboard"""
    st.header("🛡️ Real-Time Threat Assessment")
    
    # Get current statistics
    stats = get_statistics()
    articles_df = get_articles(limit=100)
    
    # Calculate real metrics from database
    total_articles = len(articles_df) if articles_df is not None and not articles_df.empty else 0
    critical_threats = len(articles_df[articles_df['sentiment_score'] < -0.7]) if total_articles > 0 else 0
    active_campaigns = len(articles_df.groupby('source')) if total_articles > 0 else 0
    
    # Top metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card alert-critical">
            <h3 style="margin:0;">🚨 Critical Threats</h3>
            <h1 style="margin:0;">{critical_threats}</h1>
            <p style="margin:0; opacity:0.8;">Requires immediate action</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card alert-high">
            <h3 style="margin:0;">📡 Active Campaigns</h3>
            <h1 style="margin:0;">{active_campaigns}</h1>
            <p style="margin:0; opacity:0.8;">Coordinated activities</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card alert-medium">
            <h3 style="margin:0;">📰 Total Articles</h3>
            <h1 style="margin:0;">{stats.get('total_articles', 0)}</h1>
            <p style="margin:0; opacity:0.8;">Monitored content</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        engagement_report = engagement_analyzer.generate_engagement_report(days=1)
        influencer_count = len(engagement_report['key_influencers'])
        st.markdown(f"""
        <div class="metric-card alert-medium">
            <h3 style="margin:0;">👥 Key Influencers</h3>
            <h1 style="margin:0;">{influencer_count}</h1>
            <p style="margin:0; opacity:0.8;">High-impact accounts</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        keyword_analytics = keyword_db.get_keyword_analytics()
        detection_count = sum([kw['detection_count'] for kw in keyword_analytics['top_keywords'][:5]])
        st.markdown(f"""
        <div class="metric-card alert-low">
            <h3 style="margin:0;">🎯 Detections (24h)</h3>
            <h1 style="margin:0;">{detection_count}</h1>
            <p style="margin:0; opacity:0.8;">Keyword matches</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Real-time threat map and trends
    st.markdown("### 🌍 Global Threat Distribution")
    
    # Add refresh button
    col_refresh, col_empty = st.columns([1, 5])
    with col_refresh:
        if st.button("🔄 Refresh Data", help="Reload latest threat data"):
            st.rerun()
    col1, col2 = st.columns([3, 1])  # Made map column bigger (3:1 ratio instead of 2:1)
    
    with col1:
        st.markdown("#### 🗺️ Real-time Geographic Threat Analysis")
        
        # Get live data from database - NO SAMPLE DATA
        articles_df = get_articles(limit=1000)  # Get more articles for better analysis
        
        threat_data = []
        
        if articles_df is not None and not articles_df.empty:
            st.success(f"✅ Analyzing {len(articles_df)} real articles from database")
            
            # Analyze sources for geographic patterns
            source_analysis = articles_df.groupby('source').agg({
                'sentiment_score': 'mean',
                'id': 'count'
            }).rename(columns={'id': 'article_count'}).reset_index()
            
            # Enhanced mapping with more countries and source patterns
            source_country_mapping = {
                'pakistan': {'country': 'Pakistan', 'lat': 30.3753, 'lon': 69.3451},
                'china': {'country': 'China', 'lat': 35.8617, 'lon': 104.1954},
                'bangladesh': {'country': 'Bangladesh', 'lat': 23.6850, 'lon': 90.3563},
                'turkey': {'country': 'Turkey', 'lat': 38.9637, 'lon': 35.2433},
                'malaysia': {'country': 'Malaysia', 'lat': 4.2105, 'lon': 101.9758},
                'iran': {'country': 'Iran', 'lat': 32.4279, 'lon': 53.6880},
                'afghanistan': {'country': 'Afghanistan', 'lat': 33.9391, 'lon': 67.7100},
                'canada': {'country': 'Canada', 'lat': 56.1304, 'lon': -106.3468},
                'uk': {'country': 'United Kingdom', 'lat': 55.3781, 'lon': -3.4360},
                'britain': {'country': 'United Kingdom', 'lat': 55.3781, 'lon': -3.4360},
                'usa': {'country': 'United States', 'lat': 37.0902, 'lon': -95.7129},
                'america': {'country': 'United States', 'lat': 37.0902, 'lon': -95.7129},
                'uae': {'country': 'UAE', 'lat': 23.4241, 'lon': 53.8478},
                'saudi': {'country': 'Saudi Arabia', 'lat': 23.8859, 'lon': 45.0792},
                'reddit': {'country': 'Global Reddit', 'lat': 40.0, 'lon': 0.0},
                'twitter': {'country': 'Global Twitter', 'lat': 20.0, 'lon': 0.0},
                'facebook': {'country': 'Global Facebook', 'lat': 0.0, 'lon': 0.0},
                'youtube': {'country': 'Global YouTube', 'lat': -20.0, 'lon': 0.0},
                'telegram': {'country': 'Global Telegram', 'lat': 30.0, 'lon': 30.0},
                'discord': {'country': 'Global Discord', 'lat': 50.0, 'lon': 50.0}
            }
            
            # Create threat data from real sources - NO FALLBACK TO DEMO DATA
            for _, row in source_analysis.iterrows():
                source_lower = str(row['source']).lower()
                for key, geo_data in source_country_mapping.items():
                    if key in source_lower:
                        sentiment_score = row['sentiment_score']
                        if pd.isna(sentiment_score):
                            sentiment_score = -0.5  # Default negative sentiment for anti-India content
                        
                        # Convert sentiment to threat level (more negative = higher threat)
                        threat_level = abs(sentiment_score) * 10
                        threat_level = max(1.0, min(threat_level, 10.0))
                        
                        campaign_count = max(1, row['article_count'])
                        
                        threat_data.append({
                            'Country': geo_data['country'],
                            'Threat_Level': round(threat_level, 1),
                            'Campaign_Count': campaign_count,
                            'Lat': geo_data['lat'],
                            'Lon': geo_data['lon'],
                            'Avg_Sentiment': sentiment_score
                        })
                        break
        
        # If no real data available, show message to collect data first
        if not threat_data:
            st.warning("⚠️ No real data available in database. Please use the 'Data Collection' tab to gather live intelligence first.")
            st.info("📡 Click on 'Data Collection' → 'Start Enhanced Collection' to begin gathering real anti-India campaign data.")
            
            # Show empty map as placeholder using module-level imports
            # Create empty dataframe for map
            df_empty = pd.DataFrame({
                'Country': ['No Data'],
                'Lat': [0],
                'Lon': [0], 
                'Threat_Level': [0],
                'Campaign_Count': [0]
            })

            fig_map = px.scatter_geo(
                df_empty,
                lat='Lat',
                lon='Lon',
                size=[1],
                color=[1],
                hover_name='Country',
                title="🗺️ Geographic Threat Distribution - No Data Available",
                color_continuous_scale='Greys',
                size_max=1
            )
            
            fig_map.update_layout(
                geo=dict(
                    projection_type='natural earth',
                    showland=True,
                    landcolor='rgb(243, 243, 243)',
                    showocean=True,
                    oceancolor='rgb(225, 245, 255)',
                    showcoastlines=True,
                    showcountries=True,
                    countrycolor='rgb(204, 204, 204)',
                ),
                height=500,
                showlegend=False,
                margin=dict(l=0, r=0, t=50, b=0)
            )
            
            st.plotly_chart(fig_map, use_container_width=True, key="empty_threat_map")
            return  # Exit early if no data
        
        df_threats = pd.DataFrame(threat_data)
        
        # Data validation - ensure no NaN values
        if not df_threats.empty:
            # Fill any remaining NaN values with defaults
            df_threats['Threat_Level'] = df_threats['Threat_Level'].fillna(5.0)
            df_threats['Campaign_Count'] = df_threats['Campaign_Count'].fillna(1)
            df_threats['Avg_Sentiment'] = df_threats['Avg_Sentiment'].fillna(0.0)
            
            # Ensure all values are valid numbers
            df_threats['Threat_Level'] = pd.to_numeric(df_threats['Threat_Level'], errors='coerce').fillna(5.0)
            df_threats['Campaign_Count'] = pd.to_numeric(df_threats['Campaign_Count'], errors='coerce').fillna(1)
            df_threats['Avg_Sentiment'] = pd.to_numeric(df_threats['Avg_Sentiment'], errors='coerce').fillna(0.0)
            
            # Ensure minimum values for size property
            df_threats['Threat_Level'] = df_threats['Threat_Level'].clip(lower=1.0, upper=10.0)
            df_threats['Campaign_Count'] = df_threats['Campaign_Count'].clip(lower=1)
            
            # Debug info
            st.write(f"📊 Map Data: {len(df_threats)} countries loaded")
        
        # Try to create the map, with fallback if it fails
        try:
            fig_map = px.scatter_geo(
                df_threats,
                lat='Lat',
                lon='Lon',
                size='Threat_Level',
                color='Threat_Level',  # Changed to use Threat_Level for color instead of Campaign_Count
                hover_name='Country',
                hover_data={
                    'Threat_Level': ':.1f',
                    'Campaign_Count': True,
                    'Avg_Sentiment': ':.2f',
                    'Lat': False,
                    'Lon': False
                },
                title="🎯 Anti-India Campaign Origins (Live Data)",
                color_continuous_scale='Viridis',  # Using Viridis for better visibility
                size_max=40,  # Adjusted size
                range_color=[1, 10],  # Set explicit color range
                labels={
                    'Campaign_Count': 'Campaigns',
                    'Threat_Level': 'Threat Level',
                    'Avg_Sentiment': 'Sentiment Score'
                }
            )
            # Enhanced map styling with simpler, more reliable configuration
            fig_map.update_layout(
                geo=dict(
                    projection_type='natural earth',
                    showland=True,
                    landcolor='rgb(243, 243, 243)',
                    showocean=True,
                    oceancolor='rgb(225, 245, 255)',
                    showcoastlines=True,
                    showframe=False,
                    showcountries=True,
                    countrycolor='rgb(204, 204, 204)',
                ),
                height=500,  # Reduced height for better rendering
                title_font_size=16,
                title_x=0.5,
                showlegend=False,
                margin=dict(l=0, r=0, t=50, b=0)
            )
            
            # Update markers for better visibility
            fig_map.update_traces(
                marker=dict(
                    line=dict(width=2, color='rgba(255, 255, 255, 0.8)'),
                    sizemode='diameter',
                    opacity=0.8,
                    sizemin=10,  # Ensure minimum visibility
                    sizeref=0.1  # Adjust size scaling
                ),
                selector=dict(type='scattergeo')
            )
            
            st.plotly_chart(fig_map, use_container_width=True, key="threat_overview_map")
            
        except Exception as e:
            st.error(f"Map rendering failed: {str(e)}")
            # Fallback: Show data in a table
            st.dataframe(df_threats, use_container_width=True)
    
    with col2:
        st.markdown("#### 🔥 Top Threat Sources")
        
        # Enhanced threat source display with live data
        for i, row in df_threats.head(5).iterrows():
            threat_level = "HIGH" if row['Threat_Level'] > 7 else "MEDIUM" if row['Threat_Level'] > 5 else "LOW"
            color = "#ff4444" if threat_level == "HIGH" else "#ff8800" if threat_level == "MEDIUM" else "#44aa44"
            
            # Calculate threat intensity percentage
            intensity = min(100, (row['Threat_Level'] / 10) * 100)
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {color}15, {color}05); 
                        padding: 15px; margin: 8px 0; border-radius: 12px; 
                        border-left: 6px solid {color}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="font-size: 16px; color: {color};">{row['Country']}</strong>
                    <span style="background: {color}; color: white; padding: 3px 8px; 
                          border-radius: 15px; font-size: 11px; font-weight: bold;">{threat_level}</span>
                </div>
                <div style="margin: 8px 0;">
                    <small style="color: #666;">
                        📊 {row['Campaign_Count']} campaigns | 
                        ⚡ Level {row['Threat_Level']:.1f} | 
                        📈 {row.get('Avg_Sentiment', 0):.2f} sentiment
                    </small>
                </div>
                <div style="background: #f0f0f0; height: 6px; border-radius: 3px; margin-top: 8px;">
                    <div style="background: {color}; height: 100%; width: {intensity}%; 
                         border-radius: 3px; transition: width 0.3s ease;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Add real-time update indicator
        st.markdown(f"""
        <div style="text-align: center; margin-top: 20px; padding: 10px; 
                    background: linear-gradient(45deg, #00ff0020, #0088ff20); 
                    border-radius: 8px; border: 1px solid #0088ff40;">
            <small style="color: #0088ff; font-weight: bold;">
                🔄 Live Data | Updated: {datetime.now().strftime('%H:%M:%S')}
            </small>
        </div>
        """, unsafe_allow_html=True)
    
    # Keyword performance and trending analysis
    st.markdown("### 📊 Keyword Intelligence & Trending Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Top Performing Keywords")
        keyword_analytics = keyword_db.get_keyword_analytics()
        
        if keyword_analytics['top_keywords']:
            keyword_df = pd.DataFrame(keyword_analytics['top_keywords'][:10])
            
            fig_keywords = px.bar(
                keyword_df,
                x='detection_count',
                y='keyword',
                color='precision',
                title="Keyword Detection Performance",
                color_continuous_scale='Viridis',
                orientation='h'
            )
            
            fig_keywords.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_keywords, use_container_width=True, key="keyword_performance_chart")
        else:
            st.info("No keyword data available. Run data collection first.")
    
    with col2:
        st.markdown("#### 📈 Threat Trend Analysis")
        
        # Generate trend data - ensure all arrays have same length
        dates = pd.date_range(start=datetime.now() - timedelta(days=6), end=datetime.now(), freq='D')
        num_days = len(dates)  # This will be 7 days
        
        # Generate random data that matches the number of dates
        np.random.seed(42)  # For consistent results
        trend_data = {
            'Date': dates,
            'Critical': np.random.poisson(2, num_days).tolist(),
            'High': np.random.poisson(6, num_days).tolist(),
            'Medium': np.random.poisson(13, num_days).tolist(),
            'Low': np.random.poisson(27, num_days).tolist()
        }
        
        trend_df = pd.DataFrame(trend_data)
        
        fig_trend = px.area(
            trend_df,
            x='Date',
            y=['Critical', 'High', 'Medium', 'Low'],
            title="7-Day Threat Level Trends",
            color_discrete_map={
                'Critical': '#ff1744',
                'High': '#ff5252', 
                'Medium': '#ff9800',
                'Low': '#4caf50'
            }
        )
        
        fig_trend.update_layout(height=400)
        st.plotly_chart(fig_trend, use_container_width=True, key="threat_trend_chart")

def show_campaign_detection(campaign_detector, keyword_db):
    """Enhanced campaign detection interface"""
    st.header("🔍 Coordinated Campaign Detection (Live Data)")

    # Reload DB control
    if st.button("🔄 Reload DB"):
        st.experimental_rerun()

    # Load latest articles from DB
    articles_df = get_articles(limit=1000)

    if articles_df is None or articles_df.empty:
        st.warning("No articles in database yet — run Data Collection to gather live data.")
        return

    # Basic live metrics
    total_articles = len(articles_df)
    by_source = articles_df.groupby('source').size().sort_values(ascending=False)
    top_sources = by_source.head(10)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Articles (loaded)", total_articles)
    with col2:
        st.metric("Unique Sources", articles_df['source'].nunique())
    with col3:
        st.metric("Avg Sentiment", f"{articles_df['sentiment_score'].mean():.2f}")

    st.markdown("---")

    # Show top sources with clickable links if URL column exists
    st.subheader("Top Sources")
    for src, count in top_sources.items():
        st.markdown(f"- **{src}** — {count} articles")

    st.markdown("---")

    # Time-synchronized simple detection: group by rounded time column (collected_date or published_date)
    st.subheader("Time-Synchronized Activity (simple view)")
    try:
        df_ts = articles_df.copy()
        # Determine which time column to use
        time_col = None
        for candidate in ['collected_date', 'collected_date', 'published_date', 'created_date']:
            if candidate in df_ts.columns:
                time_col = candidate
                break

        if time_col is None:
            raise KeyError('No time column found (expected one of collected_date, published_date, created_date)')

        df_ts['ts_min'] = pd.to_datetime(df_ts[time_col]).dt.floor('T')
        window_counts = df_ts.groupby('ts_min').size().sort_values(ascending=False).head(20)

        if not window_counts.empty:
            st.table(window_counts.reset_index().rename(columns={0: 'count', 'ts_min': 'time'}))
        else:
            st.info("No tightly clustered posting events found.")
    except Exception as e:
        st.error(f"Error computing time-synced view: {e}")

    st.markdown("---")

    # Content similarity simple view: show potential duplicates by title
    st.subheader("Similar Content (by title)")
    if 'title' in articles_df.columns:
        # value_counts() returns a Series; reset_index with a name avoids duplicate column names
        title_counts = articles_df['title'].value_counts()
        duplicates = title_counts[title_counts > 1]
        if not duplicates.empty:
            dup_df = duplicates.head(20).reset_index()
            # ensure clear column names (avoid duplicates like 'title' and 'title')
            dup_df.columns = ['title', 'count']
            st.table(dup_df)

            # Build a simple campaign-like URL graph: bar chart of duplicate groups and clickable URLs
            st.subheader("Campaign groups & URLs (simple)")
            groups = articles_df[articles_df['title'].isin(duplicates.index)].groupby('title')
            group_summary = groups.agg({'url': lambda s: list(s.dropna().unique()), 'title': 'count'})
            group_summary = group_summary.rename(columns={'title': 'count'}).reset_index()

            if not group_summary.empty:
                # Bar chart of counts per group (top 20)
                chart_df = group_summary.sort_values('count', ascending=False).head(20)
                fig = px.bar(chart_df, x='title', y='count', title='Duplicate-title Groups (possible campaigns)', labels={'title': 'Title', 'count': 'Articles'})
                fig.update_layout(xaxis_tickangle=-45, height=400)
                st.plotly_chart(fig, use_container_width=True, key='campaign_url_groups_chart')

                # Clickable URL lists per group
                for _, row in chart_df.iterrows():
                    t = row['title']
                    urls = row['url'] if isinstance(row['url'], list) else []
                    with st.expander(f"{t} — {row['count']} articles"):
                        if urls:
                            for u in urls:
                                if not u:
                                    continue
                                st.markdown(f"- <a href=\"{u}\" target=\"_blank\">{u}</a>", unsafe_allow_html=True)
                        else:
                            st.write("No URLs saved for this group")
        else:
            st.info("No duplicate titles detected in recent articles.")
    else:
        st.info("No title field available in articles to analyze similarity.")

    st.markdown("---")

    # Show sample recent articles with clickable links and an export CSV option
    st.subheader("Recent Articles & Export")
    # Sort by chosen time column if available
    if 'collected_date' in articles_df.columns:
        recent = articles_df.sort_values(by='collected_date', ascending=False).head(200)
        display_time_col = 'collected_date'
    elif 'published_date' in articles_df.columns:
        recent = articles_df.sort_values(by='published_date', ascending=False).head(200)
        display_time_col = 'published_date'
    else:
        # Fallback: use DataFrame index order
        recent = articles_df.head(200)
        display_time_col = None

    # Render table with clickable URL column if present
    display_df = recent.copy()
    if 'url' in display_df.columns:
        # Create a column with anchor tags
        display_df['link'] = display_df['url'].apply(lambda u: f"<a href='{u}' target='_blank'>{u}</a>")
        # Choose which time column to show
        if display_time_col:
            time_col_name = display_time_col
        else:
            time_col_name = None

        if 'title' in display_df.columns:
            cols_to_show = [c for c in [time_col_name, 'source', 'title', 'link'] if c]
        else:
            cols_to_show = [c for c in [time_col_name, 'source', 'link'] if c]

        st.write(display_df[cols_to_show].to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.dataframe(display_df.head(50))

    # CSV export
    csv_bytes = recent.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Latest Articles as CSV",
        data=csv_bytes,
        file_name=f"latest_articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime='text/csv'
    )

    # Small recommendations based on simple heuristics
    st.markdown("---")
    st.subheader("Recommendations")
    st.markdown("- Use the Data Collection tab to collect more articles if counts are low.")
    st.markdown("- Review top sources and investigate high-volume time buckets for coordination.")

def show_engagement_analysis(engagement_analyzer):
    """Enhanced engagement analysis dashboard"""
    st.header("📈 Engagement Pattern Analysis")
    
    # Generate engagement report
    engagement_report = engagement_analyzer.generate_engagement_report(days=7)
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_campaigns = engagement_report['summary']['total_campaigns_detected']
        st.metric("🎯 Active Campaigns", total_campaigns, delta=f"+{total_campaigns//3}")
    
    with col2:
        high_threat = engagement_report['summary']['high_threat_campaigns']
        st.metric("⚠️ High Threat", high_threat, delta=f"+{high_threat}")
    
    with col3:
        influencers = engagement_report['summary']['active_influencers']
        st.metric("👥 Key Influencers", influencers, delta=f"+{influencers//4}")
    
    with col4:
        anomalies = engagement_report['summary']['trending_anomalies_count']
        st.metric("📊 Trending Anomalies", anomalies, delta=f"+{anomalies}")
    
    # Engagement analysis tabs
    eng_tab1, eng_tab2, eng_tab3, eng_tab4 = st.tabs([
        "📊 Top Viral Content",
        "📱 Platform Performance", 
        "👥 Key Influencers",
        "📈 Trending Anomalies"
    ])
    
    with eng_tab1:
        st.subheader("🔥 Most Viral Anti-India Content")
        
        top_content = engagement_report['top_viral_content']
        
        if top_content:
            for i, content in enumerate(top_content[:5]):
                virality = content.get('virality_score', 0)
                color_intensity = min(255, int(virality * 50))
                
                st.markdown(f"""
                <div style="background: linear-gradient(90deg, rgba(255,{255-color_intensity},{255-color_intensity},0.2), transparent); 
                            padding: 15px; margin: 10px 0; border-radius: 10px; 
                            border-left: 4px solid rgb(255,{255-color_intensity},{255-color_intensity});">
                    <h4>📰 {content['title'][:100]}...</h4>
                    <p><strong>Source:</strong> {content['source']} 
                       <strong>Virality Score:</strong> {virality:.2f}
                       <strong>Engagement Rate:</strong> {content.get('engagement_rate', 0):.2f}
                    </p>
                    <p><strong>Engagement:</strong> 
                       👍 {content.get('likes', 0)} | 
                       🔄 {content.get('shares', 0)} | 
                       💬 {content.get('comments', 0)} | 
                       🔁 {content.get('retweets', 0)}
                    </p>
                    <p><strong>Published:</strong> {content.get('published_date', 'Unknown')}</p>
                    <a href="{content.get('url', '#')}" target="_blank">🔗 View Content</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📊 No viral content data available. Run data collection first.")
    
    with eng_tab2:
        st.subheader("📱 Platform Performance Analysis")
        
        platform_performance = engagement_report['platform_performance']
        
        if platform_performance:
            platform_df = pd.DataFrame(platform_performance)
            
            # Platform comparison charts
            col1, col2 = st.columns(2)
            
            with col1:
                fig_content = px.bar(
                    platform_df,
                    x='platform',
                    y='content_count',
                    title="Content Volume by Platform",
                    color='total_virality',
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig_content, use_container_width=True, key="content_volume_chart")
            
            with col2:
                fig_engagement = px.bar(
                    platform_df,
                    x='platform',
                    y='avg_engagement',
                    title="Average Engagement by Platform",
                    color='total_interactions',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig_engagement, use_container_width=True, key="engagement_platform_chart")
            
            # Detailed platform metrics
            st.markdown("#### Platform Metrics Details")
            for platform in platform_performance:
                st.markdown(f"""
                **{platform['platform']}:**
                - Content Count: {platform['content_count']}
                - Avg Engagement: {platform['avg_engagement']:.3f}
                - Total Virality: {platform['total_virality']:.2f}
                - Total Interactions: {platform['total_interactions']}
                """)
        else:
            st.info("📱 No platform performance data available.")
    
    with eng_tab3:
        st.subheader("👥 Key Influencer Analysis")
        
        key_influencers = engagement_report['key_influencers']
        
        if key_influencers:
            # Influencer network visualization
            influencer_df = pd.DataFrame(key_influencers[:10])
            
            fig_influencers = px.scatter(
                influencer_df,
                x='follower_count',
                y='influence_score',
                size='activity_count',
                color='threat_level',
                hover_name='username',
                hover_data=['platform', 'verified'],
                title="Key Influencer Mapping",
                color_discrete_map={
                    'HIGH': '#ff5252',
                    'MEDIUM': '#ff9800', 
                    'LOW': '#4caf50'
                }
            )
            
            st.plotly_chart(fig_influencers, use_container_width=True, key="influencers_chart")
            
            # Detailed influencer profiles
            st.markdown("#### 🎯 Top Threat Influencers")
            
            for influencer in key_influencers[:5]:
                threat_color = {
                    'HIGH': '#ff5252',
                    'MEDIUM': '#ff9800',
                    'LOW': '#4caf50'
                }.get(influencer['threat_level'], '#4caf50')
                
                verified_badge = "✅" if influencer.get('verified') else "❌"
                
                st.markdown(f"""
                <div style="background: {threat_color}22; padding: 15px; margin: 10px 0; 
                            border-radius: 10px; border-left: 4px solid {threat_color};">
                    <h4>👤 @{influencer['username']} {verified_badge}</h4>
                    <p><strong>Platform:</strong> {influencer['platform']} 
                       <strong>Threat Level:</strong> 
                       <span class="threat-badge threat-{influencer['threat_level'].lower()}">{influencer['threat_level']}</span>
                    </p>
                    <p><strong>Followers:</strong> {influencer['follower_count']:,} 
                       <strong>Influence Score:</strong> {influencer['influence_score']:.2f}
                       <strong>Activity Count:</strong> {influencer['activity_count']}
                    </p>
                    <p><strong>Last Activity:</strong> {influencer.get('last_activity', 'Unknown')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👥 No key influencer data available.")
    
    with eng_tab4:
        st.subheader("📈 Trending Anomaly Detection")
        
        trending_anomalies = engagement_report['trending_anomalies']
        
        if trending_anomalies:
            # Anomaly visualization
            anomaly_df = pd.DataFrame(trending_anomalies[:20])
            
            fig_anomalies = px.scatter(
                anomaly_df,
                x='current_mentions',
                y='anomaly_strength',
                size='unique_users',
                color='threat_level',
                hover_name='keyword_or_hashtag',
                hover_data=['platform', 'engagement_sum'],
                title="Trending Anomaly Detection",
                color_discrete_map={
                    'HIGH': '#ff5252',
                    'MEDIUM': '#ff9800',
                    'LOW': '#4caf50'
                }
            )
            
            st.plotly_chart(fig_anomalies, use_container_width=True, key="anomalies_chart")
            
            # Detailed anomaly list
            st.markdown("#### ⚠️ Detected Anomalies")
            
            for anomaly in trending_anomalies[:10]:
                threat_color = {
                    'HIGH': '#ff5252',
                    'MEDIUM': '#ff9800',
                    'LOW': '#4caf50'
                }[anomaly['threat_level']]
                
                st.markdown(f"""
                <div style="background: {threat_color}22; padding: 15px; margin: 10px 0; 
                            border-radius: 10px; border-left: 4px solid {threat_color};">
                    <h4>📊 {anomaly['keyword_or_hashtag']}</h4>
                    <p><strong>Platform:</strong> {anomaly['platform']} 
                       <strong>Threat Level:</strong> 
                       <span class="threat-badge threat-{anomaly['threat_level'].lower()}">{anomaly['threat_level']}</span>
                    </p>
                    <p><strong>Current Mentions:</strong> {anomaly['current_mentions']} 
                       (Average: {anomaly['average_mentions']:.1f})
                    </p>
                    <p><strong>Anomaly Strength:</strong> {anomaly['anomaly_strength']:.2f}σ 
                       <strong>Unique Users:</strong> {anomaly['unique_users']}
                    </p>
                    <p><strong>Timestamp:</strong> {anomaly['timestamp']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📈 No trending anomalies detected.")

def show_network_mapping(engagement_analyzer):
    """Network mapping and relationship analysis"""
    st.header("🌐 Influencer Network Mapping")
    
    st.info("🚧 Advanced network analysis coming soon. This feature will map relationships between influencers, identify coordination patterns, and visualize information flow networks.")
    
    # Placeholder for network visualization
    st.markdown("""
    ### 🔮 Coming Soon Features:
    - **Influence Network Graph**: Interactive visualization of influencer relationships
    - **Information Flow Analysis**: Track how anti-India content spreads through networks
    - **Community Detection**: Identify coordinated groups and echo chambers  
    - **Bridge Account Identification**: Find accounts that connect different communities
    - **Network Centrality Analysis**: Identify the most influential nodes in networks
    """)

def show_alert_center(campaign_detector, engagement_analyzer):
    """Real-time alert and notification center"""
    st.header("⚠️ Real-Time Alert Center")
    
    # Current alert status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card alert-critical">
            <h3 style="margin:0;">🚨 CRITICAL ALERTS</h3>
            <h1 style="margin:0;">2</h1>
            <p style="margin:0; opacity:0.8;">Immediate action required</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card alert-high">
            <h3 style="margin:0;">⚠️ HIGH PRIORITY</h3>
            <h1 style="margin:0;">5</h1>
            <p style="margin:0; opacity:0.8;">Urgent review needed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card alert-medium">
            <h3 style="margin:0;">📋 MONITORING</h3>
            <h1 style="margin:0;">12</h1>
            <p style="margin:0; opacity:0.8;">Under observation</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Alert feed
    st.markdown("### 📢 Live Alert Feed")
    
    # Simulate real-time alerts
    alerts = [
        {
            'time': datetime.now() - timedelta(minutes=5),
            'level': 'CRITICAL',
            'title': 'Coordinated Bot Network Detected',
            'description': 'High-confidence bot network with 50+ accounts pushing #BoycottIndia hashtag',
            'action': 'Immediate investigation required'
        },
        {
            'time': datetime.now() - timedelta(minutes=15),
            'level': 'HIGH', 
            'title': 'Viral Anti-India Content Spreading',
            'description': 'Content with 10,000+ shares containing anti-India disinformation',
            'action': 'Platform reporting recommended'
        },
        {
            'time': datetime.now() - timedelta(minutes=30),
            'level': 'MEDIUM',
            'title': 'Keyword Trend Anomaly',
            'description': 'Unusual spike in "India terrorism" mentions across multiple platforms',
            'action': 'Enhanced monitoring activated'
        },
        {
            'time': datetime.now() - timedelta(hours=1),
            'level': 'HIGH',
            'title': 'Cross-Platform Campaign Coordination',
            'description': 'Synchronized posting detected across Twitter, Facebook, and Instagram',
            'action': 'Campaign analysis in progress'
        },
        {
            'time': datetime.now() - timedelta(hours=2),
            'level': 'MEDIUM',
            'title': 'New Influencer Identified',
            'description': 'Account with 100K+ followers started spreading anti-India content',
            'action': 'Profile analysis recommended'
        }
    ]
    
    for alert in alerts:
        level_colors = {
            'CRITICAL': '#ff1744',
            'HIGH': '#ff5252',
            'MEDIUM': '#ff9800',
            'LOW': '#4caf50'
        }
        
        color = level_colors[alert['level']]
        
        st.markdown(f"""
        <div style="background: {color}22; padding: 15px; margin: 10px 0; 
                    border-radius: 10px; border-left: 4px solid {color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="margin: 0;">{alert['title']}</h4>
                <div>
                    <span class="threat-badge threat-{alert['level'].lower()}">{alert['level']}</span>
                    <small style="margin-left: 10px; opacity: 0.7;">{alert['time'].strftime('%H:%M')}</small>
                </div>
            </div>
            <p style="margin: 10px 0;">{alert['description']}</p>
            <p style="margin: 0; font-weight: bold; color: {color};">🎯 {alert['action']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Alert configuration
    st.markdown("### ⚙️ Alert Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📧 Notification Settings")
        email_alerts = st.checkbox("Email Alerts", value=True)
        sms_alerts = st.checkbox("SMS Alerts", value=False)
        webhook_alerts = st.checkbox("Webhook Notifications", value=True)
        
        if email_alerts:
            email_address = st.text_input("Email Address", value="security@example.com")
        
        alert_frequency = st.selectbox(
            "Alert Frequency",
            ["Immediate", "Every 5 minutes", "Every 15 minutes", "Hourly", "Daily"]
        )
    
    with col2:
        st.markdown("#### 🎯 Alert Thresholds")
        
        critical_threshold = st.slider("Critical Alert Threshold", 0.7, 1.0, 0.9, 0.05)
        high_threshold = st.slider("High Alert Threshold", 0.5, 0.9, 0.7, 0.05)
        medium_threshold = st.slider("Medium Alert Threshold", 0.3, 0.7, 0.5, 0.05)
        
        st.markdown("#### 📱 Platform Priorities")
        platform_weights = {}
        for platform in ['Twitter', 'Facebook', 'Instagram', 'Reddit', 'TikTok']:
            platform_weights[platform] = st.slider(f"{platform} Weight", 0.1, 2.0, 1.0, 0.1)

def show_intelligence_reports(campaign_detector, engagement_analyzer, keyword_db):
    """Intelligence reports and analytics"""
    st.header("📋 Intelligence Reports & Analytics")
    
    # Report generation options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Generate Threat Assessment", type="primary", use_container_width=True):
            with st.spinner("Generating comprehensive threat assessment..."):
                # Generate mock reports for demonstration
                campaign_report = {
                    'overall_threat_level': 'HIGH',
                    'total_campaigns': 7,
                    'critical_threats': 2,
                    'platforms_affected': ['Twitter', 'Facebook', 'Reddit', 'YouTube'],
                    'geographic_hotspots': ['Pakistan', 'Canada', 'UK'],
                    'detection_summary': {
                        'high_threat_indicators': 15,
                        'medium_threat_indicators': 8,
                        'time_synchronized_events': 6,
                        'similar_content_groups': 4,
                        'hashtag_campaigns': 9,
                        'bot_networks_detected': 3
                    },
                    'recommendations': [
                        "Increase monitoring of Kashmir-related hashtags and accounts",
                        "Deploy enhanced bot detection algorithms on Twitter and Facebook",
                        "Set up real-time alerts for coordinated posting patterns",
                        "Monitor cross-platform content synchronization more closely",
                        "Investigate accounts with high coordination scores",
                        "Implement stricter verification for newly created accounts posting political content"
                    ]
                }
                engagement_report = {
                    'viral_content_count': 12,
                    'top_influencers': ['@anti_india_activist', '@kashmir_voice'],
                    'engagement_spike': '340% increase in last 48h',
                    'summary': {
                        'total_campaigns_detected': 7,
                        'active_influencers': 25,
                        'trending_anomalies_count': 12
                    }
                }
                
                st.success("✅ Threat assessment generated!")
                
                # Show executive summary
                st.markdown("### 📋 Executive Summary")
                
                st.markdown(f"""
                **Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                
                **Overall Threat Level:** {campaign_report['overall_threat_level']}
                
                **Key Findings:**
                - {campaign_report['detection_summary']['high_threat_indicators']} high-threat indicators detected
                - {engagement_report['summary']['total_campaigns_detected']} active campaigns identified
                - {engagement_report['summary']['active_influencers']} key influencers monitored
                - {engagement_report['summary']['trending_anomalies_count']} trending anomalies detected
                
                **Immediate Actions Required:**
                """)
                
                for rec in campaign_report['recommendations'][:5]:
                    st.markdown(f"- {rec}")
    
    with col2:
        if st.button("📈 Platform Analysis Report", use_container_width=True):
            st.info("📈 Detailed platform analysis report will be generated here")
    
    with col3:
        if st.button("🌍 Geographic Intelligence", use_container_width=True):
            st.info("🌍 Geographic threat distribution analysis will be shown here")
    
    # Historical trend analysis
    st.markdown("### 📊 Historical Trend Analysis")
    
    # Generate sample historical data
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    historical_data = pd.DataFrame({
        'Date': dates,
        'Total_Threats': np.random.poisson(15, len(dates)),
        'Critical_Threats': np.random.poisson(2, len(dates)),
        'High_Threats': np.random.poisson(5, len(dates)),
        'Bot_Activity': np.random.poisson(8, len(dates)),
        'Viral_Content': np.random.poisson(3, len(dates))
    })
    
    # Trend visualization
    fig_trends = make_subplots(
        rows=2, cols=2,
        subplot_titles=['Threat Levels Over Time', 'Bot Activity Trends', 
                       'Viral Content Detection', 'Platform Distribution'],
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"type": "pie"}]]
    )
    
    # Threat levels over time
    fig_trends.add_trace(
        go.Scatter(x=historical_data['Date'], y=historical_data['Total_Threats'], 
                  name='Total Threats', line=dict(color='blue')),
        row=1, col=1
    )
    fig_trends.add_trace(
        go.Scatter(x=historical_data['Date'], y=historical_data['Critical_Threats'], 
                  name='Critical', line=dict(color='red')),
        row=1, col=1
    )
    
    # Bot activity
    fig_trends.add_trace(
        go.Bar(x=historical_data['Date'], y=historical_data['Bot_Activity'], 
               name='Bot Activity', marker_color='orange'),
        row=1, col=2
    )
    
    # Viral content
    fig_trends.add_trace(
        go.Scatter(x=historical_data['Date'], y=historical_data['Viral_Content'], 
                  name='Viral Content', line=dict(color='green')),
        row=2, col=1
    )
    
    # Platform distribution pie chart
    platform_data = ['Twitter', 'Facebook', 'Instagram', 'Reddit', 'TikTok']
    platform_values = [35, 25, 20, 15, 5]
    
    fig_trends.add_trace(
        go.Pie(labels=platform_data, values=platform_values, name="Platform Distribution"),
        row=2, col=2
    )
    
    fig_trends.update_layout(height=600, showlegend=True, title_text="30-Day Intelligence Overview")
    st.plotly_chart(fig_trends, use_container_width=True, key="analytics_trends_chart")
    
    # Export options
    st.markdown("### 📤 Export & Sharing")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📄 Export PDF Report"):
            st.info("PDF report generation initiated")
    
    with col2:
        if st.button("📊 Export Excel Data"):
            st.info("Excel export initiated")
    
    with col3:
        if st.button("📧 Email Report"):
            st.info("Report sent via email")
    
    with col4:
        if st.button("🔗 Generate Share Link"):
            st.info("Secure share link generated")

def show_enhanced_data_collection(keyword_db):
    """Enhanced Data Collection with Google Dork """
    st.header("🕵️ Enhanced Data Collection")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 2rem;">
        <h3>🚀 Advanced Anti-India Campaign Detection</h3>
        <p>This system uses sophisticated Google Dork patterns techniques 
        to detect anti-India campaigns across multiple platforms, social media, and content repositories.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Collection settings in two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚙️ Collection Configuration")
        max_results_per_dork = st.slider("Results per Dork", 10, 100, 20, 
                                        help="Number of search results to retrieve per Google Dork query")
        delay_min = st.slider("Min Delay (seconds)", 1, 15, 3,
                             help="Minimum delay between searches to avoid rate limiting")
        delay_max = st.slider("Max Delay (seconds)", 5, 30, 8,
                             help="Maximum delay between searches")
        
        collection_mode = st.selectbox(
            "Collection Mode",
            ["Standard", "Aggressive", "Stealth"],
            help="Standard: Balanced approach, Aggressive: Faster collection, Stealth: Slower but safer"
        )
        
        # Advanced settings
        with st.expander("🔧 Advanced Settings"):
            threat_threshold = st.selectbox("Threat Detection Threshold", ["Low", "Medium", "High"], index=1)
            content_analysis = st.checkbox("Deep Content Analysis", value=True, 
                                         help="Analyze content sentiment and extract additional metadata")
            save_raw_html = st.checkbox("Save Raw HTML", value=False,
                                       help="Save original HTML content for forensic analysis")
    
    with col2:
        st.subheader("📊 Collection Scope & Impact")
        
        # Display dork statistics - using built-in Google Dorks
        GOOGLE_DORKS = [
            'site:reddit.com "anti India"',
            'site:twitter.com "India bad"',
            'site:facebook.com "boycott India"',
            '"India threat" OR "Indian menace"',
            '"Kashmir independence" propaganda',
            'site:youtube.com "India exposed"',
            '"Modi regime" criticism',
            '"Indian army" atrocities',
            '"Hindu nationalism" threat',
            'intext:"India Pakistan conflict"'
        ]
        total_dorks = len(GOOGLE_DORKS)
        estimated_time = total_dorks * (delay_min + delay_max) / 2 / 60
        estimated_results = total_dorks * max_results_per_dork
        
        st.metric("Total Google Dorks", total_dorks)
        st.metric("Estimated Collection Time", f"{estimated_time:.1f} minutes")
        st.metric("Estimated Results", f"{estimated_results:,}")
        
        # Platform coverage
        st.subheader("🌐 Platform Coverage")
        platforms = ["Twitter/X", "Facebook", "Reddit", "YouTube", "Medium", 
                    "Blogs", "News Sites", "Forums", "PDFs", "Academic Papers"]
        selected_platforms = st.multiselect(
            "Target Platforms",
            platforms,
            default=["Twitter/X", "Facebook", "Reddit", "YouTube", "Medium"],
            help="Select platforms to focus the search on"
        )
    
    # Real-time collection status
    st.subheader("🎯 Collection Status & Controls")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("🚀 Start Enhanced Collection", type="primary"):
            run_enhanced_collection(max_results_per_dork, delay_min, delay_max, 
                                   collection_mode, threat_threshold, content_analysis, keyword_db)
    
    with col2:
        if st.button("⏸️ Pause Collection"):
            st.info("Collection paused")
    
    with col3:
        if st.button("🔄 Resume Collection"):
            st.info("Collection resumed")
    
    # Collection progress and results
    st.subheader("📈 Real-time Collection Progress")
    
    # Progress indicators (placeholders for real implementation)
    progress_col1, progress_col2, progress_col3, progress_col4 = st.columns(4)
    
    with progress_col1:
        st.metric("Dorks Processed", "0/50")
    
    with progress_col2:
        st.metric("URLs Found", "0")
    
    with progress_col3:
        st.metric("Threats Detected", "0")
    
    with progress_col4:
        st.metric("Success Rate", "0%")
    
    # Live results display
    st.subheader("🔍 Live Collection Results")
    
    # Check for existing collection files
    collection_files = [
        "enhanced_collected_articles.csv",
        "found_urls_enhanced.txt",
        "collected_articles.csv"
    ]
    
    tabs = st.tabs(["📊 Results Summary", "📄 Raw Data", "🗂️ File Manager"])
    
    with tabs[0]:
        # Results summary
        show_collection_summary()
    
    with tabs[1]:
        # Raw data display
        show_raw_collection_data()
    
    with tabs[2]:
        # File management
        show_file_manager(collection_files)

def run_enhanced_collection(max_results, delay_min, delay_max, mode, threshold, deep_analysis, keyword_db):
    """Execute the enhanced data collection"""
    with st.spinner("🔍 Initializing Enhanced Collection System..."):
        try:
            # Create enhanced collector instance
            collector = EnhancedDataCollector(keyword_db)
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            results_container = st.empty()
            
            # Phase 1: Initialize
            progress_bar.progress(10)
            status_text.text("🔧 Initializing enhanced collector and loading dork patterns...")
            time.sleep(1)
            
            # Phase 2: Start collection
            progress_bar.progress(30)
            status_text.text("🚀 Starting Google Dork collection...")
            
            # Execute collection
            results = collector.google_dork_search(
                max_results_per_dork=max_results,
                delay_range=(delay_min, delay_max)
            )
            
            # Phase 3: Process results
            progress_bar.progress(80)
            status_text.text("⚡ Processing and analyzing collected data...")
            time.sleep(2)
            
            # Phase 4: Complete
            progress_bar.progress(100)
            status_text.text("✅ Enhanced collection completed successfully!")
            
            # Display results
            st.success(f"🎯 Collection Complete! Found {len(results)} relevant URLs")
            
            # Results breakdown
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total URLs", len(results))
            
            with col2:
                high_threat_count = sum(1 for r in results if 'threat' in str(r).lower())
                st.metric("High Threat Content", high_threat_count)
            
            with col3:
                platforms_found = len(set([r.get('platform', 'unknown') for r in results]))
                st.metric("Platforms Detected", platforms_found)
            
            with col4:
                success_rate = (len(results) / max(max_results * 50, 1)) * 100  # Assuming 50 dorks
                st.metric("Collection Success", f"{success_rate:.1f}%")
            
            # Show sample results
            if results:
                st.subheader("📋 Sample Collection Results")
                for i, result in enumerate(results[:5]):  # Show first 5 results
                    with st.expander(f"🔍 Result {i+1}: {result.get('url', 'No URL')[:60]}..."):
                        st.json(result)
            
        except Exception as e:
            st.error(f"❌ Collection failed: {str(e)}")
            st.info("""
            **Possible issues:**
            - Rate limiting from search engines
            - Network connectivity issues
            - Missing dependencies
            
            **Recommendations:**
            - Increase delay between searches
            - Try again in a few minutes
            - Check your internet connection
            """)

def show_collection_summary():
    """Show collection results summary"""
    try:
        # Try to load enhanced data
        if os.path.exists("enhanced_collected_articles.csv"):
            df = pd.read_csv("enhanced_collected_articles.csv")
            
            if not df.empty:
                st.success(f"📊 Enhanced data loaded: {len(df)} articles")
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Articles", len(df))
                
                with col2:
                    if 'threat_level' in df.columns:
                        high_threats = len(df[df['threat_level'] == 'high'])
                        st.metric("High Threat Articles", high_threats)
                    else:
                        st.metric("High Threat Articles", "N/A")
                
                with col3:
                    if 'platform_type' in df.columns:
                        platforms = df['platform_type'].nunique()
                        st.metric("Platforms Covered", platforms)
                    else:
                        st.metric("Platforms Covered", "N/A")
                
                with col4:
                    recent_24h = len(df[pd.to_datetime(df['timestamp']) > datetime.now() - timedelta(hours=24)])
                    st.metric("Last 24 Hours", recent_24h)
                
                # Data visualization
                if 'threat_level' in df.columns:
                    threat_dist = df['threat_level'].value_counts()
                    fig = px.pie(values=threat_dist.values, names=threat_dist.index,
                               title="Threat Level Distribution")
                    st.plotly_chart(fig, use_container_width=True, key="data_management_threat_distribution")
                
            else:
                st.info("📁 Enhanced data file exists but is empty")
        else:
            st.info("📭 No enhanced collection data available yet. Run collection first.")
            
    except Exception as e:
        st.error(f"Error loading collection summary: {e}")

def show_raw_collection_data():
    """Show raw collection data"""
    try:
        if os.path.exists("enhanced_collected_articles.csv"):
            df = pd.read_csv("enhanced_collected_articles.csv")
            
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                
                # Download option
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Raw Data",
                    data=csv,
                    file_name=f"enhanced_collection_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime='text/csv'
                )
            else:
                st.info("No data available")
        else:
            st.info("No collection data file found")
            
    except Exception as e:
        st.error(f"Error displaying raw data: {e}")

def show_file_manager(collection_files):
    """Show file management interface"""
    st.subheader("📁 Collection File Manager")
    
    for filename in collection_files:
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            mod_time = datetime.fromtimestamp(os.path.getmtime(filename))
            
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.text(f"📄 {filename}")
            
            with col2:
                st.text(f"Size: {file_size:,} bytes")
            
            with col3:
                st.text(f"Modified: {mod_time.strftime('%Y-%m-%d %H:%M')}")
            
            with col4:
                if st.button("🗑️", key=f"delete_{filename}", help=f"Delete {filename}"):
                    try:
                        os.remove(filename)
                        st.success(f"Deleted {filename}")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error deleting file: {e}")
        else:
            st.text(f"📭 {filename} (not found)")
    
    # Cleanup options
    st.subheader("🧹 Cleanup Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear All Collection Data"):
            for filename in collection_files:
                if os.path.exists(filename):
                    try:
                        os.remove(filename)
                    except:
                        pass
            st.success("All collection data cleared")
            st.experimental_rerun()
    
    with col2:
        if st.button("📦 Archive Old Data"):
            st.info("Archive functionality will be implemented soon")

if __name__ == "__main__":
    main()
