const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export async function uploadDocument(token, file) {
  const formData = new FormData()
  formData.append('file', file)
  
  // Note: Do NOT set Content-Type header when uploading files;
  // let the browser set it automatically with the correct multi-part boundary.
  const response = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  })
  
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Unknown upload error' }))
    throw new Error(err.detail || 'Upload failed')
  }
  
  return response.json()
}

export async function queryDocuments(token, question) {
  const response = await fetch(`${API_BASE}/query`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ question })
  })
  
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Query failed' }))
    throw new Error(err.detail || 'Query failed')
  }
  
  return response.json()
}

export async function getDocuments(token) {
  const response = await fetch(`${API_BASE}/documents`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
  
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Failed to fetch documents' }))
    throw new Error(err.detail || 'Failed to fetch documents')
  }
  
  return response.json()
}

export async function deleteDocument(token, filename) {
  const response = await fetch(`${API_BASE}/documents/${encodeURIComponent(filename)}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
  
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Failed to delete document' }))
    throw new Error(err.detail || 'Failed to delete document')
  }
  
  return response.json()
}
