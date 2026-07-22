import React, { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Sparkles, FileText, Check, Copy } from 'lucide-react'
import Logo from './Logo'
import './ChatArea.css'

export default function ChatArea({ 
  messages = [], 
  onSendMessage, 
  isLoading = false, 
  documentCount = 0 
}) {
  const [input, setInput] = useState('')
  const [selectedCitation, setSelectedCitation] = useState(null)
  const [copiedIndex, setCopiedIndex] = useState(null)
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

  const handleCopy = (text, index) => {
    navigator.clipboard.writeText(text)
    setCopiedIndex(index)
    setTimeout(() => {
      setCopiedIndex(null)
    }, 2000)
  }

  const renderContent = (text) => {
    if (!text) return null
    
    const lines = text.split('\n')
    return lines.map((line, i) => {
      const parts = line.split(/(\*\*.*?\*\*|`.*?`)/g)
      return (
        <React.Fragment key={i}>
          {parts.map((part, j) => {
            if (part.startsWith('**') && part.endsWith('**')) {
              return <strong key={j}>{part.slice(2, -2)}</strong>
            } else if (part.startsWith('`') && part.endsWith('`')) {
              return <code key={j}>{part.slice(1, -1)}</code>
            }
            return <span key={j}>{part}</span>
          })}
          {i < lines.length - 1 && <br />}
        </React.Fragment>
      )
    })
  }

  // Format date/timestamp
  const formatTime = (dateObj) => {
    if (!dateObj) return ''
    const d = new Date(dateObj)
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="chat-area">
      <div className="chat-header">
        <div className="chat-title-info">
          <h2>Conversation</h2>
          <div className="status-indicator">
            <span className="dot"></span>
            <p>{documentCount > 0 ? `${documentCount} Documents Indexed` : 'Waiting for Documents'}</p>
          </div>
        </div>
      </div>

      <div className="chat-messages-container">
        {messages.length === 0 ? (
          <div className="chat-empty-state">
            <Logo size={56} className="empty-logo animate-float" />
            <h2 className="font-heading">Welcome to DocPilot AI</h2>
            <p className="text-secondary">Upload a document in the sidebar to populate your knowledge base, then start asking questions below.</p>
            
            <div className="feature-cards-grid">
              <div className="feature-card">
                <FileText className="feature-card-icon" />
                <h4>Multi-Format Upload</h4>
                <p>Support for PDFs, Word, text, and more.</p>
              </div>
              <div className="feature-card">
                <Bot className="feature-card-icon" />
                <h4>Contextual AI</h4>
                <p>Get intelligent answers based strictly on your files.</p>
              </div>
              <div className="feature-card">
                <Check className="feature-card-icon" />
                <h4>Verified Citations</h4>
                <p>Every claim backed by exact source page references.</p>
              </div>
            </div>

            <div className="example-queries">
              <div className="query-pill" onClick={() => setInput('Summarize the main points of the uploaded document.')}>
                "Summarize the main points..."
              </div>
              <div className="query-pill" onClick={() => setInput('What is the main objective or vision described?')}>
                "What is the main vision described?"
              </div>
              <div className="query-pill" onClick={() => setInput('List all key findings and recommendations')}>
                "List all key findings and recommendations"
              </div>
              <div className="query-pill" onClick={() => setInput('Compare the different sections discussed')}>
                "Compare the different sections discussed"
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
                <div className="message-bubble">
                  {msg.role === 'assistant' && (
                    <button 
                      className={`copy-btn ${copiedIndex === index ? 'copied' : ''}`}
                      onClick={() => handleCopy(msg.content, index)}
                      title="Copy message"
                    >
                      {copiedIndex === index ? <Check size={14} /> : <Copy size={14} />}
                    </button>
                  )}
                  <div className="message-content">
                    {renderContent(msg.content)}
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
                <div className="message-bubble loading-bubble">
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

      <div className="chat-input-wrapper">
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
            className="send-btn"
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
