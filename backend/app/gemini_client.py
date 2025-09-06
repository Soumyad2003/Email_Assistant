import os
import json
import logging
import google.generativeai as genai
from typing import Dict, Any

logger = logging.getLogger(__name__)

class GeminiClient:
    """Gemini client for email analysis and response generation"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        logger.info("✅ Gemini client initialized successfully")

    def analyze_email(self, email_data: Dict) -> Dict:
        """Analyze email for sentiment and priority using Gemini"""
        try:
            prompt = f"""
            Analyze the following customer support email and provide a JSON response with sentiment and priority:

            Subject: {email_data['subject']}
            Body: {email_data['body']}
            From: {email_data['sender']}

            Please respond with valid JSON in this exact format:
            {{
                "sentiment": "Positive|Negative|Neutral",
                "confidence": 0.95,
                "priority": "Urgent|High|Normal|Low",
                "reasoning": "Brief explanation"
            }}

            Priority guidelines:
            - Urgent: System outages, billing errors, account access issues, security concerns
            - High: Feature requests, login problems, urgent inquiries
            - Normal: General questions, feedback, documentation requests
            - Low: Compliments, suggestions, non-critical requests
            """

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up response text to extract JSON
            try:
                cleaned_text = self._clean_response_text(response_text)
                result = json.loads(cleaned_text)
                
                return {
                    'sentiment': {
                        'sentiment': result.get('sentiment', 'Neutral'),
                        'confidence': float(result.get('confidence', 0.5))
                    },
                    'priority': result.get('priority', 'Normal'),
                    'reasoning': result.get('reasoning', 'AI analysis completed')
                }
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse Gemini response as JSON: {response_text}")
                return self._fallback_analysis(response_text, email_data)

        except Exception as e:
            logger.error(f"Error analyzing email with Gemini: {e}")
            return {
                'sentiment': {'sentiment': 'Neutral', 'confidence': 0.5},
                'priority': 'Normal',
                'reasoning': 'Analysis failed, using defaults'
            }

    def generate_response(self, email_data: Dict, analysis: Dict) -> Dict:
        """Generate email response using Gemini"""
        try:
            prompt = f"""
            Generate a professional, helpful email response to this customer support request:

            Original Email:
            Subject: {email_data['subject']}
            From: {email_data['sender']}
            Body: {email_data['body']}

            Email Analysis:
            - Priority: {analysis['priority']}
            - Sentiment: {analysis['sentiment']['sentiment']}

            Guidelines:
            - Be professional, empathetic, and helpful
            - Address the customer's specific concern
            - Provide clear next steps or solutions when possible
            - Use a friendly but professional tone
            - Keep response concise but complete
            - Do not include any email headers (To:, From:, Subject:)

            Generate only the email body content:
            """

            response = self.model.generate_content(prompt)
            generated_text = response.text.strip()

            return {
                'generated_response': generated_text,
                'model': 'gemini-1.5-pro'
            }

        except Exception as e:
            logger.error(f"Error generating response with Gemini: {e}")
            return {
                'generated_response': f"Thank you for contacting us regarding '{email_data['subject']}'. We have received your message and will respond shortly with a solution. We appreciate your patience.",
                'model': 'fallback'
            }

    def _clean_response_text(self, response_text: str) -> str:
        """Clean response text to extract JSON content"""
        # Remove markdown code blocks if present
        if 'json' in response_text.lower():
            # Split by triple backticks and find JSON content
            parts = response_text.split('```')
            for part in parts:
                part = part.strip()
                if part.startswith('{') and part.endswith('}'):
                    return part
                # Remove 'json' prefix if present
                if part.lower().startswith('json'):
                    clean_part = part[4:].strip()
                    if clean_part.startswith('{') and clean_part.endswith('}'):
                        return clean_part
        
        # If no code blocks, try to find JSON in the text
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return response_text[start_idx:end_idx + 1]
        
        return response_text

    def _fallback_analysis(self, response_text: str, email_data: Dict) -> Dict:
        """Fallback analysis when JSON parsing fails"""
        text_lower = response_text.lower()
        
        # Simple keyword-based fallback
        if any(word in text_lower for word in ['positive', 'happy', 'good', 'great']):
            sentiment = 'Positive'
        elif any(word in text_lower for word in ['negative', 'angry', 'frustrated', 'bad']):
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'
            
        if any(word in text_lower for word in ['urgent', 'critical', 'immediate']):
            priority = 'Urgent'
        elif any(word in text_lower for word in ['high', 'important']):
            priority = 'High'
        else:
            priority = 'Normal'

        return {
            'sentiment': {'sentiment': sentiment, 'confidence': 0.7},
            'priority': priority,
            'reasoning': 'Fallback analysis used'
        }
