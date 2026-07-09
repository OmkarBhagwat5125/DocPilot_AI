import React, { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Sparkles, FileText, Check } from 'lucide-react'
import './ChatArea.css'

export default function ChatArea({ 
  messages = [], 
  onSendMessage, 
  isLoading = false, 
  documentCount = 0 
}) {
  const [input, setInput] = useState('')
  const [selectedCitation, setSelectedCitation] = useState(null)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading])

  // Focus input when documentCount changes or component mounts
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSend = (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return
    onSendMessage(input.trim())
    setInput('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      handleSend(e)
    }
  }

  // Format date/timestamp
  const formatTime = (dateObj) => {
    if (!dateObj) return ''
    const d = new Date(dateObj)
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="chat-area">
      <div className="chat-header glass-panel">
        <div className="chat-title-info">
          <h2>Conversation</h2>
          <div className="status-indicator">
            <span className="dot animate-pulse"></span>
            <p>{documentCount > 0 ? `${documentCount} Documents Indexed` : 'Waiting for Documents'}</p>
          </div>
        </div>
      </div>

      <div className="chat-messages-container">
        {messages.length === 0 ? (
          <div className="chat-empty-state">
            <div className="empty-graphic">
              <Bot size={48} className="empty-icon animate-float" />
              <Sparkles size={24} className="sparkle-icon" />
            </div>
            <h2>Welcome to DocPilot AI</h2>
            <p>Upload a document in the sidebar to populate your knowledge base, then start asking questions below.</p>
            <div className="example-queries">
              <div className="query-pill" onClick={() => setInput('Summarize the main points of the uploaded document.')}>
                "Summarize the main points..."
              </div>
              <div className="query-pill" onClick={() => setInput('What is the main objective or vision described?')}>
                "What is the main vision described?"
              </div>
            </div>
          </div>
        ) : (
          <div className="chat-messages">
            {messages.map((msg, index) => (
              <div key={index} className={`message-wrapper ${msg.role}`} id={`chat-msg-${index}`}>
                <div className="avatar-wrapper">
                  {msg.role === 'user' ? (
                    <div className="user-avatar"><User size={16} /></div>
                  ) : (
                    <div className="bot-avatar"><Bot size={16} /></div>
                  )}
                </div>
                <div className="message-bubble glass-panel">
                  <div className="message-content">
                    {msg.content}
                  </div>
                  
                  {/* Citations block */}
                  {msg.role === 'assistant' && msg.sources && msg.sources.length > 0 && (
                    <div className="citations-block">
                      <div className="citations-title">
                        <FileText size={12} />
                        <span>Sources Cited:</span>
                      </div>
                      <div className="citation-pills">
                        {msg.sources.map((src, sIdx) => (
                          <div 
                            key={sIdx} 
                            className={`citation-pill ${selectedCitation === src ? 'active' : ''}`}
                            onClick={() => setSelectedCitation(selectedCitation === src ? null : src)}
                            title={`Document: ${src.source}, Page: ${src.page_number}`}
                          >
                            <span className="cit-name">{src.source}</span>
                            <span className="cit-page">Pg {src.page_number}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <span className="message-time">{formatTime(msg.timestamp)}</span>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="message-wrapper assistant loading">
                <div className="avatar-wrapper">
                  <div className="bot-avatar"><Bot size={16} /></div>
                </div>
                <div className="message-bubble glass-panel loading-bubble">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div className="chat-input-wrapper glass-panel">
        <form onSubmit={handleSend} className="chat-input-form" id="chat-input-form-element">
          <textarea
            id="chat-textarea-input"
            ref={inputRef}
            rows={1}
            className="chat-textarea"
            placeholder={documentCount > 0 ? "Ask anything about your documents..." : "Please upload a document to begin..."}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading || documentCount === 0}
          />
          <button
            id="chat-send-btn"
            type="submit"
            className="btn btn-primary send-btn"
            disabled={!input.trim() || isLoading || documentCount === 0}
            title="Send Message"
          >
            <Send size={16} />
          </button>
        </form>
        <div className="input-hints">
          <span>Enter to send</span>
          <span className="divider">•</span>
          <span>Shift + Enter for newline</span>
        </div>
      </div>
    </div>
  )
}
