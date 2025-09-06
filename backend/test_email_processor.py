import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.email_processor import EmailProcessor

def test_email_processor():
    print("🚀 Testing Email Processor...")
    print("=" * 50)
    
    # Initialize processor
    processor = EmailProcessor()
    
    # Test 1: Load emails from CSV
    print("Test 1: Loading emails from CSV")
    raw_emails = processor.load_emails_from_csv()
    
    if not raw_emails:
        print("❌ Failed to load emails")
        return False
    
    print(f"✅ Loaded {len(raw_emails)} emails")
    
    # Test 2: Filter support emails
    print("\nTest 2: Filtering support emails")
    support_emails = processor.filter_support_emails(raw_emails)
    
    if not support_emails:
        print("❌ No support emails found")
        return False
        
    print(f"✅ Found {len(support_emails)} support emails")
    
    # Test 3: Extract metadata from first email
    print("\nTest 3: Extracting metadata")
    if support_emails:
        first_email = support_emails[0]
        metadata = processor.extract_email_metadata(first_email)
        
        print(f"📧 Sample email metadata:")
        print(f"   - Sender: {first_email['sender']}")
        print(f"   - Subject: {first_email['subject']}")
        print(f"   - Word count: {metadata['word_count']}")
        print(f"   - Urgent word count: {metadata['urgent_word_count']}")
        print(f"   - Has billing keywords: {metadata['has_billing_keywords']}")
        print(f"   - Has technical keywords: {metadata['has_technical_keywords']}")
    
    print("\n✅ Email processor test completed successfully!")
    return True

if __name__ == "__main__":
    test_email_processor()
