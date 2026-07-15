import React, { useState, useEffect } from 'react'
import { supabase } from './lib/supabase'
import AuthScreen from './components/AuthScreen'
import Sidebar from './components/Sidebar'
import ChatArea from './components/ChatArea'
import * as api from './lib/api'
import './App.css'

export default function App() {
  const [session, setSession] = useState(null)
  const [documents, setDocuments] = useState([])
  const [messages, setMessages] = useState([])
  
  // Loading states
  const [isUploading, setIsUploading] = useState(false)
  const [isQuerying, setIsQuerying] = useState(false)
  const [isInitializing, setIsInitializing] = useState(true)

  // Listen to Supabase Auth State Changes
  useEffect(() => {
    console.log('App: Setting up auth listener')
    supabase.auth.getSession().then(({ data: { session } }) => {
      console.log('App: Session retrieved:', session)
      setSession(session)
      setIsInitializing(false)
    }).catch(err => {
      console.error('App: Error getting session:', err)
      setIsInitializing(false)
    })

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      console.log('App: Auth state changed:', session)
      setSession(session)
    })

    return () => subscription.unsubscribe()
  }, [])

  // Load documents when session is established
  useEffect(() => {
    if (session) {
      loadDocuments()
    } else {
      setDocuments([])
      setMessages([])
    }
  }, [session])

  const loadDocuments = async () => {
    if (!session) return
    try {
      const docs = await api.getDocuments(session.access_token)
      setDocuments(docs)
    } catch (err) {
      console.error("Failed to load documents list:", err)
    }
  }

  const handleUpload = async (file) => {
    if (!session) return
    setIsUploading(true)
    try {
      await api.uploadDocument(session.access_token, file)
      await loadDocuments()
    } catch (err) {
      throw err
    } finally {
      setIsUploading(false)
    }
  }

  const handleDelete = async (filename) => {
    if (!session) return
    const confirmDelete = window.confirm(`Are you sure you want to delete ${filename}? This will remove it from your knowledge base.`)
    if (!confirmDelete) return
    
    try {
      await api.deleteDocument(session.access_token, filename)
      await loadDocuments()
      
      // Filter out messages that contain sources citing this document (optional, but keep it clean)
      setDocuments(prev => prev.filter(d => d !== filename))
    } catch (err) {
      alert(`Delete failed: ${err.message || err}`)
    }
  }

  const handleSendMessage = async (text) => {
    if (!session) return
    
    const userMsg = {
      role: 'user',
      content: text,
      timestamp: new Date()
    }
    
    setMessages(prev => [...prev, userMsg])
    setIsQuerying(true)
    
    try {
      const res = await api.queryDocuments(session.access_token, text)
      const assistantMsg = {
        role: 'assistant',
        content: res.answer,
        sources: res.sources || [],
        timestamp: new Date()
      }
      setMessages(prev => [...prev, assistantMsg])
    } catch (err) {
      const errorMsg = {
        role: 'assistant',
        content: `Error generating response: ${err.message || 'Unknown network error.'}`,
        sources: [],
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMsg])
    } finally {
      setIsQuerying(false)
    }
  }

  const handleSignOut = async () => {
    const confirmOut = window.confirm('Are you sure you want to sign out?')
    if (!confirmOut) return
    await supabase.auth.signOut()
    setSession(null)
  }

  if (isInitializing) {
    return (
      <div className="init-loader-container" style={{display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', backgroundColor: '#09090e', color: '#f8fafc'}}>
        <div className="init-spinner" style={{width: '40px', height: '40px', border: '3px solid rgba(255, 255, 255, 0.05)', borderTopColor: '#6366f1', borderRadius: '50%', animation: 'spin 1s linear infinite'}}></div>
        <p style={{marginTop: '16px', fontSize: '14px', color: '#94a3b8'}}>Loading DocPilot AI...</p>
      </div>
    )
  }

  if (!session) {
    return <AuthScreen onAuthSuccess={setSession} />
  }

  return (
    <div className="app-container">
      <div className="bg-glow orb-1"></div>
      <div className="bg-glow orb-2"></div>
      <Sidebar
        documents={documents}
        onUpload={handleUpload}
        onDelete={handleDelete}
        onSignOut={handleSignOut}
        isUploading={isUploading}
        userEmail={session.user?.email || 'User'}
      />
      <ChatArea
        messages={messages}
        onSendMessage={handleSendMessage}
        isLoading={isQuerying}
        documentCount={documents.length}
      />
    </div>
  )
}
