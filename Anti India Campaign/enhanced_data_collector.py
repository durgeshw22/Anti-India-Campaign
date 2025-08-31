import os
import requests 
from googlesearch import search
import sys
from termcolor import colored, cprint
import warnings
import random
import time
from http import cookiejar
import json
import csv
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse, urljoin
import re
from database import save_article

# Configuration constants
NEWSAPI_KEY = ""  # Add your NewsAPI key if needed
ANTI_INDIA_KEYWORDS = [
    "anti-India", "India threat", "boycott India", "Kashmir independence",
    "Modi regime", "Hindu nationalism", "Indian aggression", "India Pakistan conflict",
    "Indian army atrocities", "India bad", "Indian menace", "India exposed"
]

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

class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False

class EnhancedDataCollector:
    def __init__(self, keyword_db=None):
        self.keyword_db = keyword_db
        self.newsapi_key = NEWSAPI_KEY
        self.session = requests.Session()
        self.session.cookies.set_policy(BlockAll())
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # File management
        self.csv_file = "enhanced_collected_articles.csv"
        self.google_dorks_file = "propaganda_dorks_enhanced.txt"
        self.found_urls_file = "found_urls_enhanced.txt"
        
        # Enhanced dorks list from the attached file
        self.enhanced_dorks = self.load_enhanced_dorks()
        
        self.init_csv()
        
        # Suppress warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    def load_enhanced_dorks(self):
        """Load enhanced dorks from attached file content"""
        enhanced_dorks = [
            # Basic keywords
            '"Kashmir"', '"Khalistan"', '"Balochistan"', '"Arunachal Pradesh"',
            '"Indian occupation of Kashmir"', '"settler colonialism in Kashmir"',
            '"Kashmiri freedom struggle"', '"war crimes in Kashmir"',
            '"Indian Army atrocities"', '"Sikh referendum"', '"Free Nagalim"',
            '"Line of Actual Control"',
            
            # Hindi keywords
            '"कश्मीर"', '"खालिस्तान"', '"भारतीय सेना"', '"अत्याचार"',
            '"ज़ुल्म"', '"आज़ादी"', '"कब्जा"',
            
            # Social issues
            '"Hindutva extremism"', '"Brahmanical patriarchy"', '"caste oppression"',
            '"Dalit atrocities"', '"Islamophobia in India"', '"anti-muslim violence"',
            '"persecution of Christians"', '"CAA NRC protest"', '"Manipur violence"',
            '"Farmers Protest"', '"religious intolerance"', '"minorities unsafe"',
            
            # Political keywords
            '"fascist India"', '"Indian apartheid"', '"saffron terror"',
            '"ethnic cleansing"', '"Indian genocide"', '"dictatorship"',
            '"failed state"', '"state-sponsored terrorism"', '"silencing dissent"',
            '"death of democracy"', '"Godi media"', '"puppet media"',
            
            # Economic keywords
            '"failing Indian economy"', '"jobless growth"', '"crony capitalism"',
            '"rising inequality"', '"Adani scam"', '"Ambani"', '"poverty in India"',
            
            # Historical events
            '"1984 Sikh genocide"', '"Babri Masjid demolition"',
            '"Gujarat riots 2002"', '"Operation Blue Star"',
            
            # Advanced searches
            '"India" AND "human rights report" AND (Amnesty OR "Human Rights Watch")',
            '"Kashmir" AND ("UN report" OR "plebiscite")',
            '"China" AND "border" AND ("aggression" OR "incursion" OR "occupation")',
            'filetype:pdf "India" AND ("fact-finding report" OR "atrocities")',
            'site:youtube.com intitle:("Exposed" OR "The Dark Side of" OR "The Truth About") "India"',
            'site:medium.com ("The Failure of Modi\'s India" OR "The End of Secular India")'
        ]
        
        return enhanced_dorks
    
    def init_csv(self):
        """Initialize CSV file with enhanced headers"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'timestamp', 'title', 'content', 'url', 'source', 
                    'published_date', 'keywords_found', 'collection_method',
                    'domain', 'engagement_score', 'threat_level', 'language',
                    'geographic_origin', 'platform_type', 'sentiment_score'
                ])
    
    def save_to_csv(self, article_data, method="Unknown"):
        """Enhanced save to CSV with additional fields"""
        try:
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Parse domain from URL
                domain = ""
                if article_data.get('url'):
                    try:
                        domain = urlparse(article_data['url']).netloc
                    except:
                        domain = "unknown"
                
                # Determine platform type
                platform_type = self.determine_platform_type(domain)
                
                writer.writerow([
                    datetime.now().isoformat(),
                    article_data.get('title', ''),
                    article_data.get('content', ''),
                    article_data.get('url', ''),
                    article_data.get('source', ''),
                    article_data.get('published_date', ''),
                    json.dumps(article_data.get('keywords_found', [])),
                    method,
                    domain,
                    article_data.get('engagement_score', 0),
                    article_data.get('threat_level', 'low'),
                    article_data.get('language', 'unknown'),
                    article_data.get('geographic_origin', 'unknown'),
                    platform_type,
                    article_data.get('sentiment_score', 0)
                ])
                print(f"✅ Enhanced save: {article_data.get('title', 'No title')[:50]}... [{platform_type}]")
        except Exception as e:
            print(f"❌ Error saving to CSV: {e}")
    
    def determine_platform_type(self, domain):
        """Determine platform type from domain"""
        platform_mapping = {
            'twitter.com': 'social_media',
            'x.com': 'social_media',
            'facebook.com': 'social_media',
            'instagram.com': 'social_media',
            'youtube.com': 'video_platform',
            'tiktok.com': 'video_platform',
            'reddit.com': 'forum',
            'medium.com': 'blog_platform',
            'wordpress.com': 'blog_platform',
            'blogspot.com': 'blog_platform',
            'telegram.org': 'messaging',
            'whatsapp.com': 'messaging'
        }
        
        for key, value in platform_mapping.items():
            if key in domain.lower():
                return value
        
        if any(news_indicator in domain.lower() for news_indicator in ['news', 'times', 'post', 'daily', 'herald']):
            return 'news_media'
        
        return 'website'
    
    def google_dork_search(self, dork=None, max_results_per_dork=20, delay_range=(3, 8), **kwargs):
        """Enhanced Google Dork search with better error handling.

        Accepts either a single `dork` string or iterates self.enhanced_dorks.
        Supports `max_results` as an alias for compatibility.
        """
        # backward-compat: accept max_results kw
        if 'max_results' in kwargs and kwargs.get('max_results') is not None:
            try:
                max_results_per_dork = int(kwargs.get('max_results'))
            except Exception:
                pass

        print(colored("\n🔍 Starting Enhanced Google Dork Search for Anti-India Campaigns", 'cyan', attrs=['bold']))
        print(colored(f"📊 Total dorks to process: {len(self.enhanced_dorks)}", 'cyan'))

        all_found_urls = []

        # Save results to file
        with open(self.found_urls_file, 'w', encoding='utf-8') as f:
            f.write(f"# Enhanced Anti-India Campaign Detection Results\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Total Dorks: {len(self.enhanced_dorks)}\n\n")

            # decide which dorks to process: single dork or the full list
            dorks_to_process = [dork] if dork else self.enhanced_dorks

            for i, dork in enumerate(dorks_to_process):
                print(colored(f'\n--- [ {i+1}/{len(self.enhanced_dorks)} ] Searching: {str(dork)[:60]}... ---', 'magenta'))
                f.write(f"\n# =======================================================\n")
                f.write(f"# Dork {i+1}: {dork}\n")
                f.write(f"# =======================================================\n")

                dork_urls = []

                try:
                    # Enhanced search with better parameters
                    for url in search(dork, num_results=max_results_per_dork, sleep_interval=2):
                        try:
                            print(colored('[+] Found > ', 'yellow') + url)
                        except Exception:
                            pass
                        f.write(url + "\n")
                        dork_urls.append(url)
                        all_found_urls.append({
                            'url': url,
                            'dork': dork,
                            'found_at': datetime.now().isoformat(),
                            'search_index': i + 1
                        })

                        # Process found URL immediately
                        try:
                            self.process_found_url(url, dork)
                        except Exception as e:
                            print(colored(f"  ❌ Error processing found URL: {e}", 'red'))

                except Exception as e:
                    error_msg = f'[!] Error during search for "{dork}": {e}'
                    try:
                        print(colored(error_msg, 'red'))
                    except Exception:
                        print(error_msg)
                    f.write(f"# ERROR: {error_msg}\n")

                    if "429" in str(e) or "blocked" in str(e).lower():
                        print(colored('[!] Rate limited. Waiting 90 seconds...', 'red'))
                        time.sleep(90)
                    else:
                        print(colored('[!] Other error. Waiting 30 seconds...', 'red'))
                        time.sleep(30)
                    continue

                # Random delay between dorks
                sleep_time = random.uniform(delay_range[0], delay_range[1])
                print(colored(f'[+] Dork complete ({len(dork_urls)} URLs found). Sleeping {sleep_time:.1f}s...', 'blue'))
                time.sleep(sleep_time)

        print(colored(f'\n🎯 Enhanced search complete! Total URLs found: {len(all_found_urls)}', 'green', attrs=['bold']))
        print(colored(f'📁 Results saved to: {self.found_urls_file}', 'green'))

        return all_found_urls
    
    def process_found_url(self, url, dork):
        """Process a found URL and extract content"""
        try:
            # Skip certain file types and irrelevant URLs
            if any(ext in url.lower() for ext in ['.pdf', '.doc', '.zip', '.mp4', '.jpg', '.png']):
                return
            
            if '/search?' in url or 'google.com' in url:
                return
            
            response = self.session.get(url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract title
                title_tag = soup.find('title')
                title = title_tag.get_text().strip() if title_tag else "No title"
                
                # Extract content
                content = self.extract_content(soup)
                
                # Check for anti-India keywords
                keywords_found = self.find_keywords_in_text(title + " " + content)
                
                if keywords_found:  # Only save if anti-India content is found
                    article_data = {
                        'title': title,
                        'content': content[:2000],  # Limit content length
                        'url': url,
                        'source': urlparse(url).netloc,
                        'published_date': datetime.now().isoformat(),
                        'keywords_found': keywords_found,
                        'threat_level': self.assess_threat_level(keywords_found, content),
                        'language': self.detect_language(content),
                        'geographic_origin': self.detect_geographic_origin(content, url),
                        'sentiment_score': self.calculate_sentiment_score(content)
                    }
                    
                    # Save to database and CSV
                    save_article(article_data)
                    self.save_to_csv(article_data, method="Google_Dork_Enhanced")
                    
                    print(colored(f"  💾 Saved anti-India content: {title[:40]}...", 'green'))
                
        except Exception as e:
            print(colored(f"  ❌ Error processing {url}: {e}", 'red'))
    
    def extract_content(self, soup):
        """Extract meaningful content from webpage"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Try different content selectors
        content_selectors = [
            'article', '.content', '.post-content', '.entry-content',
            '.article-body', '.story-body', 'main', '.main-content'
        ]
        
        content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content = ' '.join([elem.get_text() for elem in elements])
                break
        
        # Fallback to body if no specific content found
        if not content:
            body = soup.find('body')
            if body:
                content = body.get_text()
        
        # Clean up content
        content = re.sub(r'\s+', ' ', content).strip()
        return content
    
    def find_keywords_in_text(self, text):
        """Find anti-India keywords in text"""
        text_lower = text.lower()
        found_keywords = []
        
        # Check enhanced keywords
        all_keywords = ANTI_INDIA_KEYWORDS + [
            'kashmir liberation', 'free kashmir', 'occupied kashmir',
            'khalistan movement', 'sikh referendum', 'punjab independence',
            'indian fascism', 'modi dictatorship', 'bjp terrorism',
            'hindu extremism', 'islamophobia india', 'minority persecution',
            'human rights violations india', 'war crimes kashmir',
            'indian apartheid', 'ethnic cleansing india',
            'manipur violence', 'farmers protest suppression',
            'press freedom india', 'democracy death india'
        ]
        
        for keyword in all_keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def assess_threat_level(self, keywords_found, content):
        """Assess threat level based on keywords and content"""
        high_threat_indicators = [
            'genocide', 'ethnic cleansing', 'war crimes', 'terrorism',
            'fascism', 'dictatorship', 'apartheid', 'occupation'
        ]
        
        medium_threat_indicators = [
            'boycott', 'protest', 'violation', 'suppression',
            'extremism', 'persecution', 'atrocities'
        ]
        
        content_lower = content.lower()
        
        for indicator in high_threat_indicators:
            if indicator in content_lower:
                return 'high'
        
        for indicator in medium_threat_indicators:
            if indicator in content_lower:
                return 'medium'
        
        return 'low' if keywords_found else 'minimal'
    
    def detect_language(self, content):
        """Simple language detection"""
        # Hindi/Devanagari script detection
        if re.search(r'[\u0900-\u097F]', content):
            return 'hindi'
        # Urdu/Arabic script detection
        elif re.search(r'[\u0600-\u06FF]', content):
            return 'urdu'
        # Chinese characters
        elif re.search(r'[\u4e00-\u9fff]', content):
            return 'chinese'
        else:
            return 'english'
    
    def detect_geographic_origin(self, content, url):
        """Detect geographic origin from content and URL"""
        country_indicators = {
            'pakistan': ['.pk', 'pakistan', 'islamabad', 'karachi', 'lahore'],
            'china': ['.cn', 'china', 'beijing', 'chinese', 'ccp'],
            'canada': ['.ca', 'canada', 'toronto', 'vancouver', 'ottawa'],
            'uk': ['.uk', '.co.uk', 'britain', 'london', 'british'],
            'usa': ['.us', 'america', 'washington', 'american'],
            'turkey': ['.tr', 'turkey', 'ankara', 'istanbul', 'turkish']
        }
        
        content_lower = content.lower()
        url_lower = url.lower()
        
        for country, indicators in country_indicators.items():
            for indicator in indicators:
                if indicator in content_lower or indicator in url_lower:
                    return country
        
        return 'unknown'
    
    def calculate_sentiment_score(self, content):
        """Simple sentiment scoring"""
        negative_words = [
            'hate', 'evil', 'bad', 'terrible', 'awful', 'disgusting',
            'corrupt', 'criminal', 'violent', 'dangerous', 'threat',
            'destroy', 'attack', 'kill', 'murder', 'genocide'
        ]
        
        positive_words = [
            'good', 'great', 'excellent', 'wonderful', 'peaceful',
            'democratic', 'free', 'justice', 'rights', 'help'
        ]
        
        content_lower = content.lower()
        
        negative_count = sum(1 for word in negative_words if word in content_lower)
        positive_count = sum(1 for word in positive_words if word in content_lower)
        
        # Simple scoring: -1 to 1 scale
        total_words = len(content.split())
        if total_words == 0:
            return 0
        
        score = (positive_count - negative_count) / max(total_words, 1) * 100
        return max(-1, min(1, score))  # Clamp between -1 and 1
    
    def run_comprehensive_collection(self):
        """Run comprehensive data collection using all methods"""
        print(colored("🚀 Starting Comprehensive Anti-India Campaign Detection", 'cyan', attrs=['bold']))
        
        # 1. Enhanced Google Dork Search
        print(colored("\n📍 Phase 1: Enhanced Google Dork Search", 'blue'))
        google_results = self.google_dork_search()
        
        # 2. News API Collection
        print(colored("\n📍 Phase 2: News API Collection", 'blue'))
        news_results = self.collect_from_newsapi(days_back=7, max_articles=100)
        
        print(colored(f"\n✅ Comprehensive collection complete!", 'green', attrs=['bold']))
        print(colored(f"📊 Total Google Dork results: {len(google_results)}", 'green'))
        print(colored(f"📊 Total NewsAPI articles: {news_results}", 'green'))
        print(colored(f"📁 Enhanced data saved to: {self.csv_file}", 'green'))
        
        return {
            'google_dork_results': len(google_results),
            'newsapi_results': news_results,
            'total_processed': len(google_results) + news_results,
            'output_file': self.csv_file
        }

    def collect_with_engagement_tracking(self, *args, **kwargs):
        """Compatibility wrapper used by the dashboard.

        This will ensure the database is initialized, run the comprehensive
        collection (Google dorks + NewsAPI), and return the total number of
        saved items as an integer. It also attempts to call any engagement
        analysis steps if available.
        """
        # Ensure DB ready
        try:
            self.ensure_database()
        except Exception as e:
            print(f"\u274c Failed to ensure database: {e}")

        # Run the comprehensive collection
        try:
            results = self.run_comprehensive_collection()
        except Exception as e:
            print(f"\u274c Comprehensive collection failed: {e}")
            return 0

        total = 0
        try:
            total = int(results.get('total_processed', 0)) if isinstance(results, dict) else 0
        except Exception:
            total = 0

        # Optional: attempt to call engagement analyzer if present
        try:
            from engagement_analyzer import compute_engagement_metrics
            # compute_engagement_metrics should accept a DB path or return summary
            try:
                engagement_summary = compute_engagement_metrics()
                print(f"\u2705 Engagement metrics: {engagement_summary}")
            except Exception:
                # ignore engagement computation failures
                pass
        except Exception:
            # engagement_analyzer not available; skip
            pass

        return total
    
    def collect_from_newsapi(self, days_back=7, max_articles=100):
        """Collect anti-India campaign news from NewsAPI and save to DB"""
        import datetime
        from database import save_article
        from config import ANTI_INDIA_KEYWORDS
        
        if not self.newsapi_key:
            print("❌ No NewsAPI key configured!")
            return 0
        
        base_url = "https://newsapi.org/v2/everything"
        total_saved = 0
        today = datetime.datetime.utcnow()
        from_date = (today - datetime.timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        for keyword in ANTI_INDIA_KEYWORDS:
            params = {
                'q': keyword,
                'from': from_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'apiKey': self.newsapi_key,
                'pageSize': 20
            }
            try:
                resp = self.session.get(base_url, params=params, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    for article in data.get('articles', []):
                        article_data = {
                            'title': article.get('title'),
                            'content': article.get('content') or article.get('description'),
                            'url': article.get('url'),
                            'source': article.get('source', {}).get('name'),
                            'published_at': article.get('publishedAt'),
                            'collected_at': today.strftime('%Y-%m-%dT%H:%M:%SZ'),
                            'method': 'NewsAPI',
                            'keywords_found': keyword,
                            'sentiment_score': self.calculate_sentiment_score(article.get('content') or "")
                        }
                        save_article(article_data)
                        total_saved += 1
                        if total_saved >= max_articles:
                            print(f"✅ Saved {total_saved} news articles from NewsAPI.")
                            return total_saved
                else:
                    print(f"❌ NewsAPI error: {resp.status_code} {resp.text}")
            except Exception as e:
                print(f"❌ NewsAPI request failed: {e}")
        print(f"✅ Saved {total_saved} news articles from NewsAPI.")
        return total_saved

    def ensure_database(self):
        """Ensure the database and articles table exist before saving."""
        from database import init_database
        try:
            init_database()
            print("✅ Database initialized and ready.")
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")

def main():
    """Main function to run enhanced data collection"""
    print(colored("🛡️  Enhanced Anti-India Campaign Detection System", 'cyan', attrs=['bold']))
    print(colored("=" * 60, 'cyan'))
    
    collector = EnhancedDataCollector()
    results = collector.run_comprehensive_collection()
    
    print(colored("\n📋 Collection Summary:", 'green', attrs=['bold']))
    for key, value in results.items():
        print(colored(f"  {key}: {value}", 'green'))

if __name__ == "__main__":
    main()
