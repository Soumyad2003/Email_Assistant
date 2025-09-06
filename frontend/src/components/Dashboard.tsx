import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Mail, RefreshCw, Send, Save, Zap, CheckCircle, Upload, Trash2, FileText, Brain, MessageSquare } from 'lucide-react';

interface Email {
  id: number;
  sender: string;
  subject: string;
  body: string;
  sent_date: string;
  sentiment: string;
  sentiment_confidence: number;
  priority: string;
  status: string;
  has_response: boolean;
}

interface Analytics {
  total_emails: number;
  resolved_emails: number;
  pending_emails: number;
  emails_with_responses: number;
  emails_without_responses: number;
  sentiment_distribution: { [key: string]: number };
  priority_distribution: { [key: string]: number };
  ai_engine?: string;
}

const Dashboard: React.FC = () => {
  const [emails, setEmails] = useState<Email[]>([]);
  const [analytics, setAnalytics] = useState<Analytics>({
    total_emails: 0,
    resolved_emails: 0,
    pending_emails: 0,
    emails_with_responses: 0,
    emails_without_responses: 0,
    sentiment_distribution: {},
    priority_distribution: {}
  });
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [responseText, setResponseText] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [generatingResponse, setGeneratingResponse] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Replace the API_BASE constant with:
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

  useEffect(() => {
    loadEmails();
    loadAnalytics();
    const interval = setInterval(() => {
      loadEmails();
      loadAnalytics();
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadEmails = async () => {
    try {
      const response = await axios.get(`${API_BASE}/emails`);
      setEmails(response.data);
    } catch (error) {
      console.error('Error loading emails:', error);
    }
  };

  const loadAnalytics = async () => {
    try {
      const response = await axios.get(`${API_BASE}/analytics`);
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error loading analytics:', error);
    }
  };

  const loadSampleEmails = async () => {
    try {
      setLoading(true);
      const response = await axios.post(`${API_BASE}/load-emails`);
      await loadEmails();
      await loadAnalytics();
      
      alert(`✅ ${response.data.message}\n\n🤖 AI Engine: ${response.data.ai_engine || 'Gemini Pro'}\nEmails analyzed for sentiment & priority!`);
    } catch (error) {
      alert('Error loading emails');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    setSelectedFile(file || null);
  };

  const uploadCSV = async () => {
    if (!selectedFile) {
      alert('Please select a CSV file first');
      return;
    }

    try {
      setLoading(true);
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await axios.post(`${API_BASE}/upload-csv`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      alert(`✅ ${response.data.message}\n\n🤖 AI Engine: ${response.data.ai_engine || 'Gemini Pro'}`);
      
      setSelectedFile(null);
      const fileInput = document.getElementById('csv-file-input') as HTMLInputElement;
      if (fileInput) fileInput.value = '';

      await loadEmails();
      await loadAnalytics();
    } catch (error: any) {
      alert(`Upload failed: ${error.response?.data?.error || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const clearDatabase = async () => {
    const confirmed = window.confirm(
      '⚠️ WARNING: This will permanently delete ALL emails and responses.\n\nAre you sure?'
    );
    
    if (!confirmed) return;

    try {
      setLoading(true);
      const response = await axios.post(`${API_BASE}/clear-database`);
      alert(response.data.message);
      
      setSelectedEmail(null);
      setResponseText('');
      
      await loadEmails();
      await loadAnalytics();
    } catch (error: any) {
      alert(`Failed to clear database: ${error.response?.data?.error || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const selectEmail = async (email: Email) => {
    setSelectedEmail(email);
    try {
      const response = await axios.get(`${API_BASE}/emails/${email.id}/response`);
      setResponseText(response.data.generated_response || '');
    } catch (error) {
      setResponseText('');
    }
  };

  const resolveEmail = async (emailId: number, event: React.MouseEvent) => {
    event.stopPropagation();
    try {
      await axios.post(`${API_BASE}/emails/${emailId}/resolve`);
      await loadEmails();
      await loadAnalytics();
      alert('Email marked as resolved!');
    } catch (error) {
      alert('Failed to mark email as resolved');
    }
  };

  const generateResponseForEmail = async () => {
    if (!selectedEmail) return;
    
    try {
      setGeneratingResponse(true);
      console.log('🤖 Generating Gemini response for email ID:', selectedEmail.id);
      
      const response = await axios.post(`${API_BASE}/emails/${selectedEmail.id}/generate-response`);
      console.log('✅ Gemini response generated:', response.data);
      
      // Update response text with Gemini's output
      setResponseText(response.data.response || '');
      
      // Update selected email
      setSelectedEmail(prev => prev ? { ...prev, has_response: true } : null);
      
      // Refresh data
      await loadEmails();
      await loadAnalytics();
      
      alert(`🤖 Gemini AI Response Generated!\n\nEmail: ${response.data.email_priority} priority, ${response.data.email_sentiment} sentiment\nEngine: ${response.data.ai_engine}`);
      
    } catch (error: any) {
      console.error('❌ Error generating Gemini response:', error);
      alert('Error generating AI response: ' + (error.response?.data?.error || error.message));
    } finally {
      setGeneratingResponse(false);
    }
  };

  const sendResponse = async () => {
    if (!selectedEmail) return;
    try {
      await axios.post(`${API_BASE}/emails/${selectedEmail.id}/send`, {
        email_id: selectedEmail.id,
        response_text: responseText,
        send_immediately: true
      });
      await loadEmails();
      await loadAnalytics();
      alert('Response sent successfully!');
    } catch (error) {
      alert('Error sending response');
    }
  };

  const saveDraft = async () => {
    if (!selectedEmail) return;
    try {
      await axios.post(`${API_BASE}/emails/${selectedEmail.id}/save-draft`, {
        email_id: selectedEmail.id,
        response_text: responseText,
        send_immediately: false
      });
      alert('Draft saved successfully!');
    } catch (error) {
      alert('Error saving draft');
    }
  };

  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case 'Urgent': return 'bg-red-500';
      case 'High': return 'bg-orange-500';
      case 'Normal': return 'bg-blue-500';
      case 'Low': return 'bg-gray-500';
      default: return 'bg-gray-400';
    }
  };

  const getSentimentColor = (sentiment: string): string => {
    switch (sentiment) {
      case 'Positive': return 'bg-green-500';
      case 'Negative': return 'bg-red-500';
      case 'Neutral': return 'bg-gray-500';
      default: return 'bg-gray-400';
    }
  };

  const sentimentData = Object.entries(analytics.sentiment_distribution).map(([key, value]) => ({
    name: key,
    value: value
  }));

  const priorityData = Object.entries(analytics.priority_distribution).map(([key, value]) => ({
    name: key,
    count: value
  }));

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <Mail className="h-8 w-8 text-blue-600 mr-3" />
              <h1 className="text-3xl font-bold text-gray-900">AI Email Assistant</h1>
              <span className="ml-4 text-sm text-gray-500 bg-gradient-to-r from-purple-100 to-blue-100 px-3 py-1 rounded-full">
                🤖 Powered by Gemini Pro
              </span>
            </div>
            <div className="flex items-center space-x-3">
              {/* CSV Upload Section */}
              <div className="flex items-center space-x-2">
                <input
                  id="csv-file-input"
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <label
                  htmlFor="csv-file-input"
                  className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg cursor-pointer flex items-center gap-2"
                >
                  <FileText className="h-4 w-4" />
                  Choose CSV
                </label>
                {selectedFile && (
                  <span className="text-sm text-gray-600 max-w-32 truncate" title={selectedFile.name}>
                    {selectedFile.name}
                  </span>
                )}
                <button
                  onClick={uploadCSV}
                  disabled={!selectedFile || loading}
                  className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 disabled:opacity-50"
                >
                  <Upload className="h-4 w-4" />
                  Upload CSV
                </button>
              </div>

              <button
                onClick={loadSampleEmails}
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 disabled:opacity-50"
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                Load Sample
              </button>

              <button
                onClick={clearDatabase}
                disabled={loading}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 disabled:opacity-50"
              >
                <Trash2 className="h-4 w-4" />
                Clear All
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Analytics Cards */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500">Total Emails</h3>
            <p className="text-3xl font-bold text-gray-900">{analytics.total_emails}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500">Have Responses</h3>
            <p className="text-3xl font-bold text-purple-600">{analytics.emails_with_responses}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500">Need Responses</h3>
            <p className="text-3xl font-bold text-yellow-600">{analytics.emails_without_responses}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500">Resolved</h3>
            <p className="text-3xl font-bold text-green-600">{analytics.resolved_emails}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500">Pending</h3>
            <p className="text-3xl font-bold text-orange-600">{analytics.pending_emails}</p>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Sentiment Distribution</h3>
            {sentimentData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={sentimentData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${percent ? (percent * 100).toFixed(0) : 0}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {sentimentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={
                        entry.name === 'Positive' ? '#22c55e' : 
                        entry.name === 'Negative' ? '#ef4444' : '#6b7280'
                      } />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-64 text-gray-500">
                <div className="text-center">
                  <Brain className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                  <p>Sentiment data available after loading emails</p>
                </div>
              </div>
            )}
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Priority Distribution</h3>
            {priorityData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={priorityData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-64 text-gray-500">
                <div className="text-center">
                  <Brain className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                  <p>Priority data available after loading emails</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Email Management */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Email List */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b">
              <h3 className="text-lg font-medium text-gray-900">
                Support Emails
                <span className="text-sm text-gray-500 ml-2">
                  (Analyzed: {analytics.total_emails}, Responses: {analytics.emails_with_responses})
                </span>
              </h3>
            </div>
            <div className="max-h-96 overflow-y-auto">
              {emails.length === 0 ? (
                <div className="p-6 text-center text-gray-500">
                  <Mail className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No emails found.</p>
                  <p className="text-sm">Load sample emails or upload a CSV to get started.</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {emails.map((email, index) => (
                    <div
                      key={email.id}
                      className={`p-4 cursor-pointer hover:bg-gray-50 ${
                        selectedEmail?.id === email.id ? 'bg-blue-50' : ''
                      } ${email.status === 'resolved' ? 'opacity-75 bg-green-50' : ''} ${
                        !email.has_response ? 'border-l-4 border-purple-400' : ''
                      }`}
                      onClick={() => selectEmail(email)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium text-white ${getPriorityColor(email.priority)}`}>
                              {email.priority}
                            </span>
                            <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium text-white ${getSentimentColor(email.sentiment)}`}>
                              {email.sentiment}
                            </span>
                            {!email.has_response && (
                              <span className="px-2.5 py-0.5 rounded-full text-xs font-medium text-purple-800 bg-purple-100 flex items-center gap-1">
                                <Brain className="h-3 w-3" />
                                Need Response
                              </span>
                            )}
                            {email.status === 'resolved' && (
                              <span className="px-2.5 py-0.5 rounded-full text-xs font-medium text-white bg-green-600 flex items-center gap-1">
                                <CheckCircle className="h-3 w-3" />
                                Resolved
                              </span>
                            )}
                            {email.priority === 'Urgent' && index === 0 && (
                              <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-md">
                                🔥 Top Priority
                              </span>
                            )}
                          </div>
                          <p className="text-sm font-medium text-gray-900 truncate">{email.subject}</p>
                          <p className="text-sm text-gray-600 truncate">From: {email.sender}</p>
                          <p className="text-sm text-gray-500 mt-1">{email.body.substring(0, 100)}...</p>
                        </div>
                        <div className="flex-shrink-0 ml-4">
                          {email.status !== 'resolved' && (
                            <button
                              onClick={(e) => resolveEmail(email.id, e)}
                              className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm flex items-center gap-1"
                            >
                              <CheckCircle className="h-3 w-3" />
                              Submit
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Email Detail */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b">
              <h3 className="text-lg font-medium text-gray-900">Email Details & Response</h3>
            </div>
            <div className="p-6">
              {selectedEmail ? (
                <div className="space-y-6">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Original Email</h4>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="mb-2">
                        <span className="font-medium">Subject: </span>
                        <span>{selectedEmail.subject}</span>
                      </div>
                      <div className="mb-3">
                        <span className="font-medium">From: </span>
                        <span>{selectedEmail.sender}</span>
                      </div>
                      <div className="mb-3 flex gap-4">
                        <div>
                          <span className="font-medium">Priority: </span>
                          <span className={`px-2 py-1 rounded text-xs text-white ${getPriorityColor(selectedEmail.priority)}`}>
                            {selectedEmail.priority}
                          </span>
                        </div>
                        <div>
                          <span className="font-medium">Sentiment: </span>
                          <span className={`px-2 py-1 rounded text-xs text-white ${getSentimentColor(selectedEmail.sentiment)}`}>
                            {selectedEmail.sentiment} ({(selectedEmail.sentiment_confidence * 100).toFixed(0)}%)
                          </span>
                        </div>
                        <div>
                          <span className="font-medium">Status: </span>
                          <span className={`font-medium ${selectedEmail.status === 'resolved' ? 'text-green-600' : 'text-orange-600'}`}>
                            {selectedEmail.status === 'resolved' ? 'Resolved' : 'Pending'}
                          </span>
                        </div>
                      </div>
                      <div className="whitespace-pre-wrap">{selectedEmail.body}</div>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-sm font-medium text-gray-900">AI Generated Response</h4>
                      {!selectedEmail.has_response && (
                        <button 
                          onClick={generateResponseForEmail}
                          disabled={generatingResponse}
                          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md flex items-center gap-2 disabled:opacity-50"
                        >
                          <Brain className={`h-4 w-4 ${generatingResponse ? 'animate-pulse' : ''}`} />
                          {generatingResponse ? 'Generating...' : 'Generate Response'}
                        </button>
                      )}
                    </div>
                    <textarea
                      value={responseText}
                      onChange={(e) => setResponseText(e.target.value)}
                      rows={8}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
                      placeholder={selectedEmail.has_response ? "AI response ready for review and editing..." : "Click 'Generate Response' to create an AI-powered response using Gemini"}
                    />
                    <div className="flex gap-3 mt-4">
                      <button 
                        onClick={sendResponse}
                        disabled={!responseText.trim()}
                        className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md flex items-center gap-2 disabled:opacity-50"
                      >
                        <Send className="h-4 w-4" />
                        Send Response
                      </button>
                      <button 
                        onClick={saveDraft}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md flex items-center gap-2"
                      >
                        <Save className="h-4 w-4" />
                        Save Draft
                      </button>
                      {selectedEmail.has_response && (
                        <button 
                          onClick={generateResponseForEmail}
                          disabled={generatingResponse}
                          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md flex items-center gap-2 disabled:opacity-50"
                        >
                          <Zap className="h-4 w-4" />
                          Regenerate
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center h-64 text-gray-500">
                  <div className="text-center">
                    <Mail className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p>Select an email to view details</p>
                    <p className="text-sm">Emails analyzed by Gemini • Responses generated on-demand</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
