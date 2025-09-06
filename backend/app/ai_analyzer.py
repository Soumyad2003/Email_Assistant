import os
import re
import json
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
import requests
import logging

load_dotenv()

class AIAnalyzer:
    """AI-powered email analyzer with Gemini Pro and Hugging Face integration"""
    
    def __init__(self):
        # Configure APIs
        self.setup_gemini()
        self.setup_huggingface()
        
        # Knowledge base for RAG (Retrieval-Augmented Generation)
        self.knowledge_base = {
            "login_issues": {
                "keywords": ["login", "password", "access", "signin", "authenticate"],
                "solution": "For login issues: 1) Try the 'Forgot Password' option 2) Clear browser cache and cookies 3) Disable browser extensions 4) Try incognito/private mode. If issues persist, our technical team can reset your account within 2 hours.",
                "escalation_needed": False
            },
            "billing_issues": {
                "keywords": ["billing", "payment", "charge", "refund", "invoice", "subscription"],
                "solution": "For billing inquiries: 1) Check your account dashboard under 'Billing' section 2) Verify payment method is valid 3) Review usage limits. Our billing team investigates discrepancies within 24 hours and processes refunds within 3-5 business days.",
                "escalation_needed": True
            },
            "technical_issues": {
                "keywords": ["api", "integration", "server", "database", "timeout", "error", "bug"],
                "solution": "For technical issues: 1) Check our status page for known issues 2) Review API documentation 3) Verify API keys and permissions 4) Check rate limits. Our engineering team prioritizes critical technical issues and provides updates every 2 hours.",
                "escalation_needed": True
            },
            "account_issues": {
                "keywords": ["account", "verification", "verify", "register", "signup", "profile"],
                "solution": "For account issues: 1) Check spam folder for verification emails 2) Ensure email address is correct 3) Try requesting new verification email. Account verification emails are sent instantly, and our support team can manually verify accounts within 1 hour if needed.",
                "escalation_needed": False
            },
            "general_inquiry": {
                "keywords": ["question", "help", "information", "how to", "guide"],
                "solution": "Thank you for your inquiry. Our comprehensive documentation and FAQ section covers most common questions. For specific guidance, our support team provides detailed responses within 12-24 hours.",
                "escalation_needed": False
            }
        }
        
        # Urgency classification keywords
        self.urgency_keywords = {
            "urgent": ["urgent", "immediately", "asap", "emergency", "critical"],
            "high": ["important", "priority", "soon", "deadline", "business critical"],
            "normal": ["question", "help", "inquiry", "information"],
            "low": ["feedback", "suggestion", "general", "whenever"]
        }
        
        print("🤖 AI Analyzer initialized with:")
        print(f"   - Gemini Pro: {'✅' if hasattr(self, 'gemini_model') else '❌'}")
        print(f"   - Hugging Face: {'✅' if hasattr(self, 'hf_headers') else '❌'}")
        print(f"   - Knowledge Base: {len(self.knowledge_base)} categories")

    def setup_gemini(self):
        """Initialize Google Gemini Pro"""
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                print("✅ Gemini Pro configured")
            else:
                print("⚠️ Gemini API key not found")
        except Exception as e:
            print(f"❌ Gemini setup error: {e}")

    def setup_huggingface(self):
        """Initialize Hugging Face API"""
        try:
            api_key = os.getenv("HUGGINGFACE_API_KEY")
            if api_key:
                self.hf_headers = {"Authorization": f"Bearer {api_key}"}
                self.hf_sentiment_url = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-xlm-roberta-base-sentiment"
                print("✅ Hugging Face configured")
            else:
                print("⚠️ Hugging Face API key not found")
        except Exception as e:
            print(f"❌ Hugging Face setup error: {e}")

    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment using Hugging Face + Gemini fallback"""
        # Try Hugging Face first
        hf_result = self._huggingface_sentiment(text)
        if hf_result['method'] == 'huggingface':
            return hf_result
        
        # Fallback to Gemini
        return self._gemini_sentiment(text)

    def _huggingface_sentiment(self, text: str) -> Dict:
        """Use Hugging Face for sentiment analysis"""
        try:
            if not hasattr(self, 'hf_headers'):
                return self._fallback_sentiment(text)
            
            response = requests.post(
                self.hf_sentiment_url,
                headers=self.hf_headers,
                json={"inputs": text[:500]},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    # Parse HF response format
                    predictions = result[0] if isinstance(result[0], list) else result
                    best_prediction = max(predictions, key=lambda x: x['score'])
                    
                    # Map to standard format
                    sentiment_map = {
                        'positive': 'Positive',
                        'negative': 'Negative', 
                        'neutral': 'Neutral'
                    }
                    
                    sentiment = sentiment_map.get(best_prediction['label'].lower(), 'Neutral')
                    confidence = round(best_prediction['score'], 3)
                    
                    return {
                        'sentiment': sentiment,
                        'confidence': confidence,
                        'method': 'huggingface',
                        'raw_scores': predictions
                    }
            
            return self._fallback_sentiment(text)
            
        except Exception as e:
            print(f"⚠️ HuggingFace sentiment error: {e}")
            return self._fallback_sentiment(text)

    def _gemini_sentiment(self, text: str) -> Dict:
        """Use Gemini Pro for sentiment analysis"""
        try:
            if not hasattr(self, 'gemini_model'):
                return self._fallback_sentiment(text)
            
            prompt = f"""Analyze the sentiment of this customer email text. Respond with only a JSON object in this exact format:
{{"sentiment": "Positive|Negative|Neutral", "confidence": 0.XX, "reasoning": "brief explanation"}}

