import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.email_processor import EnhancedEmailProcessor

def test_enhanced_processor():
    print("🚀 Testing Enhanced Email Processor...")
    print("=" * 60)
    
    # Initialize processor
    processor = EnhancedEmailProcessor(use_imap=False)  # CSV mode for testing
    
    # Test 1: Load and process emails
    print("📧 Test 1: Loading and processing emails")
    emails = processor.get_all_emails()
    
    if not emails:
        print("❌ No emails loaded")
        return False
    
    print(f"✅ Processed {len(emails)} emails")
    
    # Test 2: Priority queue functionality
    print("\n⚡ Test 2: Priority queue processing")
    
    urgent_count = 0
    high_count = 0
    normal_count = 0
    
    # Process emails by priority
    processed_emails = []
    for i in range(min(10, len(emails))):  # Process up to 10 emails
        next_email = processor.get_next_priority_email()
        if next_email:
            priority = next_email.get('priority', 'Normal')
            processed_emails.append(next_email)
            
            if priority == 'Urgent':
                urgent_count += 1
            elif priority == 'High':
                high_count += 1
            else:
                normal_count += 1
                
            print(f"   📨 Email {i+1}: {priority} priority")
            print(f"      From: {next_email['sender']}")
            print(f"      Subject: {next_email['subject'][:50]}...")
    
    # Test 3: Information extraction
    print(f"\n🔍 Test 3: Information extraction sample")
    if processed_emails:
        sample_email = processed_emails[0]
        info = sample_email.get('extracted_info', {})
        
        print(f"   📊 Sample extraction results:")
        print(f"      - Word count: {info.get('word_count', 0)}")
        print(f"      - Urgency score: {info.get('urgency_score', 0)}")  
        print(f"      - Phone numbers: {len(info.get('phone_numbers', []))}")
        print(f"      - Mentioned emails: {len(info.get('mentioned_emails', []))}")
        print(f"      - Technical keywords: {info.get('technical_keywords', [])}")
        print(f"      - Has billing keywords: {info.get('has_billing_keywords', False)}")
    
    # Test 4: Queue statistics
    print(f"\n📈 Test 4: Priority queue statistics")
    queue_stats = processor.priority_queue.get_queue_stats()
    print(f"   - Emails processed: {queue_stats['total_processed']}")
    print(f"   - Still in queue: {queue_stats['total_queued']}")
    print(f"   - Priority breakdown: {queue_stats['priority_breakdown']}")
    print(f"   - Next priority: {queue_stats['next_priority']}")
    
    print(f"\n✅ Enhanced Email Processor test completed successfully!")
    print(f"   - Urgent emails processed first: {urgent_count}")
    print(f"   - High priority emails: {high_count}")  
    print(f"   - Normal priority emails: {normal_count}")
    
    return True

if __name__ == "__main__":
    test_enhanced_processor()
