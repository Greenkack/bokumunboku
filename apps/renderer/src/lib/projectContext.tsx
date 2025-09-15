// DEF: Zentraler Context für Projekt-/Bedarf-Daten (persistiert in localStorage)
import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'

export type Anlagenmodus = 'pv' | 'wp' | 'pv_wp'
export type Anlagentyp = 'neuanlage' | 'bestandsanlage'
export type Einspeisetyp = 'teileinspeisung' | 'volleinspeisung'
export type Kundentyp = 'privat' | 'gewerblich'
export type Anrede = 'Herr' | 'Frau' | 'Familie'
export type Titel = '' | 'Dr.' | 'Prof.' | 'Mag.' | 'Ing.'

export interface Kunde {
  anlagentyp: Anlagentyp
  einspeisetyp: Einspeisetyp
  kundentyp: Kundentyp
  anrede: Anrede
  titel: Titel
  vorname: string
  nachname: string
  strasse: string
  hausnummer: string
  plz: string
  ort: string
  bundesland: string
  email: string
  telFestnetz: string
  telMobil: string
  bemerkung: string
}

export interface ProjektState {
  anlagenmodus: Anlagenmodus
  kunde: Kunde
}

const DEFAULT_STATE: ProjektState = {
  anlagenmodus: 'pv_wp',
  kunde: {
    anlagentyp: 'neuanlage',
    einspeisetyp: 'teileinspeisung',
    kundentyp: 'privat',
    anrede: 'Herr',
    titel: '',
    vorname: '',
    nachname: '',
    strasse: '',
    hausnummer: '',
    plz: '',
    ort: '',
    bundesland: '',
    email: '',
    telFestnetz: '',
    telMobil: '',
    bemerkung: '',
  },
}

const KEY = 'kakerlake.project.v1'

const Ctx = createContext<{
  state: ProjektState
  setState: React.Dispatch<React.SetStateAction<ProjektState>>
  reset: () => void
}>({ state: DEFAULT_STATE, setState: () => {}, reset: () => {} })

export const ProjectProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<ProjektState>(() => {
    try {
      const raw = localStorage.getItem(KEY)
      return raw ? JSON.parse(raw) as ProjektState : DEFAULT_STATE
    } catch {
      return DEFAULT_STATE
    }
  })

  useEffect(() => {
    localStorage.setItem(KEY, JSON.stringify(state))
  }, [state])

  const value = useMemo(() => ({
    state, setState, reset: () => setState(DEFAULT_STATE)
  }), [state])

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useProject() {
  return useContext(Ctx)
}
