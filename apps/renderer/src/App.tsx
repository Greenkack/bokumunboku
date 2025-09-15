// DEF: Interaktive Demo UI für PV-/Speicher-Flow nach deinen Regeln
import React, { useMemo, useState } from "react"
import { Outlet, NavLink } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import { ProjectProvider } from './lib/projectContext'
import {
  calcKwp,
  computePVFlow,
  type ProjectBasics,
  type PVSetup,
  type Tariffs,
} from "@kakerlake/core"

// Formatierer
const nf2 = new Intl.NumberFormat("de-DE", { maximumFractionDigits: 2 })
const ef2 = new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR", maximumFractionDigits: 2 })

export default function App() {
  return (
    <ProjectProvider>
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <div className="grid grid-cols-[280px_1fr]">
          <Sidebar />
          <main className="min-h-screen">
            <header className="sticky top-0 z-10 border-b bg-white/90 backdrop-blur supports-[backdrop-filter]:bg-white/60">
              <div className="mx-auto flex max-w-7xl items-center justify-between p-3">
                <div className="font-semibold">PV/WP Suite</div>
                <nav className="flex gap-3 text-sm">
                  <NavLink to="/ergebnisse" className={({isActive}) => (isActive ? 'font-semibold' : '')}>Dashboard</NavLink>
                  <NavLink to="/pdf-angebote" className={({isActive}) => (isActive ? 'font-semibold' : '')}>PDF</NavLink>
                  <NavLink to="/einstellungen" className={({isActive}) => (isActive ? 'font-semibold' : '')}>Einstellungen</NavLink>
                </nav>
              </div>
            </header>
            <div className="mx-auto max-w-7xl p-4">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </ProjectProvider>
  )
}
  // --- Eingaben (Demo-Defaults nah an deinem Beispiel) ---
  const [householdKWh, setHouseholdKWh] = useState<number>(3500)
  const [heatingKWh, setHeatingKWh] = useState<number>(0)
  const [tariff, setTariff] = useState<number>(0.27)

  const [modules, setModules] = useState<number>(20)
  const [moduleWp, setModuleWp] = useState<number>(440)
  const [batteryKWh, setBatteryKWh] = useState<number>(6.6)

  const [feedIn, setFeedIn] = useState<number>(0.0786)

  // Overrides (können leer bleiben → Core nimmt sinnvolle Standardlogik)
  const [annualProductionOverride, setAnnualProductionOverride] = useState<number | "">("")
  const [directUseOverride, setDirectUseOverride] = useState<number | "">("")

  // --- Core-Inputs bauen ---
  const basics: ProjectBasics = {
    annualConsumptionHouseholdKWh: Math.max(0, Number(householdKWh) || 0),
    annualConsumptionHeatingKWh: Math.max(0, Number(heatingKWh) || 0),
    tariffEuroPerKWh: Math.max(0, Number(tariff) || 0),
  }

  const setup: PVSetup = {
    modules: Math.max(0, Number(modules) || 0),
    moduleWp: Math.max(0, Number(moduleWp) || 0),
    batteryCapacityKWh: Math.max(0, Number(batteryKWh) || 0),
  }

  const tariffs: Tariffs = {
    feedInEuroPerKWh: Math.max(0, Number(feedIn) || 0),
  }

  // --- Core rechnen ---
  const result = useMemo(() => {
    const input = {
      basics,
      setup,
      tariffs,
      annualProductionOverrideKWh:
        annualProductionOverride === "" ? undefined : Math.max(0, Number(annualProductionOverride) || 0),
      directUseOverrideKWh:
        directUseOverride === "" ? undefined : Math.max(0, Number(directUseOverride) || 0),
    }
    return computePVFlow(input)
  }, [basics, setup, tariffs, annualProductionOverride, directUseOverride])

  const kWp = calcKwp(setup.modules, setup.moduleWp)

  return (
    <div className="min-h-screen bg-cyan-400/70 p-6">
      <div className="mx-auto max-w-6xl">
        <header className="mb-6 rounded-xl bg-white/90 p-5 shadow-lg">
          <h1 className="m-0 text-2xl font-bold">✅ Renderer + Core laufen</h1>
          <p className="mt-2 text-sm text-slate-700">
            Diese Demo rechnet live nach deiner Logik (300-Tage-Ladebudget, Einspeisevergütung, de-DE-Format).
            Links Eingaben, rechts Ergebnisse.
          </p>
        </header>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Eingaben */}
          <section className="rounded-xl bg-white p-5 shadow-lg">
            <h2 className="mb-4 text-lg font-semibold">Eingaben</h2>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {/* Verbrauch */}
              <div className="space-y-2">
                <h3 className="font-medium">Verbräuche</h3>
                <label className="block text-sm">
                  Jahresverbrauch Haushalt (kWh)
                  <input
                    type="number"
                    className="mt-1 w-full rounded border p-2"
                    value={householdKWh}
                    onChange={(e) => setHouseholdKWh(Number(e.target.value))}
                    min={0}
                    step={1}
                  />
                </label>
                <label className="block text-sm">
                  Jahresverbrauch Heizung (kWh, optional)
                  <input
                    type="number"
                    className="mt-1 w-full rounded border p-2"
                    value={heatingKWh}
                    onChange={(e) => setHeatingKWh(Number(e.target.value))}
                    min={0}
                    step={1}
                  />
                </label>
                <label className="block text-sm">
                  Stromtarif (€/kWh)
                  <input
                    type="number"
                    className="mt-1 w-full rounded border p-2"
                    value={tariff}
                    onChange={(e) => setTariff(Number(e.target.value))}
                    min={0}
                    step={0.001}
                  />
                </label>
              </div>

              {/* PV/ Speicher */}
              <div className="space-y-2">
                <h3 className="font-medium">PV & Speicher</h3>
                <label className="block text-sm">
                  Module (Stück)
                  <input
                    type="number"
                    className="mt-1 w-full rounded border p-2"
                    value={modules}
                    onChange={(e) => setModules(Number(e.target.value))}
                    min={0}
                    step={1}
                  />
                </label>
                <label className="block text-sm">
                  Modul-Wp (z. B. 440)
                  <input
                    type="number"
                    className="mt-1 w-full rounded border p-2"
                    value={moduleWp}
                    onChange={(e) => setModuleWp(Number(e.target.value))}
                    min={0}
                    step={10}
                  />
                </label>
                <label className="block text-sm">
                  Batterie nutzbar (kWh)
                  <input
                    type="number"
                    className="mt-1 w-full rounded border p-2"
                    value={batteryKWh}
                    onChange={(e) => setBatteryKWh(Number(e.target.value))}
                    min={0}
                    step={0.1}
                  />
                </label>
              </div>

              {/* Tarife/Overrides */}
              <div className="space-y-2">
                <h3 className="font-medium">Tarife & Overrides</h3>
                <label className="block text-sm">
                  Einspeisevergütung (€/kWh)
                  <input
                    type="number"
                    className="mt-1 w-full rounded border p-2"
                    value={feedIn}
                    onChange={(e) => setFeedIn(Number(e.target.value))}
                    min={0}
                    step={0.0001}
                  />
                </label>
                <label className="block text-sm">
                  Jahresproduktion Override (kWh, optional)
                  <input
                    type="number"
                    className="mt-1 w-full rounded border p-2"
                    value={annualProductionOverride}
                    onChange={(e) =>
                      setAnnualProductionOverride(e.target.value === "" ? "" : Number(e.target.value))
                    }
                    min={0}
                    step={1}
                    placeholder="z. B. 9077"
                  />
                </label>
                <label className="block text-sm">
                  Direktverbrauch Override (kWh, optional)
                  <input
                    type="number"
                    className="mt-1 w-full rounded border p-2"
                    value={directUseOverride}
                    onChange={(e) =>
                      setDirectUseOverride(e.target.value === "" ? "" : Number(e.target.value))
                    }
                    min={0}
                    step={1}
                    placeholder="z. B. 2633"
                  />
                </label>
              </div>

              {/* kWp Anzeige */}
              <div className="rounded-lg border bg-slate-50 p-3">
                <div className="text-sm text-slate-600">Anlagengröße</div>
                <div className="text-2xl font-semibold">{nf2.format(kWp)} kWp</div>
                <div className="text-xs text-slate-500">= Module × Wp / 1000</div>
              </div>
            </div>
          </section>

          {/* Ergebnisse */}
          <section className="rounded-xl bg-white p-5 shadow-lg">
            <h2 className="mb-4 text-lg font-semibold">Ergebnisse (pro Jahr)</h2>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <Card title="Produktion" value={`${nf2.format(result.annualProductionKWh)} kWh`} />
              <Card title="Direktverbrauch" value={`${nf2.format(result.directUseKWh)} kWh`} />
              <Card title="→ in Speicher" value={`${nf2.format(result.toBatteryKWh)} kWh`} />
              <Card title="← aus Speicher" value={`${nf2.format(result.fromBatteryKWh)} kWh`} />
              <Card title="Speicher-Überschuss" value={`${nf2.format(result.batterySurplusKWh)} kWh`} />
              <Card title="Netzeinspeisung (Prod.)" value={`${nf2.format(result.feedInFromProductionKWh)} kWh`} />
              <Card title="Grid-Export gesamt" value={`${nf2.format(result.gridExportTotalKWh)} kWh`} />

              <Card title="Ersparnis Direkt" value={ef2.format(result.savingsDirectEuro)} />
              <Card title="Ersparnis Speicher" value={ef2.format(result.savingsFromBatteryEuro)} />
              <Card title="Einnahmen Einspeisung" value={ef2.format(result.revenueFeedInEuro)} />
              <Card title="Einnahmen Batterie-Export" value={ef2.format(result.revenueBatteryExportEuro)} />
              <Card title="Summe/Jahr" value={ef2.format(result.totalAnnualBenefitEuro)} />
            </div>

            <p className="mt-4 text-xs text-slate-500">
              Batterie-Ladebudget = Batterie-kWh × <strong>300</strong> (Fixwert, wie von dir vorgegeben).
            </p>
          </section>
        </div>
      </div>
    </div>
  )
}

function Card({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-lg border p-3">
      <div className="text-sm text-slate-600">{title}</div>
      <div className="text-xl font-semibold">{value}</div>
    </div>
  )
}
