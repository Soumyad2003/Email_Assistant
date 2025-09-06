import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class GeminiResponseGenerator:
    """Advanced response generator using Google Gemini Pro with RAG and context awareness"""
    
    def __init__(self):
        self.setup_gemini()
        
        # Response templates for different scenarios
        self.response_templates = {
            "empathetic_opening": {
                "Negative": [
                    "I sincerely apologize for the frustration you've experienced.",
                    "I understand how concerning this situation must be for you.",
                    "Thank you for bringing this to our attention, and I'm sorry for the inconvenience."
                ],
                "Positive": [
                    "Thank you for your positive feedback and for reaching out!",
                    "We're delighted to hear from you and appreciate your patience.",
                    "Thank you for contacting us - we're here to help!"
                ],
                "Neutral": [
                    "Thank you for contacting our support team.",
                    "We've received your inquiry and are here to assist you.",
                    "Thank you for reaching out to us."
                ]
            },
            "priority_acknowledgment": {
                "Urgent": "This has been marked as high priority and our team will address it immediately.",
                "High": "We understand the importance of this matter and will prioritize your request.",
                "Normal": "We'll ensure your request receives proper attention and care.",
                "Low": "We appreciate you taking the time to contact us."
            },
            "professional_closing": {
                "enterprise": "If you need any additional assistance, please don't hesitate to reach out to your dedicated account manager or our support team.\n\nBest regards,\nEnterprise Support Team",
                "startup": "We're here to support your growth! If you have any other questions, feel free to reach out.\n\nBest regards,\nCustomer Success Team", 
                "standard": "If you have any additional questions, please don't hesitate to contact us.\n\nBest regards,\nCustomer Support Team",
                "education": "We're committed to supporting educational institutions. Please let us know if you need any additional assistance.\n\nBest regards,\nEducation Support Team"
            }
        }
        
        print("🤖 Gemini Response Generator initialized")
        print(f"   - Gemini Pro: {'✅' if hasattr(self, 'gemini_model') else '❌'}")
        print(f"   - Response Templates: {len(self.response_templates)} categories")

    def setup_gemini(self):
        """Initialize Google Gemini Pro"""
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                print("✅ Gemini Pro configured for response generation")
            else:
                print("⚠️ Gemini API key not found")
        except Exception as e:
            print(f"❌ Gemini setup error: {e}")

    def generate_response(self, email_data: Dict, analysis: Dict) -> Dict:
        """Generate comprehensive response using Gemini Pro with context awareness"""
        
        if hasattr(self, 'gemini_model'):
            return self._generate_gemini_response(email_data, analysis)
        else:
            return self._generate_template_response(email_data, analysis)

    def _generate_gemini_response(self, email_data: Dict, analysis: Dict) -> Dict:
        """Generate response using Gemini Pro with RAG and context"""
        try:
            # Extract key information
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            sender = email_data.get('sender', '')
            
            sentiment = analysis['sentiment']['sentiment']  
            priority = analysis['priority']
            knowledge_match = analysis['knowledge_match']
            extracted_info = analysis['extracted_info']
            
            # Build context-rich prompt
            prompt = self._build_response_prompt(
                email_data, analysis, sentiment, priority, knowledge_match, extracted_info
            )
            
            # Generate response with Gemini
            response = self.gemini_model.generate_content(prompt)
            generated_text = response.text.strip()
            
            # Post-process and enhance response
            final_response = self._enhance_response(
                generated_text, sentiment, priority, extracted_info
            )
            
            return {
                'generated_response': final_response,
                'method': 'gemini_pro',
                'context_used': {
                    'sentiment': sentiment,
                    'priority': priority,
                    'knowledge_category': knowledge_match['category'],
                    'customer_tier': extracted_info.get('customer_tier', 'standard'),
                    'emotion': extracted_info.get('emotion_indicators', {}).get('dominant_emotion', 'neutral')
                },
                'confidence': 0.9,
                'generation_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Gemini response generation error: {e}")
            return self._generate_template_response(email_data, analysis)

    def _build_response_prompt(self, email_data: Dict, analysis: Dict, sentiment: str, 
                              priority: str, knowledge_match: Dict, extracted_info: Dict) -> str:
        """Build comprehensive prompt for Gemini Pro"""
        
        # Get relevant knowledge
        knowledge_info = knowledge_match.get('info', {})
        solution = knowledge_info.get('solution', '')
        
        # Customer context
        customer_tier = extracted_info.get('customer_tier', 'standard')
        dominant_emotion = extracted_info.get('emotion_indicators', {}).get('dominant_emotion', 'neutral')
        request_type = extracted_info.get('request_type', 'general_support')
        
        prompt = f"""You are a professional customer support representative for a technology company. Generate a helpful, empathetic, and professional response to this customer email.

CUSTOMER EMAIL:
From: {email_data.get('sender', '')}
Subject: {email_data.get('subject', '')}
Body: {email_data.get('body', '')}

CONTEXT ANALYSIS:
- Customer Sentiment: {sentiment}
- Priority Level: {priority}
- Customer Tier: {customer_tier}
- Dominant Emotion: {dominant_emotion}  
- Request Type: {request_type}
- Knowledge Base Category: {knowledge_match.get('category', 'general')}

RELEVANT SOLUTION INFORMATION:
{solution}

RESPONSE REQUIREMENTS:
1. Professional and empathetic tone
2. Address the customer's specific concerns
3. {"Acknowledge their frustration empathetically" if sentiment == "Negative" else "Match their positive energy" if sentiment == "Positive" else "Maintain friendly professionalism"}
4. {"Emphasize urgency and immediate action" if priority == "Urgent" else "Show appropriate priority level"}
5. Include specific next steps or solutions
6. {"Use enterprise-appropriate language" if customer_tier == "enterprise" else "Use friendly, accessible language"}
7. Keep response concise but complete (150-250 words)
8. End with appropriate call-to-action

Generate a professional customer support response:"""

        return prompt

    def _enhance_response(self, generated_text: str, sentiment: str, priority: str, 
                         extracted_info: Dict) -> str:
        """Enhance Gemini response with templates and personalization"""
        
        # Get customer tier for appropriate closing
        customer_tier = extracted_info.get('customer_tier', 'standard')
        
        # Add empathetic opening if very negative sentiment
        if sentiment == "Negative" and extracted_info.get('emotion_indicators', {}).get('intensity', 0) > 5:
            empathetic_opening = "I want to personally apologize for this experience. "
            if not generated_text.lower().startswith(('i ', 'we ', 'dear')):
                generated_text = empathetic_opening + generated_text
        
        # Add priority acknowledgment if not already included
        if priority == "Urgent" and "priority" not in generated_text.lower():
            priority_note = f"\n\n{self.response_templates['priority_acknowledgment'][priority]}"
            # Insert before closing
            parts = generated_text.rsplit('\n\n', 1)
            if len(parts) == 2:
                generated_text = parts[0] + priority_note + '\n\n' + parts[1]
            else:
                generated_text += priority_note
        
        # Ensure appropriate closing
        if not any(closing in generated_text.lower() for closing in ['best regards', 'sincerely', 'thank you']):
            generated_text += '\n\n' + self.response_templates['professional_closing'][customer_tier]
        
        return generated_text

    def _generate_template_response(self, email_data: Dict, analysis: Dict) -> Dict:
        """Fallback template-based response generation"""
        
        sentiment = analysis['sentiment']['sentiment']
        priority = analysis['priority']  
        knowledge_match = analysis['knowledge_match']
        extracted_info = analysis['extracted_info']
        
        # Build response using templates
        customer_tier = extracted_info.get('customer_tier', 'standard')
        
        # Opening
        opening_options = self.response_templates['empathetic_opening'][sentiment]
        opening = opening_options[0]  # Use first option for consistency
        
        # Solution from knowledge base
        solution = knowledge_match.get('info', {}).get('solution', 
                                                      "Our support team will review your inquiry and respond with a detailed solution within 24 hours.")
        
        # Priority acknowledgment
        priority_ack = self.response_templates['priority_acknowledgment'][priority]
        
        # Closing
        closing = self.response_templates['professional_closing'][customer_tier]
        
        # Combine response
        response_text = f"Dear Valued Customer,\n\n{opening}\n\n{solution}\n\n{priority_ack}\n\n{closing}"
        
        return {
            'generated_response': response_text,
            'method': 'template_fallback',
            'context_used': {
                'sentiment': sentiment,
                'priority': priority,
                'customer_tier': customer_tier,
                'knowledge_category': knowledge_match['category']
            },
            'confidence': 0.7,
            'generation_timestamp': datetime.now().isoformat()
        }

    def generate_response_batch(self, emails_with_analysis: List[Dict]) -> List[Dict]:
        """Generate responses for multiple emails efficiently"""
        
        responses = []
        
        print(f"🤖 Generating responses for {len(emails_with_analysis)} emails...")
        
        for i, item in enumerate(emails_with_analysis, 1):
            email_data = item['email']
            analysis = item['analysis'] 
            
            print(f"   Processing email {i}/{len(emails_with_analysis)}...")
            
            # Generate response
            response_result = self.generate_response(email_data, analysis)
            
            # Add to results
            responses.append({
                'email': email_data,
                'analysis': analysis,
                'response': response_result
            })
        
        print(f"✅ Generated {len(responses)} responses")
        return responses

    def get_response_quality_metrics(self, response_data: Dict) -> Dict:
        """Calculate quality metrics for generated response"""
        
        response_text = response_data.get('generated_response', '')
        context = response_data.get('context_used', {})
        
        metrics = {
            'word_count': len(response_text.split()),
            'professional_score': self._calculate_professional_score(response_text),
            'empathy_score': self._calculate_empathy_score(response_text, context.get('sentiment', 'Neutral')),
            'completeness_score': self._calculate_completeness_score(response_text),
            'context_relevance': self._calculate_context_relevance(response_text, context),
            'overall_quality': 0.0
        }
        
        # Calculate overall quality score
        metrics['overall_quality'] = round(
            (metrics['professional_score'] * 0.3 + 
             metrics['empathy_score'] * 0.25 +
             metrics['completeness_score'] * 0.25 +
             metrics['context_relevance'] * 0.2), 2
        )
        
        return metrics

    def _calculate_professional_score(self, text: str) -> float:
        """Calculate professionalism score (0-1)"""
        professional_indicators = [
            'dear' in text.lower(),
            'thank you' in text.lower(),
            'sincerely' in text.lower() or 'regards' in text.lower(),
            'please' in text.lower(),
            not any(casual in text.lower() for casual in ['hey', 'hi there', 'yo'])
        ]
        return sum(professional_indicators) / len(professional_indicators)

    def _calculate_empathy_score(self, text: str, sentiment: str) -> float:
        """Calculate empathy score based on sentiment appropriateness"""
        text_lower = text.lower()
        
        if sentiment == "Negative":
            empathy_indicators = [
                'apologize' in text_lower or 'sorry' in text_lower,
                'understand' in text_lower,
                'frustration' in text_lower or 'inconvenience' in text_lower,
                'resolve' in text_lower or 'fix' in text_lower
            ]
        elif sentiment == "Positive":
            empathy_indicators = [
                'thank' in text_lower,
                'appreciate' in text_lower,
                'pleased' in text_lower or 'happy' in text_lower,
                'continue' in text_lower or 'support' in text_lower
            ]
        else:
            empathy_indicators = [
                'help' in text_lower,
                'assist' in text_lower,
                'support' in text_lower
            ]
        
        return sum(empathy_indicators) / len(empathy_indicators)

    def _calculate_completeness_score(self, text: str) -> float:
        """Calculate response completeness (0-1)"""
        completeness_indicators = [
            len(text.split()) >= 50,  # Adequate length
            '?' not in text or text.count('?') <= 2,  # Not too many questions back
            'next steps' in text.lower() or 'will' in text.lower(),  # Action items
            'contact' in text.lower() or 'reach out' in text.lower()  # Follow-up option
        ]
        return sum(completeness_indicators) / len(completeness_indicators)

    def _calculate_context_relevance(self, text: str, context: Dict) -> float:
        """Calculate how well response matches context (0-1)"""
        text_lower = text.lower()
        relevance_score = 0.5  # Base score
        
        # Priority appropriateness
        priority = context.get('priority', 'Normal')
        if priority == "Urgent" and ('immediate' in text_lower or 'priority' in text_lower):
            relevance_score += 0.2
        elif priority == "Normal" and 'urgent' not in text_lower:
            relevance_score += 0.1
        
        # Customer tier appropriateness
        customer_tier = context.get('customer_tier', 'standard')
        if customer_tier == "enterprise" and ('account manager' in text_lower or 'enterprise' in text_lower):
            relevance_score += 0.2
        elif customer_tier == "startup" and 'growth' in text_lower:
            relevance_score += 0.1
        
        return min(1.0, relevance_score)
