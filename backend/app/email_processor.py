import pandas as pd
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
import heapq
from dataclasses import dataclass, field
import logging

load_dotenv()
logger = logging.getLogger(__name__)

@dataclass
class EmailTask:
    """Email task for priority queue processing"""
    priority: int  # Lower number = higher priority (1=Urgent, 2=High, 3=Normal)
    timestamp: float
    email_id: str
    email_data: Dict
    
    def __lt__(self, other):
        """Priority queue comparison - lower priority number comes first"""
        if self.priority == other.priority:
            return self.timestamp < other.timestamp
        return self.priority < other.priority

class EmailPriorityQueue:
    """Priority queue for handling emails by urgency"""
    
    def __init__(self, max_size: int = 1000):
        self.queue = []
        self.max_size = max_size
        self.processed_count = 0
        
    def add_email(self, email_data: Dict, priority: str) -> bool:
        """Add email to priority queue"""
        try:
            # Convert priority to number (lower = more urgent)
            priority_map = {
                "Urgent": 1,
                "High": 2, 
                "Normal": 3,
                "Low": 4
            }
            
            priority_num = priority_map.get(priority, 3)
            
            # Create task
            task = EmailTask(
                priority=priority_num,
                timestamp=datetime.now().timestamp(),
                email_id=email_data.get('id', f"email_{len(self.queue)}"),
                email_data=email_data
            )
            
            # Add to heap queue
            if len(self.queue) < self.max_size:
                heapq.heappush(self.queue, task)
                return True
            else:
                # Queue full, replace lowest priority if this is higher
                if task.priority < self.queue[0].priority:
                    heapq.heapreplace(self.queue, task)
                    return True
                return False
                
        except Exception as e:
            logging.error(f"Error adding email to queue: {e}")
            return False
    
    def get_next_email(self) -> Optional[EmailTask]:
        """Get highest priority email from queue"""
        if self.queue:
            task = heapq.heappop(self.queue)
            self.processed_count += 1
            return task
        return None
    
    def get_queue_stats(self) -> Dict:
        """Get priority queue statistics"""
        priority_counts = {"Urgent": 0, "High": 0, "Normal": 0, "Low": 0}
        priority_map = {1: "Urgent", 2: "High", 3: "Normal", 4: "Low"}
        
        for task in self.queue:
            priority_name = priority_map.get(task.priority, "Normal")
            priority_counts[priority_name] += 1
            
        return {
            "total_queued": len(self.queue),
            "total_processed": self.processed_count,
            "priority_breakdown": priority_counts,
            "next_priority": priority_map.get(self.queue[0].priority, "None") if self.queue else "None"
        }

class EnhancedEmailProcessor:
    """Email processor for CSV sample emails (IMAP removed)"""
    
    def __init__(self, csv_path: str = None):
        # CSV configuration
        if csv_path is None:
            csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_emails.csv')
        self.csv_path = csv_path
        
        # Priority queue
        self.priority_queue = EmailPriorityQueue()
        
        # Support-related keywords for filtering
        self.support_keywords = [
            'support', 'help', 'query', 'request', 'urgent', 'critical', 
            'issue', 'problem', 'error', 'question', 'assistance', 
            'billing', 'account', 'login', 'access', 'technical',
            'bug', 'feature', 'feedback', 'complaint', 'refund'
        ]
        
        # Urgency detection keywords
        self.urgent_keywords = [
            'urgent', 'immediately', 'critical', 'emergency', 'asap',
            'cannot access', 'system down', 'not working', 'broken',
            'servers down', 'inaccessible', 'immediate', 'billing error',
            'deadline', 'priority', 'escalate', 'frustrated', 'angry',
            'losing money', 'business critical', 'production down'
        ]
        
        print(f"📧 Enhanced Email Processor initialized")
        print(f"   - CSV mode: Enabled")
        print(f"   - Priority queue: Enabled")

    def load_emails_from_csv(self) -> List[Dict]:
        """Load emails from CSV file"""
        try:
            print(f"📂 Loading emails from: {self.csv_path}")
            
            if not os.path.exists(self.csv_path):
                print(f"❌ CSV file not found: {self.csv_path}")
                return []
            
            df = pd.read_csv(self.csv_path)
            print(f"📊 Found {len(df)} emails in CSV")
            
            emails = []
            for index, row in df.iterrows():
                try:
                    email_data = {
                        'id': f"csv_{index}",
                        'sender': str(row['sender']).strip(),
                        'subject': str(row['subject']).strip(),
                        'body': str(row['body']).strip(),
                        'sent_date': self.parse_date(str(row['sent_date'])),
                        'source': 'csv'
                    }
                    emails.append(email_data)
                except Exception as e:
                    print(f"⚠️ Error processing CSV row {index}: {e}")
                    continue
            
            print(f"✅ Successfully loaded {len(emails)} emails from CSV")
            return emails
            
        except Exception as e:
            print(f"❌ Error loading CSV emails: {e}")
            return []

    def parse_date(self, date_string: str) -> datetime:
        """Parse date string to datetime object"""
        date_formats = [
            "%d-%m-%Y %H:%S",
            "%Y-%m-%d %H:%M:%S", 
            "%d/%m/%Y %H:%S",
            "%Y-%m-%d",
            "%d-%m-%Y"
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_string.strip(), fmt)
            except ValueError:
                continue
        
        print(f"⚠️ Could not parse date: {date_string}")
        return datetime.now()

    def filter_support_emails(self, emails: List[Dict]) -> List[Dict]:
        """Filter emails containing support-related keywords"""
        if not emails:
            return []
            
        filtered_emails = []
        
        for email in emails:
            subject_lower = email['subject'].lower()
            body_lower = email['body'].lower()
            
            # Check for support keywords
            is_support_email = any(
                keyword in subject_lower or keyword in body_lower 
                for keyword in self.support_keywords
            )
            
            if is_support_email:
                filtered_emails.append(email)
        
        print(f"🔍 Filtered {len(filtered_emails)} support emails from {len(emails)} total")
        return filtered_emails

    def determine_priority(self, subject: str, body: str) -> str:
        """Determine email priority based on urgency keywords"""
        text = f"{subject} {body}".lower()
        
        # Count urgent keywords
        urgent_count = sum(1 for keyword in self.urgent_keywords if keyword in text)
        
        # Advanced priority logic
        if urgent_count >= 3 or any(critical in text for critical in ['production down', 'system failure', 'data loss']):
            return "Urgent"
        elif urgent_count >= 2 or any(high in text for high in ['critical', 'emergency', 'cannot access']):
            return "Urgent"  
        elif urgent_count >= 1 or any(medium in text for medium in ['asap', 'immediately', 'urgent']):
            return "High"
        else:
            return "Normal"
