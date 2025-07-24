import React, { useState } from 'react';
import './ChatInterface.css';

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  relatedSections?: any[];
  tokensUsed?: number;
}

interface ChatInterfaceProps {
  selectedDocuments: string[];
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ selectedDocuments }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [llmStatus, setLlmStatus] = useState<any>(null);

  // Check LLM availability on component mount
  React.useEffect(() => {
    fetch('/api/llm/status')
      .then(res => res.json())
      .then(status => setLlmStatus(status))
      .catch(err => console.error('Failed to check LLM status:', err));
  }, []);

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/llm/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: inputValue,
          documents: selectedDocuments
        })
      });

      const data = await response.json();

      if (response.ok) {
        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: data.llm_response,
          timestamp: new Date(),
          relatedSections: data.related_sections,
          tokensUsed: data.tokens_used
        };

        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error(data.error || 'Search failed');
      }
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!llmStatus) {
    return <div className="chat-loading">Checking LLM availability...</div>;
  }

  if (!llmStatus.llm_available || !llmStatus.openai_api_key_configured) {
    return (
      <div className="chat-unavailable">
        <h3>🤖 AI Chat Not Available</h3>
        <p>To enable AI-powered search:</p>
        <ol>
          <li>Install required packages: <code>pip install openai tiktoken scikit-learn</code></li>
          <li>Set your OpenAI API key: <code>set OPENAI_API_KEY=your_key_here</code></li>
          <li>Restart the backend server</li>
        </ol>
        <p>The regular search functionality is still available above.</p>
      </div>
    );
  }

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h3>🤖 AI Document Assistant</h3>
        <p>Ask questions about the technical documents in natural language</p>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-welcome">
            <p>👋 Hi! I can help you find information in the technical documents.</p>
            <div className="example-questions">
              <p><strong>Try asking:</strong></p>
              <ul>
                <li>"What are the safety requirements for head clearance?"</li>
                <li>"Explain the procedures for accidental activation prevention"</li>
                <li>"What are the noise level standards?"</li>
                <li>"How should emergency controls be designed?"</li>
              </ul>
            </div>
          </div>
        )}

        {messages.map(message => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="message-content">
              <div className="message-text">{message.content}</div>
              {message.relatedSections && message.relatedSections.length > 0 && (
                <div className="related-sections">
                  <h4>Related Document Sections:</h4>
                  {message.relatedSections.slice(0, 3).map((section, idx) => (
                    <div key={idx} className="related-section">
                      <strong>{section.document}</strong> - {section.section_title} (Page {section.page})
                      {section.similarity_score && (
                        <span className="similarity-score">
                          {Math.round(section.similarity_score * 100)}% match
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              )}
              {message.tokensUsed && (
                <div className="token-usage">
                  Tokens used: {message.tokensUsed}
                </div>
              )}
            </div>
            <div className="message-timestamp">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant loading">
            <div className="message-content">
              <div className="loading-dots">Thinking...</div>
            </div>
          </div>
        )}
      </div>

      <div className="chat-input">
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question about the documents..."
          disabled={isLoading}
          rows={2}
        />
        <button 
          onClick={sendMessage} 
          disabled={isLoading || !inputValue.trim()}
          className="send-button"
        >
          {isLoading ? '...' : 'Send'}
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;
