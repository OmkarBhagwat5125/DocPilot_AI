import React, { useRef, useState } from 'react'
import { 
  Upload, 
  FileText, 
  Trash2, 
  LogOut, 
  Loader2, 
  CheckCircle,
  FileCode,
  FileSpreadsheet
} from 'lucide-react'
import Logo from './Logo'
import './Sidebar.css'

export default function Sidebar({ 
  documents = [], 
  onUpload, 
  onDelete, 
  onSignOut, 
  isUploading = false,
  userEmail = ''
}) {
  const fileInputRef = useRef(null)
  const [isDragActive, setIsDragActive] = useState(false)
  const [statusMsg, setStatusMsg] = useState('')

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true)
    } else if (e.type === "dragleave") {
      setIsDragActive(false)
    }
  }

  const handleDrop = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0])
    }
  }

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0])
    }
  }

  const processFile = async (file) => {
    setStatusMsg('Uploading...')
    try {
      await onUpload(file)
      setStatusMsg('Success!')
      setTimeout(() => setStatusMsg(''), 3000)
    } catch (err) {
      setStatusMsg(`Error: ${err.message || 'failed'}`)
      setTimeout(() => setStatusMsg(''), 5000)
    }
  }

  const triggerFileInput = () => {
    fileInputRef.current.click()
  }

  const getFileIcon = (filename) => {
    const ext = filename.split('.').pop().toLowerCase()
    if (ext === 'csv') return <FileSpreadsheet className="file-icon csv" size={18} />
    if (ext === 'txt') return <FileText className="file-icon txt" size={18} />
    if (ext === 'docx') return <FileCode className="file-icon docx" size={18} />
    if (ext === 'pdf') return <FileText className="file-icon pdf" size={18} />
    if (ext === 'pptx') return <FileText className="file-icon pptx" size={18} />
    return <FileText className="file-icon default" size={18} />
  }

  const getBorderClass = (filename) => {
    const ext = filename.split('.').pop().toLowerCase()
    if (ext === 'pdf') return 'doc-border-pdf'
    if (ext === 'docx') return 'doc-border-docx'
    if (ext === 'csv') return 'doc-border-csv'
    if (ext === 'txt') return 'doc-border-txt'
    if (ext === 'pptx') return 'doc-border-pptx'
    return 'doc-border-default'
  }

  const storagePercentage = Math.min((documents.length / 10) * 100, 100)

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <Logo size={24} className="logo-icon" />
          <h2 className="sidebar-title gradient-text">DocPilot AI</h2>
          <span className="version-badge">v2.0</span>
        </div>
      </div>

      <div className="upload-section">
        <h3>Upload Documents</h3>
        <div 
          className={`dropzone ${isDragActive ? 'drag-active' : ''} ${isUploading ? 'uploading' : ''}`}
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          onClick={triggerFileInput}
          id="upload-dropzone"
        >
          <input
            id="file-input-element"
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf,.docx,.pptx,.csv,.txt"
            style={{ display: 'none' }}
            disabled={isUploading}
          />
          {isUploading ? (
            <div className="upload-state">
              <Loader2 className="spinner loader" size={28} />
              <p className="primary-text">Processing & Indexing...</p>
            </div>
          ) : (
            <div className="upload-state">
              <Upload className="upload-icon" />
              <p className="primary-text">Drag & drop files or click</p>
              <p className="secondary-text">PDF, DOCX, PPTX, CSV, TXT</p>
            </div>
          )}
        </div>
        {statusMsg && (
          <div className={`upload-status ${statusMsg.startsWith('Error') ? 'error' : 'success'}`}>
            {statusMsg.startsWith('Success') && <CheckCircle size={14} />}
            <span>{statusMsg}</span>
          </div>
        )}
      </div>

      <div className="documents-section">
        <div className="section-title">
          <h3>My Knowledge Base</h3>
          <span className="doc-count">{documents.length}</span>
        </div>
        <div className="storage-bar-container">
          <div 
            className="storage-bar-fill" 
            style={{ width: `${storagePercentage}%` }}
          ></div>
        </div>
        <div className="documents-list">
          {documents.length === 0 ? (
            <div className="empty-docs">
              <p>No documents uploaded yet.</p>
            </div>
          ) : (
            documents.map((doc, idx) => (
              <div key={idx} className={`document-card ${getBorderClass(doc)}`} id={`doc-card-${idx}`}>
                <div className="doc-meta">
                  {getFileIcon(doc)}
                  <span className="doc-name" title={doc}>{doc}</span>
                </div>
                <button
                  id={`delete-doc-btn-${idx}`}
                  className="btn-delete"
                  onClick={() => onDelete(doc)}
                  title="Delete Document"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="sidebar-footer">
        <div className="user-profile">
          <div className="avatar">
            {userEmail ? userEmail.charAt(0).toUpperCase() : 'U'}
          </div>
          <div className="user-info">
            <p className="user-email" title={userEmail}>{userEmail}</p>
          </div>
        </div>
        <button id="signout-button" className="btn-signout" onClick={onSignOut}>
          <LogOut size={16} />
          <span>Sign Out</span>
        </button>
      </div>
    </div>
  )
}
