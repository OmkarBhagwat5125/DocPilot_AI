import React, { useState } from 'react'
import { supabase } from '../lib/supabase'
import { Mail, Lock, Loader2, ArrowRight, Zap, Layers, Shield } from 'lucide-react'
import Logo from './Logo'
import './AuthScreen.css'

export default function AuthScreen({ onAuthSuccess }) {
  const [isSignUp, setIsSignUp] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errorMsg, setErrorMsg] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrorMsg('')
    setIsLoading(true)

    try {
      if (isSignUp) {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
        })
        if (error) throw error
        
        // Supabase might require email confirmation on the free tier. 
        // If an immediate session is active, pass it, otherwise tell user to check email.
        if (data.session) {
          onAuthSuccess(data.session)
        } else {
          setErrorMsg('Registration successful! Please check your email for the confirmation link.')
        }
      } else {
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        })
        if (error) throw error
        if (data.session) {
          onAuthSuccess(data.session)
        }
      }
    } catch (err) {
      setErrorMsg(err.message || 'Authentication failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="noise-overlay"></div>
      <div className="auth-mesh-bg"></div>
      <div className="bg-glow orb-1"></div>
      <div className="bg-glow orb-2"></div>
      <div className="bg-glow orb-3"></div>
      
      <div className="auth-card glass-panel">
        <div className="auth-header">
          <div className="auth-logo">
            <Logo size={36} />
            <h1 className="gradient-text font-heading">DocPilot AI</h1>
          </div>
          <p className="auth-tagline">Upload. Ask. Understand.</p>
          
          <div className="feature-badges">
            <div className="feature-badge">
              <Zap size={14} className="badge-icon accent-emerald" />
              <span>RAG-Powered</span>
            </div>
            <div className="feature-badge">
              <Layers size={14} className="badge-icon accent-cyan" />
              <span>Multi-Format</span>
            </div>
            <div className="feature-badge">
              <Shield size={14} className="badge-icon primary-color" />
              <span>Secure</span>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="auth-form" id="auth-form-submit">
          <div className="input-group">
            <label htmlFor="auth-email">Email Address</label>
            <div className="input-wrapper">
              <Mail className="input-icon" size={18} />
              <input
                id="auth-email"
                type="email"
                className="input-field"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="input-group">
            <label htmlFor="auth-password">Password</label>
            <div className="input-wrapper">
              <Lock className="input-icon" size={18} />
              <input
                id="auth-password"
                type="password"
                className="input-field"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          {errorMsg && (
            <div className={`auth-message-box ${errorMsg.includes('successful') ? 'success-msg' : 'error-msg'}`}>
              {errorMsg}
            </div>
          )}

          <button
            id="auth-submit-btn"
            type="submit"
            className="auth-submit-btn"
            disabled={isLoading}
          >
            {isLoading ? (
              <Loader2 className="spinner" size={20} />
            ) : (
              <>
                {isSignUp ? 'Create Account' : 'Sign In'}
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            {isSignUp ? 'Already have an account?' : "Don't have an account?"}
            <button
              id="auth-toggle-mode"
              className="auth-toggle-link"
              type="button"
              onClick={() => {
                setIsSignUp(!isSignUp)
                setErrorMsg('')
              }}
            >
              {isSignUp ? 'Sign In' : 'Sign Up'}
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}
