import React from 'react'
import ReactDOM from 'react-dom/client'
import './styles/index.css'
import AppRoutes from './routes';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AppRoutes />,
  </React.StrictMode>,
)
