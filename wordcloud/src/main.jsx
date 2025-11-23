import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

const rootElement = document.getElementById('wordcloud-root')
if (rootElement) {
  const config = {
    backgroundColor: rootElement.dataset.bgColor || '#202025',
    fogColor: rootElement.dataset.fogColor || '#202025',
    wordCount: parseInt(rootElement.dataset.wordCount) || 8,
    sphereRadius: parseInt(rootElement.dataset.radius) || 20,
    wordColor: rootElement.dataset.wordColor || 'white',
    hoverColor: rootElement.dataset.hoverColor || '#fa2720',
    words: window.WORDCLOUD_WORDS || null
  }
  
  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      <App {...config} />
    </React.StrictMode>,
  )
}