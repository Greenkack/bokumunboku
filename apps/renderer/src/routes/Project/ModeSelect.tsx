// DEF: Hilfsscreen + Auswahl „Anlagenmodus“; führt zum Kundendaten-Form
import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useProject, type Anlagenmodus } from '../../lib/projectContext'

export default function ModeSelect() {
  const nav = useNavigate()
  const { state, setState, reset } = useProject()

  function setMode(m: Anlagenmodus) {
    setState(s => ({ ...s, anlagenmodus: m }))
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <section className="rounded-xl bg-white p-5 shadow">
        <h2 className="mb-2 text-lg font-semibold">Bedarfsanalyse – Hinweise</h2>
        <ul className="list-disc pl-5 text-sm text-slate-600">
          <li>Wähle zuerst den <b>Anlagenmodus</b>.</li>
          <li>Im nächsten Schritt erfasst du die <b>Kundendaten</b> (inkl. Adress-Paste & Auto-Parsing).</li>
          <li>Alle Eingaben werden lokal gespeichert (Browser/LocalStorage) und sind revisierbar.</li>
        </ul>
        <div className="mt-4">
          <button onClick={reset} className="rounded border px-3 py-1 text-sm">Eingaben zurücksetzen</button>
        </div>
      </section>

      <section className="rounded-xl bg-white p-5 shadow">
        <h2 className="mb-3 text-lg font-semibold">Anlagenmodus wählen</h2>
        <div className="grid grid-cols-3 gap-2">
          <ModeCard
            label="Photovoltaik"
            active={state.anlagenmodus === 'pv'}
            onClick={() => setMode('pv')}
          />
          <ModeCard
            label="Wärmepumpe"
            active={state.anlagenmodus === 'wp'}
            onClick={() => setMode('wp')}
          />
          <ModeCard
            label="PV + WP"
            active={state.anlagenmodus === 'pv_wp'}
            onClick={() => setMode('pv_wp')}
          />
        </div>

        <div className="mt-6 flex gap-2">
          <button
            onClick={() => nav('/projekt-bedarf/kundendaten')}
            className="rounded bg-slate-900 px-4 py-2 text-white"
          >
            Nächster Bereich
          </button>
          <span className="self-center text-xs text-slate-500">
            Aktuell gewählt: <b>{state.anlagenmodus}</b>
          </span>
        </div>
      </section>
    </div>
  )
}

function ModeCard({ label, active, onClick }: {label:string; active:boolean; onClick:()=>void}) {
  return (
    <button
      onClick={onClick}
      className={`rounded border p-4 text-sm ${active ? 'bg-slate-900 text-white' : 'bg-white hover:bg-slate-50'}`}
    >
      {label}
    </button>
  )
}
