// DEF: App-Bootstrap mit React Router + Tailwind (inkl. Unterrouten für Projekt/Bedarf)
import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import App from './App'

// === Projekt/Bedarf (NEU) ===
import ModeSelect from './routes/Project/ModeSelect'
import CustomerForm from './routes/Project/CustomerForm'

// (bestehende Seiten kannst du später wieder anhängen)
import Results from './routes/Results'
import SolarCalculator from './routes/SolarCalculator'
import HeatpumpSimulator from './routes/HeatpumpSimulator'
import PdfOutput from './routes/PdfOutput'
import Settings from './routes/Settings'
import DashboardCRM from './routes/CRM/DashboardCRM'
import Customers from './routes/CRM/Customers'
import Workflows from './routes/CRM/Workflows'
import Calendar from './routes/CRM/Calendar'
import QuickCalc from './routes/QuickCalc'
import InfoHub from './routes/InfoHub'

import './index.css'

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <Results /> },

      // ▼▼ Projekt & Bedarfsanalyse – jetzt *zweistufig* ▼▼
      {
        path: 'projekt-bedarf',
        children: [
          { index: true, element: <ModeSelect /> },           // Schritt 0: Hilfsscreen + Anlagenmodus
          { path: 'kundendaten', element: <CustomerForm /> }, // Schritt 1: Kundendaten-Form
        ],
      },

      { path: 'solarkalkulator', element: <SolarCalculator /> },
      { path: 'waermepumpe', element: <HeatpumpSimulator /> },
      { path: 'ergebnisse', element: <Results /> },
      { path: 'pdf-angebote', element: <PdfOutput /> },
      { path: 'einstellungen', element: <Settings /> },

      { path: 'crm/dashboard', element: <DashboardCRM /> },
      { path: 'crm/kunden', element: <Customers /> },
      { path: 'crm/workflows', element: <Workflows /> },
      { path: 'crm/kalender', element: <Calendar /> },

      { path: 'schnellkalkulation', element: <QuickCalc /> },
      { path: 'infoportal', element: <InfoHub /> },
    ],
  },
])

const root = document.getElementById('root')
if (!root) throw new Error('root not found')

ReactDOM.createRoot(root).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
)
