import React, { useState, useEffect } from 'react'
import { X, Minimize2, FileText, Download, ExternalLink, MessageSquare, BookOpen } from 'lucide-react'
import { supabase } from '../lib/supabase'
import './ViewDocumentPanel.css'

export default function ViewDocumentPanel({ source, onClose, onAskAboutPage, session }) {
  const [signedUrl, setSignedUrl] = useState(null)

  useEffect(() => {
    if (source?.source && session?.user?.id) {
      const fetchUrl = async () => {
        const { data, error } = await supabase.storage
          .from('documents')
          .createSignedUrl(`${session.user.id}/${source.source}`, 3600)
        
        if (data?.signedUrl) {
          setSignedUrl(data.signedUrl)
        }
      }
      fetchUrl()
    }
  }, [source, session])

  if (!source) {
    return (
      <div className="view-doc-panel">
        <div className="view-doc-header"></div>
        <div className="view-doc-empty">
          <FileText className="view-doc-empty-icon" />
          <p>Click any citation to preview its source here.</p>
          <span className="view-doc-shortcut"><kbd>Ctrl</kbd> + <kbd>D</kbd> to toggle</span>
        </div>
      </div>
    )
  }

  // Get file extension for icon
  const getFileExtension = (filename) => {
    return filename?.split('.').pop()?.toLowerCase() || ''
  }

  const ext = getFileExtension(source.source)

  return (
    <div className="view-doc-panel">
      <div className="view-doc-header">
        <div className="view-doc-file-info">
          <div className="view-doc-file-icon">
            <FileText size={18} />
          </div>
          <div>
            <div className="view-doc-filename" title={source.source}>{source.source}</div>
            <div className="view-doc-page-label">Page {source.page_number}</div>
          </div>
        </div>
        <div className="view-doc-header-actions">
          <button className="view-doc-header-btn" onClick={onClose} title="Close panel">
            <X size={18} />
          </button>
        </div>
      </div>

      <div className="view-doc-body">
        {['pdf', 'txt', 'csv'].includes(ext) && signedUrl ? (
          <iframe 
            src={ext === 'pdf' ? `${signedUrl}#page=${source.page_number}` : signedUrl} 
            title={source.source}
            width="100%" 
            height="100%" 
            style={{ border: 'none', borderRadius: 'var(--radius-md)', background: 'white' }}
          />
        ) : (
          <>
            <div className="view-doc-source-label">
              <BookOpen size={12} />
              <span>Source Excerpt</span>
            </div>
            <div className="view-doc-excerpt">
              {source.content || `Content from ${source.source}, page ${source.page_number}`}
            </div>
          </>
        )}
        <div className="view-doc-meta">
          <span className="view-doc-meta-chip">
            <FileText size={11} /> {ext.toUpperCase()}
          </span>
          <span className="view-doc-meta-chip">
            Page {source.page_number}
          </span>
        </div>
      </div>

      <div className="view-doc-footer">
        <button 
          className="view-doc-action-btn" 
          disabled={!signedUrl} 
          onClick={() => {
            const a = document.createElement('a')
            a.href = signedUrl
            a.download = source.source
            a.click()
          }}
          title="Download Document"
        >
          <Download size={14} /> Download
        </button>
        <button 
          className="view-doc-action-btn" 
          disabled={!signedUrl} 
          onClick={() => window.open(signedUrl, '_blank')}
          title="Open in new tab"
        >
          <ExternalLink size={14} /> Open
        </button>
        <button 
          className="view-doc-action-btn primary"
          onClick={() => onAskAboutPage && onAskAboutPage(source)}
          title="Ask about this page"
        >
          <MessageSquare size={14} /> Ask
        </button>
      </div>
    </div>
  )
}
