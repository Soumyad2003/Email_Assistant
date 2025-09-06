
# 📧 AI-Powered Email Assistant  

**Intelligent Email Management System powered by Google's Gemini Pro for automated sentiment analysis, priority classification, and response generation**  

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green) ![React](https://img.shields.io/badge/React-Frontend-blue) ![Google-Gemini](https://img.shields.io/badge/AI-Google%20Gemini%20Pro-orange)  

---

## ✨ Overview  
**AI-Powered Email Assistant** is a modern email automation system that uses **Google Gemini Pro** to analyze customer emails, classify sentiment and priority, and generate professional responses. Built with **FastAPI** (Backend), **React + TypeScript** (Frontend), and **Google Gemini AI** for NLP.  

---

## ✅ Key Features  
- 🤖 **AI-Driven Analysis:** Real-time sentiment & priority classification using **Gemini Pro**  
- ⚡ **Smart Prioritization:** Automatic sorting (Urgent → High → Normal → Low)  
- ✨ **On-Demand Response Generation:** Contextual responses in one click  
- 📊 **Live Analytics Dashboard:** Sentiment & priority distribution charts  
- 📁 **CSV Upload:** Bulk email processing  
- 🎯 **Priority Queue System:** Enhanced email filtering and processing  

---

## 🏗️ System Architecture  
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Backend     │    │    AI Engine    │
│   (React)       │◄──►│   (FastAPI)     │◄──►│  (Gemini Pro)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Dashboard     │    │   SQLite DB     │    │   JSON Parser   │
│   Analytics     │    │   Email Store   │    │   Fallback      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🧩 Core Components  
### 1. **Frontend (React + TypeScript)**  
- **UI:** Tailwind CSS  
- **Charts:** Recharts for analytics visualization  
- **State:** React Hooks  
- **API Calls:** Axios  

### 2. **Backend (FastAPI)**  
- **ORM:** SQLAlchemy + SQLite  
- **Async Operations:** FastAPI performance  
- **Auth:** API key management via `.env`  

### 3. **AI Engine (Google Gemini Pro)**  
- Sentiment detection (Positive/Negative/Neutral)  
- Priority classification (Urgent/High/Normal/Low)  
- Context-aware response generation  

### 4. **Data Processing**  
- **CSV Parsing:** Pandas  
- **Validation:** Input sanitization  
- **Queue:** Priority-based processing  

---

## 🔄 Workflow  
### **Phase 1: Bulk Analysis (on email load)**  
```python
for email in email_batch:
    analysis = gemini_client.analyze_email(email)
    email.sentiment = analysis['sentiment']
    email.priority = analysis['priority']
    database.save(email)
```

### **Phase 2: Response Generation (on demand)**  
```python
def generate_response(email_id):
    email = database.get_email(email_id)
    response = gemini_client.generate_response(email, email.analysis)
    database.save_response(email_id, response)
```

---

## 📊 Data Flow  
```
CSV Upload → Parser → AI Analysis → Database → Frontend Analytics → On-demand Response
```

---

## 🔌 API Endpoints  
```
POST /api/load-emails               # Load sample emails with AI analysis
POST /api/upload-csv                # Upload custom CSV for processing
GET  /api/emails                    # Fetch prioritized email list
GET  /api/analytics                 # Real-time analytics data
POST /api/emails/{id}/generate-response  # Generate response
POST /api/emails/{id}/resolve       # Mark email as resolved
POST /api/clear-database            # Reset system state
```

---

## 🛠️ Tech Stack  
### **Backend:** FastAPI, SQLAlchemy, Pandas  
### **AI:** Google Gemini Pro  
### **Frontend:** React 18, TypeScript, Tailwind CSS, Recharts  
### **Build Tool:** Vite  

---

## 🚀 Quick Start  
### **Prerequisites**  
- Python **3.8+**  
- Node.js **16+**  
- Google Gemini API Key  

### **Setup**  
```bash
# Clone repository
git clone <repository-url>
cd ai-email-assistant

# Backend Setup
cd backend
python -m venv email_assistant
source email_assistant/bin/activate  # Windows: email_assistant\Scripts\activate
pip install -r requirements.txt

# Configure Environment
echo "GEMINI_API_KEY=your_gemini_api_key" > .env
echo "DATABASE_URL=sqlite:///./email_assistant.db" >> .env

# Frontend Setup
cd ../frontend
npm install

# Run Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run Frontend
cd frontend
npm run dev
```

### **Access**  
- **Frontend:** [http://localhost:3000](http://localhost:3000)  
- **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)  

---

## 📋 Usage  
1. **Load Emails** – Click *Load Sample* or upload CSV  
2. **Review Analysis** – Sentiment & priority classification  
3. **Generate Response** – On-demand AI responses  
4. **Edit & Send** – Customize before sending  
5. **Resolve** – Mark emails as resolved  

---

## 🧠 AI Engine Features  
- Sentiment detection with confidence score  
- Priority classification based on keywords & tone  
- Professional response generation  
- Keyword-based fallback when AI unavailable  

---

## 🔒 Security  
- **API Keys:** Stored in `.env`  
- **CORS:** Restricted origins  
- **Data Privacy:** No training on customer data  

---

## 🚧 Limitations & Roadmap  
**Current Limitations:**  
- Internet required for AI  
- English-only support  
- Single-user design  

**Future Enhancements:**  
- ✅ Multi-language support  
- ✅ Direct email integration (IMAP/Exchange)  
- ✅ Real-time notifications  
- ✅ Role-based access  

---

## 🤝 Contributing  
- Fork → Create Branch → Commit → PR  
- Follow **PEP 8** (Python) & **Prettier** (TypeScript)  
- Use **Conventional Commits**  

---

## 📄 License  
MIT License – See [LICENSE](LICENSE) for details  

---

### 🙏 Acknowledgments  
- **Google Gemini** for AI  
- **FastAPI** & **React** communities  
