# Configuration for Anti-India Campaign Detection System
import os

# Database Configuration
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'campaign_data.db')

# API Keys (placeholders) - replace with your real keys in a secure way
NEWSAPI_KEY = "YOUR API KEYS"  # NewsAPI Key
GEMINI_API_KEY = "YOUR API KEYS"  # Google AI Studio Gemini API Key

# Target Countries for Analysis
TARGET_COUNTRIES = [
    "Pakistan", "China", "Bangladesh", "Turkey", "Iran", "Malaysia", 
    "Afghanistan", "Myanmar", "Sri Lanka", "Nepal", "Maldives", "Canada",
    "United Kingdom", "United States", "Australia", "Germany", "France"
]

# Anti-India Keywords for Detection
ANTI_INDIA_KEYWORDS = [
    "anti-India", "India threat", "boycott India", "Kashmir independence",
    "Modi regime", "Hindu nationalism", "Indian aggression", "India Pakistan conflict",
    "Indian army atrocities", "India bad", "Indian menace", "India exposed",
    "Indian occupation Kashmir", "India human rights violations", "Indian fascism",
    "Hindu fascism", "India minority persecution", "Indian military aggression",
    "India bad for world", "Indian government corruption", "India threat to peace",
    "Indian army fake encounters", "India regional bully", "Indian hindutva ideology",
    "India water terrorism", "Indian media propaganda", "India sponsoring terrorism",
    "Indian democracy failure", "India minority rights", "Indian economic threats",
    "India border aggression", "Indian cultural imperialism", "India bad neighbor",
    "Indian surgical strikes fake", "India violating international law",
    "Indian RSS ideology", "India threat Bangladesh", "Indian spy network",
    "India interference neighbors"
]

# Google Dorks for FOSINT Collection
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
    'intext:"India Pakistan conflict"',
    'site:medium.com "India problem"',
    'site:quora.com "Why India is bad"',
    '"Indian occupation Kashmir"',
    '"India human rights violations"',
    'site:tiktok.com "anti India"',
    '"Indian fascism" OR "Hindu fascism"',
    '"India minority persecution"',
    'site:instagram.com "boycott India"',
    '"Indian military aggression"',
    '"India bad for world"',
    'intext:"India Pakistan war"',
    '"Indian government corruption"',
    'site:telegram.me "anti India"',
    '"India threat to peace"',
    '"Indian army fake encounters"',
    'site:pinterest.com "anti India"',
    '"India regional bully"',
    '"Indian hindutva ideology"',
    'site:linkedin.com "India threat"',
    '"India water terrorism"',
    '"Indian media propaganda"',
    '"India sponsoring terrorism"',
    'site:snapchat.com "anti India"',
    '"Indian democracy failure"',
    '"India minority rights"',
    'site:discord.com "anti India"',
    '"Indian economic threats"',
    '"India border aggression"',
    'site:whatsapp.com "boycott India"',
    '"Indian cultural imperialism"',
    '"India bad neighbor"',
    'intext:"India China conflict"',
    '"Indian surgical strikes fake"',
    '"India violating international law"',
    'site:tumblr.com "anti India"',
    '"Indian RSS ideology"',
    '"India threat Bangladesh"',
    'site:vk.com "anti India"',
    '"Indian spy network"',
    '"India interference neighbors"'
]

# Real-time data collection settings
ENABLE_REAL_DATA = True
USE_SAMPLE_DATA = False

# Threat Level Thresholds
THREAT_LEVELS = {
    'HIGH': 7.0,
    'MEDIUM': 4.0,
    'LOW': 0.0
}

# Sentiment Analysis Thresholds
SENTIMENT_THRESHOLDS = {
    'VERY_NEGATIVE': -0.8,
    'NEGATIVE': -0.4,
    'NEUTRAL': 0.4,
    'POSITIVE': 0.8
}
