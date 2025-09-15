// DEF: Public API von @kakerlake/core
// - Exportiert calcKwp und computePVFlow (für Renderer)
// - Enthält nur deterministische, seiteneffektfreie Berechnungen
// - Rundungen/Formatierungen macht die UI (Renderer), nicht das Core-Paket

// ---------- Typen ----------
export type ProjectBasics = {
  /** jährlicher Haushaltsverbrauch in kWh */
  annualConsumptionHouseholdKWh: number;
  /** optional: jährlicher Heizstromverbrauch in kWh (zweiter Zähler) */
  annualConsumptionHeatingKWh?: number;
  /** Stromtarif des Kunden in €/kWh (z. B. 0.27) */
  tariffEuroPerKWh: number;
};

export type PVSetup = {
  /** Anzahl PV-Module (Stück) */
  modules: number;
  /** Modul-Nennleistung in Wp (z. B. 440) */
  moduleWp: number;
  /** nutzbare Speicherkapazität in kWh (z. B. 10.2) */
  batteryCapacityKWh?: number;
};

export type Tariffs = {
  /** Einspeisevergütung in €/kWh (z. B. 0.0786) */
  feedInEuroPerKWh: number;
};

export type PVFlowInput = {
  basics: ProjectBasics;
  setup: PVSetup;
  tariffs: Tariffs;

  /**
   * Optionaler Override für Jahresproduktion (kWh).
   * Wenn nicht gesetzt, wird 0 angesetzt (keine Heuristik hier im Core).
   * Die realistische Produktionsberechnung (PVGIS etc.) kann später als
   * eigene Funktion ergänzt und hier reingereicht werden.
   */
  annualProductionOverrideKWh?: number;

  /**
   * Optionaler Override, wie viel davon direkt im Haushalt verbraucht wird (kWh).
   * Wenn nicht gesetzt, wird min(Produktion, Verbrauch) benutzt.
   */
  directUseOverrideKWh?: number;
};

export type PVFlowResult = {
  // Größen
  kWp: number;
  annualProductionKWh: number;

  // Flüsse (Jahreswerte)
  directUseKWh: number;
  toBatteryKWh: number;
  fromBatteryKWh: number;
  batterySurplusKWh: number; // aus Speicher ins Netz
  feedInFromProductionKWh: number; // direkte Überschüsse aus Produktion
  gridExportTotalKWh: number; // Summe Einspeisungen (Produktion + Speicher)

  // Geldwerte
  savingsDirectEuro: number;
  savingsFromBatteryEuro: number;
  revenueFeedInEuro: number;
  revenueBatteryExportEuro: number;
  totalAnnualBenefitEuro: number;
};

// ---------- Helper ----------
/** kWp aus (Module * Wp) */
export function calcKwp(modules: number, moduleWp: number): number {
  const m = Math.max(0, modules | 0);
  const wp = Math.max(0, +moduleWp);
  return (m * wp) / 1000; // Wp → kWp
}

function sumAnnualConsumption(b: ProjectBasics): number {
  return Math.max(0, (b.annualConsumptionHouseholdKWh ?? 0) + (b.annualConsumptionHeatingKWh ?? 0));
}

/**
 * Reine Flusslogik auf Jahresbasis – exakt nach deiner Beschreibung:
 * - Batterie „Ladebudget“ = batteryCapacityKWh * 300
 * - directUse = min(Produktion, Verbrauch) (falls kein Override)
 * - toBattery = min(Produktion - directUse, Ladebudget)
 * - fromBattery = min(toBattery, Verbrauch - directUse)
 * - batterySurplus = toBattery - fromBattery
 * - feedInFromProduction = max(Produktion - directUse - toBattery, 0)
 * - gridExportTotal = feedInFromProduction + batterySurplus
 * - Ersparnisse/Einnahmen per Tarif/Einspeise
 */
export function computePVFlow(input: PVFlowInput): PVFlowResult {
  const { basics, setup, tariffs } = input;

  const kWp = calcKwp(setup.modules, setup.moduleWp);

  const consumption = sumAnnualConsumption(basics);
  const annualProduction = Math.max(0, input.annualProductionOverrideKWh ?? 0);

  const directUse = Math.min(
    annualProduction,
    Math.max(0, input.directUseOverrideKWh ?? consumption)
  );

  const chargeBudget = Math.max(0, (setup.batteryCapacityKWh ?? 0) * 300);
  const remainingAfterDirect = Math.max(0, annualProduction - directUse);

  const toBattery = Math.min(remainingAfterDirect, chargeBudget);
  const fromBattery = Math.min(toBattery, Math.max(0, consumption - directUse));
  const batterySurplus = Math.max(0, toBattery - fromBattery);

  const feedInFromProduction = Math.max(0, annualProduction - directUse - toBattery);
  const gridExportTotal = feedInFromProduction + batterySurplus;

  const tGrid = Math.max(0, basics.tariffEuroPerKWh);
  const tFeed = Math.max(0, tariffs.feedInEuroPerKWh);

  const savingsDirectEuro = directUse * tGrid;
  const savingsFromBatteryEuro = fromBattery * tGrid;
  const revenueFeedInEuro = feedInFromProduction * tFeed;
  const revenueBatteryExportEuro = batterySurplus * tFeed;
  const totalAnnualBenefitEuro =
    savingsDirectEuro + savingsFromBatteryEuro + revenueFeedInEuro + revenueBatteryExportEuro;

  return {
    kWp,
    annualProductionKWh: annualProduction,
    directUseKWh: directUse,
    toBatteryKWh: toBattery,
    fromBatteryKWh: fromBattery,
    batterySurplusKWh: batterySurplus,
    feedInFromProductionKWh: feedInFromProduction,
    gridExportTotalKWh: gridExportTotal,
    savingsDirectEuro,
    savingsFromBatteryEuro,
    revenueFeedInEuro,
    revenueBatteryExportEuro,
    totalAnnualBenefitEuro
  };
}