Email text: "{text[:500]}"

JSON:"""
            
            response = self.gemini_model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Parse JSON response
            if result_text.startswith('{') and result_text.endswith('}'):
                result = json.loads(result_text)
                return {
                    'sentiment': result.get('sentiment', 'Neutral'),
                    'confidence': float(result.get('confidence', 0.7)),
                    'method': 'gemini',
                    'reasoning': result.get('reasoning', '')
                }
            
            return self._fallback_sentiment(text)
            
        except Exception as e:
            print(f"⚠️ Gemini sentiment error: {e}")
            return self._fallback_sentiment(text)

    def _fallback_sentiment(self, text: str) -> Dict:
        """Keyword-based sentiment analysis fallback"""
        text_lower = text.lower()
        
        positive_words = ['thank', 'appreciate', 'great', 'excellent', 'good', 'love', 'awesome', 'perfect', 'satisfied', 'happy']
        negative_words = ['problem', 'issue', 'error', 'broken', 'failed', 'unable', 'frustrated', 'angry', 'terrible', 'awful', 'disappointed']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if negative_count > positive_count:
            return {'sentiment': 'Negative', 'confidence': 0.8, 'method': 'keyword_fallback'}
        elif positive_count > negative_count:
            return {'sentiment': 'Positive', 'confidence': 0.8, 'method': 'keyword_fallback'}
        else:
            return {'sentiment': 'Neutral', 'confidence': 0.6, 'method': 'keyword_fallback'}

    def determine_priority(self, subject: str, body: str) -> str:
        """Determine email priority with advanced logic"""
        text = f"{subject} {body}".lower()
        
        # Count keywords by priority level
        priority_scores = {"urgent": 0, "high": 0, "normal": 0, "low": 0}
        
        for priority, keywords in self.urgency_keywords.items():
            priority_scores[priority] = sum(1 for keyword in keywords if keyword in text)
        
        # Additional urgent indicators
        critical_phrases = ['production down', 'system failure', 'data loss', 'security breach', 'cannot access', 'billing error']
        if any(phrase in text for phrase in critical_phrases):
            priority_scores["urgent"] += 3
        
        # Determine final priority
        if priority_scores["urgent"] >= 2:
            return "Urgent"
        elif priority_scores["urgent"] >= 1 or priority_scores["high"] >= 2:
            return "High"
        elif priority_scores["normal"] >= 1:
            return "Normal"
        else:
            return "Low"

    def find_relevant_knowledge(self, subject: str, body: str) -> Dict:
        """Find relevant knowledge base entry using RAG"""
        text = f"{subject} {body}".lower()
        
        # Score each knowledge category
        category_scores = {}
        for category, info in self.knowledge_base.items():
            score = sum(1 for keyword in info["keywords"] if keyword in text)
            if score > 0:
                category_scores[category] = score
        
        # Return best matching category
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])[0]
            return {
                'category': best_category,
                'info': self.knowledge_base[best_category],
                'relevance_score': category_scores[best_category]
            }
        
        # Return general inquiry as fallback
        return {
            'category': 'general_inquiry',
            'info': self.knowledge_base['general_inquiry'],
            'relevance_score': 0
        }

    def extract_advanced_info(self, email_data: Dict) -> Dict:
        """Extract comprehensive information from email"""
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        sender = email_data.get('sender', '')
        
        # Basic extraction (reuse from previous)
        basic_info = email_data.get('extracted_info', {})
        
        # Advanced extraction
        advanced_info = {
            # Customer details
            'customer_domain': sender.split('@')[1] if '@' in sender else '',
            'is_business_email': any(domain in sender.lower() for domain in ['.com', '.org', '.net', '.biz']),
            
            # Content analysis
            'question_count': body.count('?'),
            'exclamation_count': body.count('!'),
            'caps_percentage': sum(1 for c in body if c.isupper()) / len(body) if body else 0,
            
            # Request type classification
            'request_type': self._classify_request_type(subject, body),
            'complexity_score': self._calculate_complexity(body),
            'estimated_resolution_time': self._estimate_resolution_time(subject, body),
            
            # Emotion indicators
            'emotion_indicators': self._detect_emotions(body),
            'customer_tier': self._classify_customer_tier(sender),
        }
        
        # Merge with basic info
        return {**basic_info, **advanced_info}

    def _classify_request_type(self, subject: str, body: str) -> str:
        """Classify the type of customer request"""
        text = f"{subject} {body}".lower()
        
        if any(word in text for word in ['refund', 'cancel', 'unsubscribe']):
            return 'cancellation_request'
        elif any(word in text for word in ['bug', 'error', 'not working', 'broken']):
            return 'bug_report'
        elif any(word in text for word in ['how to', 'tutorial', 'guide', 'documentation']):
            return 'information_request'
        elif any(word in text for word in ['feature', 'improvement', 'suggestion']):
            return 'feature_request'
        elif any(word in text for word in ['billing', 'payment', 'charge']):
            return 'billing_inquiry'
        else:
            return 'general_support'

    def _calculate_complexity(self, body: str) -> int:
        """Calculate complexity score (1-10)"""
        factors = [
            len(body.split()) > 100,  # Long email
            body.count('?') > 2,      # Multiple questions
            len(re.findall(r'\d+', body)) > 3,  # Many numbers/codes
            any(tech in body.lower() for tech in ['api', 'database', 'server', 'integration']),  # Technical
            body.count('\n') > 5      # Multiple paragraphs
        ]
        return min(10, sum(factors) * 2 + 3)  # Base complexity of 3

    def _estimate_resolution_time(self, subject: str, body: str) -> str:
        """Estimate resolution timeframe"""
        text = f"{subject} {body}".lower()
        
        if any(word in text for word in ['password', 'login', 'access']):
            return '2-4 hours'
        elif any(word in text for word in ['billing', 'refund', 'payment']):
            return '1-2 business days'
        elif any(word in text for word in ['api', 'integration', 'technical']):
            return '2-5 business days'
        elif any(word in text for word in ['bug', 'error', 'broken']):
            return '3-7 business days'
        else:
            return '1-3 business days'

    def _detect_emotions(self, text: str) -> Dict:
        """Detect specific emotions in customer text"""
        emotions = {
            'frustration': ['frustrated', 'annoying', 'annoyed', 'irritated'],
            'urgency': ['urgent', 'asap', 'immediately', 'quick', 'fast'],
            'confusion': ['confused', 'unclear', 'understand', 'explain', 'help'],
            'satisfaction': ['thank', 'appreciate', 'satisfied', 'happy', 'pleased'],
            'anger': ['angry', 'mad', 'furious', 'unacceptable', 'terrible']
        }
        
        detected = {}
        text_lower = text.lower()
        
        for emotion, keywords in emotions.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            detected[emotion] = count
        
        # Find dominant emotion
        dominant = max(detected.items(), key=lambda x: x[1])
        
        return {
            'scores': detected,
            'dominant_emotion': dominant[0] if dominant[1] > 0 else 'neutral',
            'intensity': min(10, dominant[1] * 3)
        }

    def _classify_customer_tier(self, sender: str) -> str:
        """Classify customer tier based on email domain"""
        domain = sender.split('@')[1].lower() if '@' in sender else ''
        
        # Enterprise domains (examples)
        enterprise_domains = ['microsoft.com', 'google.com', 'amazon.com', 'apple.com', 'facebook.com']
        startup_indicators = ['startup', 'ventures', 'labs', 'inc']
        
        if domain in enterprise_domains:
            return 'enterprise'
        elif any(indicator in domain for indicator in startup_indicators):
            return 'startup'
        elif domain.endswith('.edu'):
            return 'education'
        elif domain.endswith('.gov'):
            return 'government'
        else:
            return 'standard'

    def analyze_email_complete(self, email_data: Dict) -> Dict:
        """Complete analysis of an email"""
        try:
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            
            # Sentiment analysis
            sentiment_result = self.analyze_sentiment(body)
            
            # Priority determination  
            priority = self.determine_priority(subject, body)
            
            # Knowledge base lookup
            knowledge = self.find_relevant_knowledge(subject, body)
            
            # Advanced information extraction
            extracted_info = self.extract_advanced_info(email_data)
            
            # Compile complete analysis
            analysis = {
                'sentiment': sentiment_result,
                'priority': priority,
                'knowledge_match': knowledge,
                'extracted_info': extracted_info,
                'analysis_timestamp': datetime.now().isoformat(),
                'ai_confidence': self._calculate_overall_confidence(sentiment_result, knowledge)
            }
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error in complete email analysis: {e}")
            return {
                'sentiment': {'sentiment': 'Neutral', 'confidence': 0.5, 'method': 'error'},
                'priority': 'Normal',
                'knowledge_match': {'category': 'general_inquiry', 'relevance_score': 0},
                'extracted_info': {},
                'analysis_timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

    def _calculate_overall_confidence(self, sentiment_result: Dict, knowledge_match: Dict) -> float:
        """Calculate overall AI confidence score"""
        sentiment_conf = sentiment_result.get('confidence', 0.5)
        knowledge_conf = min(1.0, knowledge_match.get('relevance_score', 0) / 3)
        
        return round((sentiment_conf * 0.6 + knowledge_conf * 0.4), 3)
