import requests
import json
import re
from database import get_articles, save_article

# Configuration constants
GEMINI_API_KEY = ""  # Add your Gemini API key if needed
TARGET_COUNTRIES = [
    "Pakistan", "China", "Bangladesh", "Turkey", "Iran", "Malaysia", 
    "Afghanistan", "Myanmar", "Sri Lanka", "Nepal", "Maldives"
]

class AIAnalyzer:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    def analyze_content(self, title, content):
        """Enhanced analysis to filter anti-India content specifically"""
        prompt = f"""
        Analyze this content SPECIFICALLY for anti-India sentiment and campaigns. 
        Only classify as relevant if it contains genuine anti-India sentiment, boycott calls, or disinformation.
        
        STRICT CRITERIA:
        - Must contain explicit anti-India sentiment (hate, boycott, disinformation)
        - Must target India as a country, government, or people
        - Exclude: General criticism, news reports without bias, unrelated content
        
        Content Analysis:
        Title: {title}
        Content: {content[:1000]}
        
        Provide analysis in JSON format:
        {{
            "is_anti_india": true/false,
            "sentiment_score": -1.0 to 1.0 (negative = anti-India),
            "relevance_score": 1-5 (5 = highly anti-India),
            "countries_mentioned": [],
            "classification": "Disinformation|Hate Speech|Boycott Campaign|Political Criticism|Not Relevant",
            "threat_level": "HIGH|MEDIUM|LOW|NONE",
            "reasoning": "Brief explanation"
        }}
        """
        
        try:
            headers = {
                'Content-Type': 'application/json',
                'X-goog-api-key': self.api_key
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }
            
            response = requests.post(self.base_url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                text_content = result['candidates'][0]['content']['parts'][0]['text']
                
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', text_content, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                    
                    # Only return results for genuinely anti-India content
                    if analysis.get('is_anti_india', False) and analysis.get('relevance_score', 0) >= 3:
                        return {
                            "sentiment_score": analysis.get('sentiment_score', 0),
                            "relevance_score": analysis.get('relevance_score', 1),
                            "countries_mentioned": analysis.get('countries_mentioned', []),
                            "classification": analysis.get('classification', 'Other'),
                            "reasoning": analysis.get('reasoning', 'AI Analysis')
                        }
                    else:
                        # Mark as not relevant
                        return None
            
        except Exception as e:
            print(f"Error analyzing content: {e}")
        
        # Enhanced fallback analysis
        return self.enhanced_fallback_analysis(title, content)
    
    def enhanced_fallback_analysis(self, title, content):
        """Enhanced fallback analysis focused on anti-India content"""
        text = f"{title} {content}".lower()
        
        # Strong anti-India indicators
        strong_anti_india = [
            'boycott india', 'hate india', 'down with india', 'anti india',
            'india terrorist', 'india fascist', 'india genocide', 'india apartheid',
            'kashmir boycott', 'modi fascist', 'bjp terrorist', 'india war crimes'
        ]
        
        # Check for strong anti-India content
        strong_matches = sum(1 for term in strong_anti_india if term in text)
        
        # Only proceed if genuine anti-India content is detected
        if strong_matches == 0:
            return None  # Filter out non-anti-India content
        
        # Calculate sentiment (more negative for anti-India content)
        sentiment_score = -0.3 * strong_matches  # Base negative sentiment
        sentiment_score = max(-1.0, sentiment_score)  # Cap at -1.0
        
        # Check for countries
        countries_found = [country for country in TARGET_COUNTRIES 
                          if country.lower() in text]
        
        # Relevance scoring (only high for confirmed anti-India)
        relevance_score = min(5, 3 + strong_matches)
        
        # Classification based on content
        if any(word in text for word in ['fake', 'propaganda', 'lie', 'disinformation']):
            classification = "Disinformation"
        elif any(word in text for word in ['hate', 'terrorist', 'genocide', 'fascist']):
            classification = "Hate Speech"
        elif any(word in text for word in ['boycott', 'down with']):
            classification = "Boycott Campaign"
        else:
            classification = "Political Criticism"
        
        return {
            "sentiment_score": sentiment_score,
            "relevance_score": relevance_score,
            "countries_mentioned": countries_found,
            "classification": classification,
            "reasoning": f"Detected {strong_matches} anti-India indicators"
        }
    
    def process_unanalyzed_articles(self):
        """Process articles that haven't been analyzed yet"""
        # Get articles without sentiment analysis
        articles_df = get_articles(limit=50)
        unanalyzed = articles_df[articles_df['sentiment_score'].isna()]
        
        processed = 0
        for _, article in unanalyzed.iterrows():
            try:
                analysis = self.analyze_content(article['title'], article['content'] or '')
                
                # Update article with analysis results
                article_data = {
                    'title': article['title'],
                    'content': article['content'],
                    'url': article['url'],
                    'source': article['source'],
                    'published_date': article['published_date'],
                    'sentiment_score': analysis['sentiment_score'],
                    'relevance_score': analysis['relevance_score'],
                    'countries_mentioned': analysis['countries_mentioned'],
                    'keywords_found': json.loads(article['keywords_found']) if article['keywords_found'] else [],
                    'classification': analysis['classification']
                }
                
                save_article(article_data)
                processed += 1
                
            except Exception as e:
                print(f"Error processing article {article['id']}: {e}")
        
        return processed
