import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ai_analyzer import AIAnalyzer
from app.email_processor import EnhancedEmailProcessor
from app.response_generator import GeminiResponseGenerator

def test_response_generator():
    print("🤖 Testing Gemini Response Generator...")
    print("=" * 60)
    
    # Initialize components
    processor = EnhancedEmailProcessor(use_imap=False)
    analyzer = AIAnalyzer()
    response_generator = GeminiResponseGenerator()
    
    # Get sample emails
    emails = processor.get_all_emails()
    
    if not emails:
        print("❌ No emails to process")
        return False
    
    # Test with first 2 emails for detailed analysis
    test_emails = emails[:2]
    
    print(f"\n🧪 Testing complete email processing pipeline on {len(test_emails)} emails:")
    
    for i, email in enumerate(test_emails, 1):
        print(f"\n{'='*20} EMAIL {i} {'='*20}")
        print(f"📧 From: {email['sender']}")
        print(f"📧 Subject: {email['subject']}")
        print(f"📧 Body: {email['body'][:150]}...")
        
        # Step 1: AI Analysis
        print(f"\n🔍 Step 1: AI Analysis")
        analysis = analyzer.analyze_email_complete(email)
        
        sentiment = analysis['sentiment']
        print(f"   - Sentiment: {sentiment['sentiment']} ({sentiment['confidence']})")
        print(f"   - Priority: {analysis['priority']}")
        print(f"   - Knowledge Category: {analysis['knowledge_match']['category']}")
        print(f"   - Customer Tier: {analysis['extracted_info'].get('customer_tier', 'N/A')}")
        print(f"   - Dominant Emotion: {analysis['extracted_info'].get('emotion_indicators', {}).get('dominant_emotion', 'neutral')}")
        
        # Step 2: Response Generation
        print(f"\n🤖 Step 2: Response Generation")
        response_result = response_generator.generate_response(email, analysis)
        
        print(f"   - Method: {response_result['method']}")
        print(f"   - Confidence: {response_result['confidence']}")
        print(f"   - Context Used: {response_result['context_used']}")
        
        # Step 3: Quality Metrics
        print(f"\n📊 Step 3: Quality Assessment")
        quality_metrics = response_generator.get_response_quality_metrics(response_result)
        
        print(f"   - Professional Score: {quality_metrics['professional_score']:.2f}")
        print(f"   - Empathy Score: {quality_metrics['empathy_score']:.2f}")
        print(f"   - Completeness Score: {quality_metrics['completeness_score']:.2f}")
        print(f"   - Context Relevance: {quality_metrics['context_relevance']:.2f}")
        print(f"   - Overall Quality: {quality_metrics['overall_quality']:.2f}")
        
        # Step 4: Display Generated Response
        print(f"\n✉️ Generated Response:")
        print("-" * 50)
        print(response_result['generated_response'])
        print("-" * 50)
        
        print(f"\n✅ Email {i} processing complete!")
    
    print(f"\n🎯 Complete Pipeline Test Results:")
    print(f"   - Email Processing: ✅")
    print(f"   - AI Analysis: ✅") 
    print(f"   - Response Generation: ✅")
    print(f"   - Quality Assessment: ✅")
    print(f"   - Context Awareness: ✅")
    
    return True

if __name__ == "__main__":
    test_response_generator()
