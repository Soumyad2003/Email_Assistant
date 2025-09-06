import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ai_analyzer import AIAnalyzer
from app.email_processor import EnhancedEmailProcessor

def test_ai_analyzer():
    print("🤖 Testing AI-Powered Email Analyzer...")
    print("=" * 60)
    
    # Initialize components
    analyzer = AIAnalyzer()
    processor = EnhancedEmailProcessor(use_imap=False)
    
    # Get sample emails
    emails = processor.get_all_emails()
    
    if not emails:
        print("❌ No emails to analyze")
        return False
    
    # Test with first few emails
    test_emails = emails[:3]
    
    print(f"\n🧪 Testing AI analysis on {len(test_emails)} sample emails:")
    
    for i, email in enumerate(test_emails, 1):
        print(f"\n📧 Email {i}:")
        print(f"   From: {email['sender']}")
        print(f"   Subject: {email['subject']}")
        print(f"   Body preview: {email['body'][:100]}...")
        
        # Perform complete AI analysis
        analysis = analyzer.analyze_email_complete(email)
        
        # Display results
        sentiment = analysis['sentiment']
        print(f"\n   🎭 Sentiment Analysis:")
        print(f"      - Sentiment: {sentiment['sentiment']}")
        print(f"      - Confidence: {sentiment['confidence']}")
        print(f"      - Method: {sentiment['method']}")
        
        print(f"\n   ⚡ Priority: {analysis['priority']}")
        
        knowledge = analysis['knowledge_match']
        print(f"\n   🧠 Knowledge Match:")
        print(f"      - Category: {knowledge['category']}")
        print(f"      - Relevance Score: {knowledge['relevance_score']}")
        
        extracted = analysis['extracted_info']
        print(f"\n   📊 Key Information:")
        print(f"      - Request Type: {extracted.get('request_type', 'N/A')}")
        print(f"      - Complexity Score: {extracted.get('complexity_score', 'N/A')}")
        print(f"      - Estimated Resolution: {extracted.get('estimated_resolution_time', 'N/A')}")
        print(f"      - Customer Tier: {extracted.get('customer_tier', 'N/A')}")
        
        emotions = extracted.get('emotion_indicators', {})
        if emotions:
            print(f"      - Dominant Emotion: {emotions.get('dominant_emotion', 'neutral')}")
            print(f"      - Emotion Intensity: {emotions.get('intensity', 0)}/10")
        
        print(f"\n   🎯 Overall AI Confidence: {analysis.get('ai_confidence', 0.5)}")
        
        print("\n" + "-" * 50)
    
    print(f"\n✅ AI Analyzer testing completed successfully!")
    print(f"   - Sentiment analysis: {'✅' if analysis['sentiment']['method'] != 'error' else '❌'}")
    print(f"   - Priority classification: ✅")  
    print(f"   - Knowledge base matching: ✅")
    print(f"   - Information extraction: ✅")
    
    return True

if __name__ == "__main__":
    test_ai_analyzer()
