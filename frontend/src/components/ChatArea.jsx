import React, { useState, useRef, useEffect } from 'react'
import { Send, Bot, Sparkles, FileText, Check, Copy, Paperclip, Zap, Search, List, LayoutGrid, Eye } from 'lucide-react'
import Logo from './Logo'
import './ChatArea.css'

export default function ChatArea({ 
  messages = [], 
  onSendMessage, 
  isLoading = false, 
  documentCount = 0,
  onCitationClick
}) {
  const [input, setInput] = useState('')
  const [copiedIndex, setCopiedIndex] = useState(null)
  const [mode, setMode] = useState('quick')
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading])

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

  const formatTime = (dateObj) => {
    if (!dateObj) return ''
    const d = new Date(dateObj)
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="chat-area">
      <div className="chat-messages-container">
        {messages.length === 0 ? (
          <div className="chat-empty-state">
            <Logo size={48} className="empty-logo" />
            <h1 className="empty-greeting">What would you like to know from your documents?</h1>
            <div className="suggestion-cards">
              <div className="suggestion-card" onClick={() => setInput('Summarize the main points of the uploaded document.')}>
                <FileText size={20} />
                <span>Summarize the main points</span>
              </div>
              <div className="suggestion-card" onClick={() => setInput('What is the main objective or vision described?')}>
                <Sparkles size={20} />
                <span>What is the main vision?</span>
              </div>
              <div className="suggestion-card" onClick={() => setInput('List all key findings and recommendations')}>
                <List size={20} />
                <span>Key findings & recommendations</span>
              </div>
              <div className="suggestion-card" onClick={() => setInput('Compare the different sections discussed')}>
                <LayoutGrid size={20} />
                <span>Compare different sections</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="chat-messages">
            {messages.map((msg, index) => (
              <div key={index} className={`message-wrapper ${msg.role}`} id={`chat-msg-${index}`}>
                <div className="message-bubble">
                  <div className="message-content">
                    {renderContent(msg.content)}
                  </div>
                  
                  {msg.role === 'assistant' && (
                    <div className="message-footer">
                      <div className="citations-block">
                        {msg.sources && msg.sources.length > 0 && msg.sources.map((src, sIdx) => (
                          <div 
                            key={sIdx} 
                            className="citation-chip"
                            onClick={() => onCitationClick && onCitationClick(src)}
                            title={`Document: ${src.source}, Page: ${src.page_number}`}
                          >
                            <span>{src.source} - Pg {src.page_number}</span>
                          </div>
                        ))}
                      </div>
                      <div className="footer-actions">
                        <button 
                          className={`copy-btn ${copiedIndex === index ? 'copied' : ''}`}
                          onClick={() => handleCopy(msg.content, index)}
                          title="Copy message"
                        >
                          {copiedIndex === index ? <Check size={14} /> : <Copy size={14} />}
                        </button>
                        {msg.sources && msg.sources.length > 0 && (
                          <button className="view-doc-btn" onClick={() => onCitationClick && onCitationClick(msg.sources[0])}>
                            <Eye size={12} /> View Doc
                          </button>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="message-wrapper assistant loading">
                <div className="message-bubble loading-bubble">
                  <div className="typing-indicator">
                    <span className="dot"></span>
                    <span className="dot"></span>
                    <span className="dot"></span>
                    <div className="streaming-cursor"></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div className="chat-input-wrapper">
        <form onSubmit={handleSend} className="chat-input-form">
          <button type="button" className="attach-btn" title="Attach file">
            <Paperclip size={18} />
          </button>
          <textarea
            ref={inputRef}
            rows={1}
            className="chat-textarea"
            placeholder={documentCount > 0 ? "Ask anything about your documents..." : "Please upload a document to begin..."}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading || documentCount === 0}
          />
          <div className="input-right">
            <div className="mode-toggle">
              <button type="button" className={`mode-chip ${mode === 'quick' ? 'active' : ''}`} onClick={() => setMode('quick')}>
                <Zap size={12} /> Quick Answer
              </button>
              <button type="button" className={`mode-chip ${mode === 'deep' ? 'active' : ''}`} onClick={() => setMode('deep')}>
                <Search size={12} /> Deep Search
              </button>
            </div>
            <button
              type="submit"
              className="send-btn"
              disabled={!input.trim() || isLoading || documentCount === 0}
              title="Send Message"
            >
              <Send size={16} />
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
