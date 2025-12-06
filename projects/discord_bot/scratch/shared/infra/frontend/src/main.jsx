import React from 'react'
import { createRoot } from 'react-dom/client'

function App(){
  return (
    <div>
      <h1>Discord Casino Frontend</h1>
      <p>Connect your Discord bot backend and enjoy!</p>
    </div>
  )
}

createRoot(document.getElementById('root')).render(<App />)
