// DEF: Kundendaten-Form mit Adress-Paste & Auto-Parsing + „Nächster Bereich“
import React, { useCallback, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  useProject,
  type Anlagentyp, type Einspeisetyp, type Kundentyp, type Anrede, type Titel
} from '../../lib/projectContext'

export default function CustomerForm() {
  const nav = useNavigate()
  const { state, setState } = useProject()
  const [rawAddress, setRawAddress] = useState('')

  // lokaler Alias für Einfachheit:
  const k = state.kunde

  const setK = useCallback(<K extends keyof typeof k>(key: K, val: (typeof k)[K]) => {
    setState(s => ({ ...s, kunde: { ...s.kunde, [key]: val } }))
  }, [setState])

  // --- Adresse-Parsing: "Straße Hausnr, PLZ Ort[, Bundesland]"
  function parseAddress(input: string) {
    const parts = input.split(',').map(p => p.trim()).filter(Boolean)

    // Teil 1: Straße + Hausnummer
    if (parts[0]) {
      // z.B. "Musterstraße 12a"
      const m = parts[0].match(/^(.+?)\s+(\S+)$/)
      if (m) {
        setK('strasse', m[1])
        setK('hausnummer', m[2])
      } else {
        // fallback: ganze Zeile als Straße
        setK('strasse', parts[0])
        setK('hausnummer', '')
      }
    }

    // Teil 2: PLZ + Ort
    if (parts[1]) {
      // z.B. "80331 München"
      const m = parts[1].match(/^(\d{4,5})\s+(.+)$/)
      if (m) {
        setK('plz', m[1])
        setK('ort', m[2])
      } else {
        // fallback
        setK('plz', '')
        setK('ort', parts[1])
      }
    }

    // Teil 3: Bundesland (optional)
    if (parts[2]) {
      setK('bundesland', parts[2])
    }
  }

  const emailInvalid = useMemo(() => {
    if (!k.email) return false
    return !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(k.email)
  }, [k.email])

  function next() {
    // hier könntest du Minimalvalidierung einbauen (z. B. Pflichtfelder Vorname/Nachname)
    // wenn ok:
    nav('/solarkalkulator') // oder '/projekt-bedarf/analyse' – sobald wir den 2. Schritt gebaut haben
  }

  return (
    <div className="rounded-xl bg-white p-5 shadow">
      <h2 className="mb-1 text-lg font-semibold">Projekt – Bedarfsanalyse: Kundendaten</h2>
      <p className="mb-4 text-sm text-slate-600">
        Anlagenmodus: <b>{state.anlagenmodus}</b>
      </p>

      {/* Kopf: Auswahlfelder */}
      <div className="mb-4 grid grid-cols-2 gap-3 md:grid-cols-4">
        <Select
          label="Anlagentyp"
          value={k.anlagentyp}
          onChange={v=>setK('anlagentyp', v as Anlagentyp)}
          options={[
            { value: 'neuanlage', label: 'Neuanlage' },
            { value: 'bestandsanlage', label: 'Bestandsanlage' },
          ]}
        />
        <Select
          label="Einspeisetyp"
          value={k.einspeisetyp}
          onChange={v=>setK('einspeisetyp', v as Einspeisetyp)}
          options={[
            { value: 'teileinspeisung', label: 'Teileinspeisung' },
            { value: 'volleinspeisung', label: 'Volleinspeisung' },
          ]}
        />
        <Select
          label="Kundentyp"
          value={k.kundentyp}
          onChange={v=>setK('kundentyp', v as Kundentyp)}
          options={[
            { value: 'privat', label: 'Privat' },
            { value: 'gewerblich', label: 'Gewerblich' },
          ]}
        />
        <Select
          label="Anrede"
          value={k.anrede}
          onChange={v=>setK('anrede', v as Anrede)}
          options={[
            { value: 'Herr', label: 'Herr' },
            { value: 'Frau', label: 'Frau' },
            { value: 'Familie', label: 'Familie' },
          ]}
        />
      </div>

      <div className="mb-4 grid grid-cols-4 gap-3">
        <Select
          label="Titel"
          value={k.titel}
          onChange={v=>setK('titel', v as Titel)}
          options={[
            { value: '', label: '—' },
            { value: 'Dr.', label: 'Dr.' },
            { value: 'Prof.', label: 'Prof.' },
            { value: 'Mag.', label: 'Mag.' },
            { value: 'Ing.', label: 'Ing.' },
          ]}
        />
        <Input label="Vorname" value={k.vorname} onChange={v=>setK('vorname', v)} />
        <Input label="Nachname" value={k.nachname} onChange={v=>setK('nachname', v)} />
        <div className="hidden md:block" />
      </div>

      {/* Adresse – Paste & Parse */}
      <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
        Komplette Adresse Einfüge Bereich
      </div>
      <div className="mb-3 flex gap-2">
        <input
          className="w-full rounded border p-2"
          placeholder="z. B. Musterstraße 12, 80331 München, Bayern"
          value={rawAddress}
          onChange={e=>setRawAddress(e.target.value)}
        />
        <button
          onClick={()=>parseAddress(rawAddress)}
          className="rounded bg-slate-900 px-3 py-2 text-white"
        >
          Aus Adresse übernehmen
        </button>
      </div>

      <div className="mb-4 grid grid-cols-1 gap-3 md:grid-cols-4">
        <Input label="Straße" value={k.strasse} onChange={v=>setK('strasse', v)} />
        <Input label="Hausnummer" value={k.hausnummer} onChange={v=>setK('hausnummer', v)} />
        <Input label="PLZ" value={k.plz} onChange={v=>setK('plz', v)} />
        <Input label="Ort" value={k.ort} onChange={v=>setK('ort', v)} />
      </div>

      <div className="mb-4 grid grid-cols-1 gap-3 md:grid-cols-3">
        <Input label="E-Mail" value={k.email} onChange={v=>setK('email', v)} invalid={emailInvalid}/>
        <Input label="Telefon (Festnetz)" value={k.telFestnetz} onChange={v=>setK('telFestnetz', v)} />
        <Input label="Telefon (Mobil)" value={k.telMobil} onChange={v=>setK('telMobil', v)} />
      </div>

      <div className="mb-4 grid grid-cols-1 gap-3 md:grid-cols-3">
        <Select
          label="Bundesland"
          value={k.bundesland}
          onChange={v=>setK('bundesland', v)}
          options={[
            { value: '', label: '--- Bitte wählen ---' },
            { value: 'Baden-Württemberg', label: 'Baden-Württemberg' },
            { value: 'Bayern', label: 'Bayern' },
            { value: 'Berlin', label: 'Berlin' },
            { value: 'Brandenburg', label: 'Brandenburg' },
            { value: 'Bremen', label: 'Bremen' },
            { value: 'Hamburg', label: 'Hamburg' },
            { value: 'Hessen', label: 'Hessen' },
            { value: 'Mecklenburg-Vorpommern', label: 'Mecklenburg-Vorpommern' },
            { value: 'Niedersachsen', label: 'Niedersachsen' },
            { value: 'Nordrhein-Westfalen', label: 'Nordrhein-Westfalen' },
            { value: 'Rheinland-Pfalz', label: 'Rheinland-Pfalz' },
            { value: 'Saarland', label: 'Saarland' },
            { value: 'Sachsen', label: 'Sachsen' },
            { value: 'Sachsen-Anhalt', label: 'Sachsen-Anhalt' },
            { value: 'Schleswig-Holstein', label: 'Schleswig-Holstein' },
            { value: 'Thüringen', label: 'Thüringen' },
          ]}
        />
        <div className="md:col-span-2">
          <label className="mb-1 block text-xs text-slate-600">Anmerkung zum Kunden</label>
          <textarea
            className="min-h-[76px] w-full rounded border p-2"
            value={k.bemerkung}
            onChange={e=>setK('bemerkung', e.target.value)}
          />
        </div>
      </div>

      <div className="mt-6 flex gap-2">
        <button onClick={()=>nav('/projekt-bedarf')} className="rounded border px-4 py-2">Zurück</button>
        <button onClick={next} className="rounded bg-slate-900 px-4 py-2 text-white">Nächster Bereich</button>
      </div>
    </div>
  )
}

/* ---------- UI-Atoms ---------- */

function Input({
  label, value, onChange, invalid = false
}: {label:string; value:string; onChange:(v:string)=>void; invalid?:boolean}) {
  return (
    <label className="text-sm">
      <span className="mb-1 block text-xs text-slate-600">{label}</span>
      <input
        className={`w-full rounded border p-2 ${invalid ? 'border-red-500' : ''}`}
        value={value}
        onChange={e=>onChange(e.target.value)}
      />
      {invalid && <span className="mt-1 block text-xs text-red-600">Bitte gültige E-Mail eingeben.</span>}
    </label>
  )
}

function Select({
  label, value, onChange, options
}: {
  label:string
  value:string
  onChange:(v:string)=>void
  options:{value:string; label:string}[]
}) {
  return (
    <label className="text-sm">
      <span className="mb-1 block text-xs text-slate-600">{label}</span>
      <select
        className="w-full rounded border p-2"
        value={value}
        onChange={e=>onChange(e.target.value)}
      >
        {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </label>
  )
}
