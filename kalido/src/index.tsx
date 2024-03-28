import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'

const container = document.getElementById('app')
if (container == null) throw new Error('No container found')
const root = createRoot(container)
root.render(<App />)
