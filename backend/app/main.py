from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text, case
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging
import os
from typing import List, Optional
import shutil

# Your existing imports
from .database import engine, get_db
from .models import Base, Email, Response
from .email_processor import EnhancedEmailProcessor
from .gemini_client import GeminiClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="AI Email Assistant API",
    description="Intelligent email management and response system powered by Gemini",
    version="1.0.0"
)

# Update CORS origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://email-assistant-api.onrender.com",  # Add your actual Vercel URL
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Initialize Gemini client
try:
    gemini_client = GeminiClient()
    logger.info("🤖 Gemini AI client initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Gemini client: {e}")
    gemini_client = None

# Initialize email processor
email_processor = EnhancedEmailProcessor()

# Pydantic models
class EmailSendRequest(BaseModel):
    email_id: int
    response_text: str
    send_immediately: bool = False

@app.get("/")
def root():
    return {
        "message": "AI-Powered Email Assistant API",
        "status": "running",
        "ai_engine": "Gemini Pro"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "gemini_available": gemini_client is not None
    }

@app.post("/api/clear-database")
def clear_entire_database(db: Session = Depends(get_db)):
    """Clear entire database - all emails and responses"""
    try:
        logger.info("Starting complete database clear operation")
        deleted_responses = db.query(Response).delete()
        deleted_emails = db.query(Email).delete()
        db.commit()
        
        logger.info(f"Database cleared: {deleted_emails} emails and {deleted_responses} responses deleted")
        return {
            "message": f"Database cleared successfully. Deleted {deleted_emails} emails and {deleted_responses} responses.",
            "deleted_emails": deleted_emails,
            "deleted_responses": deleted_responses
        }
    except Exception as e:
        logger.error(f"Error clearing database: {e}")
        db.rollback()
        return {"error": str(e)}

@app.post("/api/load-emails")
def load_sample_emails(db: Session = Depends(get_db)):
    """Load emails from CSV file WITH Gemini analysis but WITHOUT response generation"""
    if not gemini_client:
        return {"error": "Gemini client not available. Check GEMINI_API_KEY."}
    
    try:
        logger.info("Starting email loading process with Gemini analysis")
        
        raw_emails = email_processor.load_emails_from_csv()
        logger.info(f"Loaded {len(raw_emails)} raw emails from CSV")
        
        filtered_emails = email_processor.filter_support_emails(raw_emails)
        logger.info(f"Filtered to {len(filtered_emails)} support emails")
        
        processed_count = 0
        skipped_count = 0
        
        for email_data in filtered_emails:
            try:
                existing = db.query(Email).filter(
                    Email.sender == email_data['sender'],
                    Email.subject == email_data['subject']
                ).first()
                
                if existing:
                    logger.info(f"Skipping duplicate email from {email_data['sender']}")
                    skipped_count += 1
                    continue
                
                # Run Gemini analysis for sentiment and priority
                logger.info(f"Running Gemini analysis for email from {email_data['sender']}")
                analysis = gemini_client.analyze_email(email_data)
                
                # Create email record WITH Gemini analysis results
                email_record = Email(
                    sender=email_data['sender'],
                    subject=email_data['subject'],
                    body=email_data['body'],
                    sent_date=email_data['sent_date'],
                    sentiment=analysis['sentiment']['sentiment'],
                    sentiment_confidence=analysis['sentiment']['confidence'],
                    priority=analysis['priority'],
                    status="pending"
                )
                
                db.add(email_record)
                processed_count += 1
                
                logger.info(f"Processed email {processed_count}: {analysis['priority']} priority, {analysis['sentiment']['sentiment']} sentiment")
                
            except Exception as e:
                logger.error(f"Error processing individual email: {e}")
                continue
        
        db.commit()
        
        total_in_db = db.query(Email).count()
        logger.info(f"Total emails in database after commit: {total_in_db}")
        
        return {
            "message": f"Successfully processed {processed_count} emails with Gemini analysis (skipped {skipped_count} duplicates). Responses can be generated on-demand.",
            "processed": processed_count,
            "skipped": skipped_count,
            "total_in_csv": len(raw_emails),
            "ai_engine": "Gemini Pro"
        }
        
    except Exception as e:
        logger.error(f"Error in load_sample_emails: {e}")
        db.rollback()
        return {"error": str(e)}

@app.post("/api/upload-csv")
async def upload_csv_emails(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and process emails from CSV file WITH Gemini analysis"""
    if not gemini_client:
        return {"error": "Gemini client not available. Check GEMINI_API_KEY."}
    
    try:
        logger.info(f"Starting CSV upload: {file.filename}")
        
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
        upload_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        upload_path = os.path.join(upload_dir, f"uploaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        with open(upload_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File saved to: {upload_path}")
        
        processor = EnhancedEmailProcessor(csv_path=upload_path)
        raw_emails = processor.load_emails_from_csv()
        filtered_emails = processor.filter_support_emails(raw_emails)
        
        logger.info(f"Processing {len(filtered_emails)} emails from uploaded CSV with Gemini analysis")
        
        processed_count = 0
        skipped_count = 0
        
        for email_data in filtered_emails:
            try:
                existing = db.query(Email).filter(
                    Email.sender == email_data['sender'],
                    Email.subject == email_data['subject']
                ).first()
                
                if existing:
                    skipped_count += 1
                    continue
                
                # Run Gemini analysis
                analysis = gemini_client.analyze_email(email_data)
                
                # Create email record WITH Gemini analysis results
                email_record = Email(
                    sender=email_data['sender'],
                    subject=email_data['subject'],
                    body=email_data['body'],
                    sent_date=email_data['sent_date'],
                    sentiment=analysis['sentiment']['sentiment'],
                    sentiment_confidence=analysis['sentiment']['confidence'],
                    priority=analysis['priority'],
                    status="pending"
                )
                
                db.add(email_record)
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing individual email from upload: {e}")
                continue
        
        db.commit()
        
        try:
            os.remove(upload_path)
        except:
            pass
        
        return {
            "message": f"Successfully uploaded {processed_count} emails with Gemini analysis (skipped {skipped_count} duplicates).",
            "filename": file.filename,
            "total_processed": processed_count,
            "skipped": skipped_count,
            "total_in_file": len(raw_emails),
            "ai_engine": "Gemini Pro"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing uploaded CSV: {e}")
        return {"error": str(e)}

@app.get("/api/emails")
def get_emails(db: Session = Depends(get_db)):
    """Get all emails sorted by priority"""
    try:
        logger.info("Fetching emails from database")
        
        # Custom priority order
        priority_order = case(
            (Email.priority == "Urgent", 1),
            (Email.priority == "High", 2),
            (Email.priority == "Normal", 3),
            (Email.priority == "Low", 4),
            else_=5
        )
        
        emails = db.query(Email).order_by(
            priority_order.asc(),
            Email.sent_date.desc()
        ).all()
        
        logger.info(f"Found {len(emails)} emails in database")
        
        result = []
        for email in emails:
            # Check if response exists
            has_response = db.query(Response).filter(Response.email_id == email.id).first() is not None
            
            result.append({
                "id": email.id,
                "sender": email.sender,
                "subject": email.subject,
                "body": email.body,
                "sent_date": email.sent_date.isoformat() if email.sent_date else None,
                "sentiment": email.sentiment,
                "sentiment_confidence": email.sentiment_confidence,
                "priority": email.priority,
                "status": email.status,
                "has_response": has_response
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error in get_emails: {e}")
        return []

@app.get("/api/emails/{email_id}/response")
def get_email_response(email_id: int, db: Session = Depends(get_db)):
    """Get generated response for an email"""
    try:
        logger.info(f"Fetching response for email ID: {email_id}")
        
        response = db.query(Response).filter(Response.email_id == email_id).first()
        if not response:
            logger.warning(f"No response found for email ID: {email_id}")
            return {"generated_response": "", "final_response": "", "is_sent": 0, "has_response": False}
        
        return {
            "generated_response": response.generated_response or "",
            "final_response": response.final_response or "",
            "is_sent": response.is_sent,
            "has_response": True
        }
        
    except Exception as e:
        logger.error(f"Error in get_email_response: {e}")
        return {"generated_response": "", "final_response": "", "is_sent": 0, "has_response": False}

@app.post("/api/emails/{email_id}/generate-response")
async def generate_response_for_email(email_id: int, db: Session = Depends(get_db)):
    """Generate AI response using Gemini for specific email"""
    if not gemini_client:
        return {"error": "Gemini client not available. Check GEMINI_API_KEY."}
    
    try:
        logger.info(f"Generating Gemini response for email ID: {email_id}")
        
        email = db.query(Email).filter(Email.id == email_id).first()
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        # Prepare email data for Gemini
        email_data = {
            'sender': email.sender,
            'subject': email.subject,
            'body': email.body,
            'sent_date': email.sent_date
        }
        
        # Use existing analysis results
        analysis = {
            'sentiment': {'sentiment': email.sentiment, 'confidence': email.sentiment_confidence},
            'priority': email.priority
        }
        
        # Generate response using Gemini
        logger.info(f"Calling Gemini to generate response for {email.priority} priority, {email.sentiment} sentiment email")
        response_result = gemini_client.generate_response(email_data, analysis)
        
        # Save or update response
        response_record = db.query(Response).filter(Response.email_id == email_id).first()
        if response_record:
            response_record.generated_response = response_result['generated_response']
            response_record.final_response = response_result['generated_response']
        else:
            response_record = Response(
                email_id=email_id,
                generated_response=response_result['generated_response'],
                final_response=response_result['generated_response'],
                is_sent=0
            )
            db.add(response_record)
        
        db.commit()
        
        logger.info(f"Gemini response generated successfully for email {email_id}")
        
        return {
            "message": "AI response generated successfully using Gemini",
            "response": response_result['generated_response'],
            "email_priority": email.priority,
            "email_sentiment": email.sentiment,
            "ai_engine": "Gemini Pro"
        }
        
    except Exception as e:
        logger.error(f"Error generating Gemini response: {e}")
        return {"error": str(e)}

@app.post("/api/emails/{email_id}/resolve")
def resolve_email(email_id: int, db: Session = Depends(get_db)):
    """Mark an email as resolved"""
    try:
        logger.info(f"Resolving email ID: {email_id}")
        
        email = db.query(Email).filter(Email.id == email_id).first()
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        email.status = "resolved"
        db.commit()
        
        logger.info(f"Email {email_id} marked as resolved")
        return {"message": "Email marked as resolved", "email_id": email_id}
        
    except Exception as e:
        logger.error(f"Error resolving email {email_id}: {e}")
        return {"error": str(e)}

@app.post("/api/emails/{email_id}/send")
async def send_email_response(email_id: int, request: EmailSendRequest, db: Session = Depends(get_db)):
    """Simulate sending email"""
    try:
        email = db.query(Email).filter(Email.id == email_id).first()
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        response_record = db.query(Response).filter(Response.email_id == email_id).first()
        if response_record:
            response_record.final_response = request.response_text
            response_record.is_sent = 1 if request.send_immediately else 0
        
        if request.send_immediately:
            email.status = "resolved"
            logger.info(f"Email simulated as sent to {email.sender}")
        
        db.commit()
        
        return {
            "message": "Email sent successfully (simulated)" if request.send_immediately else "Draft saved successfully",
            "sent": request.send_immediately
        }
        
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return {"error": str(e)}

@app.post("/api/emails/{email_id}/save-draft")
async def save_draft(email_id: int, request: EmailSendRequest, db: Session = Depends(get_db)):
    """Save draft response without sending"""
    try:
        response_record = db.query(Response).filter(Response.email_id == email_id).first()
        if response_record:
            response_record.final_response = request.response_text
            response_record.generated_response = request.response_text
        else:
            response_record = Response(
                email_id=email_id,
                generated_response=request.response_text,
                final_response=request.response_text,
                is_sent=0
            )
            db.add(response_record)
        
        db.commit()
        return {"message": "Draft saved successfully"}
        
    except Exception as e:
        logger.error(f"Error saving draft: {e}")
        return {"error": str(e)}

@app.get("/api/analytics")
def get_analytics(db: Session = Depends(get_db)):
    """Get email analytics"""
    try:
        logger.info("Calculating analytics")
        
        total_emails = db.query(Email).count()
        resolved_emails = db.query(Email).filter(Email.status == "resolved").count()
        pending_emails = total_emails - resolved_emails
        
        # Count emails with responses generated
        emails_with_responses = db.query(Email).join(Response, Email.id == Response.email_id).count()
        emails_without_responses = total_emails - emails_with_responses
        
        sentiment_data = {}
        try:
            sentiments = db.execute(text("SELECT sentiment, COUNT(*) as count FROM emails GROUP BY sentiment")).fetchall()
            for row in sentiments:
                sentiment_data[row[0]] = row[1]
        except Exception as e:
            logger.error(f"Error getting sentiment data: {e}")
        
        priority_data = {}
        try:
            priorities = db.execute(text("SELECT priority, COUNT(*) as count FROM emails GROUP BY priority")).fetchall()
            for row in priorities:
                priority_data[row[0]] = row[1]
        except Exception as e:
            logger.error(f"Error getting priority data: {e}")
        
        return {
            "total_emails": total_emails,
            "resolved_emails": resolved_emails, 
            "pending_emails": pending_emails,
            "emails_with_responses": emails_with_responses,
            "emails_without_responses": emails_without_responses,
            "sentiment_distribution": sentiment_data,
            "priority_distribution": priority_data,
            "ai_engine": "Gemini Pro"
        }
        
    except Exception as e:
        logger.error(f"Error in get_analytics: {e}")
        return {
            "total_emails": 0,
            "resolved_emails": 0, 
            "pending_emails": 0,
            "emails_with_responses": 0,
            "emails_without_responses": 0,
            "sentiment_distribution": {},
            "priority_distribution": {},
            "ai_engine": "Gemini Pro"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
