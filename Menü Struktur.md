Menü Struktur.md

Hauptmenü (A–G) – beim Start erscheinen sechs große Kacheln (A–F) zentriert (responsive, bei kleinen Displays Umbruch) und zusätzlich links unten ein kleines Menü-Card für G. Einstellungen & Adminbereich.
Persistente Navigation (oben): vorherige Seite | Menü | nächste Seite | zurück zum Hauptmenü
Rechts unten: App beenden (Bestätigungsdialog).

A. Kundendaten / Bedarfsanalyse
B. Solar Calculator
C. Wärmepumpen Simulator
D. Ergebnisse & Dashboard
E. CRM
F. Dokumentenerstellung
G. Einstellungen & Adminbereich (kleines Menü-Card links unten; zusätzlich passwortgeschützt als eigener Bereich)

A) Kundendaten / Bedarfsanalyse

Seite 1 von 5 – Kundendaten

* Anrede -> Dropdown Auswahl zwischen Herr, Frau, Familie
* Titel  ->  Dropdown Auswahl zwischen Dr. , Mag. , Ing. , Mag.
* Vorname
* Nachname
* Straße
* Hausnummer
* Postleitzahl
* Ort
* Email
* Telefon mobil
* Telefon Festnetz
* Bundesland  -> Dropdown 
→ nächste Seite

Seite 2 von 5 – Bedarfsanalyse

Kundentyp → Dropdown: Privat, Gewerblich

Einspeiseart → Dropdown: Volleinspeisung, Teileinspeisung

Bestandsanlage vorhanden → Dropdown: Ja, Nein

Jahresverbrauch Haushalt (kWh)

Jahresverbrauch Heizung (kWh, optional)

Monatliche Stromkosten Haushalt (€)

Monatliche Stromkosten Heizung (€, optional)
Automatik Berechnung und Visualisierung:
Jährlicher Gesamtverbrauch (kWh) = Haushalt kWh + Heizung kWh
Jährliche Gesamtkosten (€) = (Monat Haushalt + Monat Heizung) × 12
Stromtarif (€ / kWh) = Jährliche Gesamtkosten (€) / Jahresverbrauch (kWh)
→ nächste Seite

Seite 3 von 5 – Daten des Gebäudes

* Baujahr des Hauses -> freie Eingabe  \& mit extra + und - Buttons
* Dachdeckungsart  -> Dropdown Auswahl zwischen Frankfurter Pfannen, Trapezblech, Tonziegel, Biberschwanz, Schiefer, Bitumen, Eternit, Schindeln und sonstiges
* Dachausrichtung  -> Dropdown Auswahl zwischen Süd, Südost, Ost, Südwest, West, Nordwest, Nord, Nordost, Flachdach Süd und Flachdach Ost-West
* Dachart  -> Dropdown Auswahl zwischen Satteldach, Satteldach mit Gaube, Pultdach, Flachdach, Walmdach, Krüppelwalmdach, Zeltdach und sonstiges
* Freie Dachfläche (m²) -> freie Eingabe \& mit extra + und - Buttons
* Dachneigung (Grad) -> freie Eingabe \& mit extra + und - Buttons
* Koordinaten in Breitengrad und Längengrad -> optional und über Google Maps abrufbar
* Satellitenbild -> (Google Maps) optional 
→ nächste Seite

Seite 4 von 5 – Zusätzliche Angaben (Freischaltung)


* Interesse an Photovoltaik -> optional aus wählbar mit Kontrollkästchen -> Freischaltung Solar Calculator
* Interesse an Wärmepumpe -> optional aus wählbar mit Kontrollkästchen -> Freischaltung Wärmepumpe Simulator
* Interesse an Photovoltaik \& Wärmepumpe -> optional aus wählbar mit Kontrollkästchen -> Freischaltung Solar Calculator \& Wärmepumpe Simulator

Extras:

* zukünftiges Elektro Auto einplanen -> optional aus wählbar mit Kontrollkästchen
* zukünftige Wärmepumpe einplanen -> optional aus wählbar mit Kontrollkästchen
* sonstige zukünftige Mehrverbrauch / Mehrkosten einplanen -> optional aus wählbar mit Kontrollkästchen 

* Finanzierung / Leasing gewünscht? -> optional aus wählbar mit Kontrollkästchen ( bei Auswahl -> nach der Auswahl der Technik -> Finanzierungsmenü )

→ nächste Seite

Seite 5 von 5 – Zusammenfassung & Speichern

Zusammenfassung aller Eingaben & Optionen
Eingaben speichern → zurück ins Hauptmenü
Freischalt-Logik: Je nach Angaben werden B. Solar Calculator und/oder C. Wärmepumpen Simulator aktiviert.

B) Solar Calculator

Seite 1 von 5 – Technik-Auswahl (PV)

* Anzahl PV Module -> freie Eingabe ( Achtung sehr wichtig für Preismatrix ist dieses Eingabefeld ) \& mit extra + und - Buttons
* PV Modul Hersteller -> -> Dropdown Auswahl zwischen Herstellern die in der Produktdatenbank gespeichert sind
* PV Modul Modell -> Dropdown Auswahl zwischen Produkten von Herstellern die gewählt wurden diese aber auch in der Produktdatenbank gespeichert sind 

Erklärung: 

Wenn Hersteller A gewählt wurde, wird automatisch bei PV Modul Modell Dropdown Menü die Produkte besser gesagt die PV Module von Hersteller A sichtbar und wählbar sein! 
Wenn Hersteller A gewählt wurde, dann wird es nicht möglich sein PV Module des Herstellers B zu wählen! 
Um PV Module von Hersteller B zu wählen, muss Hersteller B bei PV Modul Hersteller gewählt werden!
Anzahl PV-Module (+ / −) (wichtiger Key für Preismatrix)

**-> Automatische Berechnung und Anzeige der PV Anlagengröße in kWp.**

**Formel: Wert für Anzahl PV Module multipliziert mit Wert für Modulleistung PV Modul Modell ( in Produktdatenbank ist auch die Leistung gespeichert mit 440w oder 460w usw. je nach Modell) = PV Anlagengröße in kWp**
**Rechenbeispiel: 32 Module gewählt bei Anzahl PV Module und bei PV Modul Modell ein Produkt gewählt mit 445w Leistung pro Modul.**
**32 x 445 = 14.240** 
**14.240 / 1000 = 14,24 kWp**

Seite 2 von 5 – Wechselrichter

* Wechselrichter Hersteller -> -> Dropdown Auswahl zwischen Herstellern die in der Produktdatenbank gespeichert sind
* Wechselrichter Modell -> Dropdown Auswahl zwischen Produkten von Herstellern die gewählt wurden diese aber auch in der Produktdatenbank gespeichert sind
* Wechselrichter Anzahl -> + - 

**-> Automatische Anzeige der Wechselrichterleistung in W. ( in Produktdatenbank ist auch die Leistung gespeichert mit 4.000w oder 10.000w usw. je nach Modell )**

***Automatische Berechnung und Visualisierung der Wechselrichterleistung:
***Gesamt-WR-Leistung (kW) = Nennleistung (kW) × Anzahl

→ nächste Seite

Seite 3 von 5 – Batteriespeicher

**Auswahlkästchen Batteriespeicher einplanen ( optional wählbar) bei Auswahl -> Freischaltung von Batteriespeicher Bereich**

* Batteriespeicher Hersteller -> -> Dropdown Auswahl zwischen Herstellern die in der Produktdatenbank gespeichert sind
* Batteriespeicher Modell -> Dropdown Auswahl zwischen Produkten von Herstellern die gewählt wurden diese aber auch in der Produktdatenbank gespeichert sind

**> Automatische Anzeige der Speicherkapazität in kWh. ( in Produktdatenbank ist auch die Kapazität gespeichert mit 6,6 kWh oder 10,00 kWh oder 7,80 kWh usw. je nach Modell)**

***Automatische Empfehlung (aus Bedarfsanalyse; Hinweis)

Seite 4 von 5 – Zusätzliche Komponenten (optional)

Zusätzliche Komponenten:

* **Auswahlkästchen zusätzliche Komponente einplanen ( optional wählbar) bei Auswahl -> Freischaltung von zusätzliche Komponenten Bereich ->**

* Wallbox -> Dropdown Auswahl zwischen Wallbox Produkten die auch in der Produktdatenbank gespeichert sind
* Energiemanagementsysteme -> Dropdown Auswahl zwischen Energiemanagementsysteme Produkten die auch in der Produktdatenbank gespeichert sind
* Leistungsoptimierer -> Dropdown Auswahl zwischen Leistungsoptimierer Produkten die auch in der Produktdatenbank gespeichert sind
* Solar Carports -> Dropdown Auswahl zwischen Solar Carports Produkten die auch in der Produktdatenbank gespeichert sind
* Notstromversorgungen -> Dropdown Auswahl zwischen Notstromversorgung Produkten die auch in der Produktdatenbank gespeichert sind 
* Tierabwehrschutz -> Dropdown Auswahl zwischen Tierabwehrschutz Produkten die auch in der Produktdatenbank gespeichert sind
* sonstiges -> freie Eingabe mit Eingabefeld individuell

**nächste Seite Button wird zu Berechnungen Starten Button**
**-> Berechnungen Starten Button klicken ( hat alles gespeichert )**
**-> zurück im Untermenü von Berechnungen**

C) Wärmepumpen Simulator

Seite 1 von 8 – Gebäude-Analyse

Beheizte Wohnfläche (m²) (+ / −)

Gebäudetyp → Neubau KfW40/KfW55/Standard, Altbau saniert/teilsaniert/unsaniert

Baujahr (+ / −)

Dämmqualität → Sehr gut, Gut, Mittel, Schlecht, Sehr schlecht

Aktuelles Heizsystem → Gas-Brennwert, Öl-Brennwert, Pellets, Fernwärme, Strom-Direktheizung, alte Gas/Öl

Warmwasserbedarf → Niedrig (1–2), Mittel (3–4), Hoch (5+)
→ nächste Seite

Seite 2 von 8 – Verbrauchswerte

Heizöl (Liter/Jahr) (+ / −)

Erdgas (kWh/Jahr) (+ / −)

Holz (Ster/Jahr) (+ / −)

Wirkungsgrad aktuelles System (%) (+ / −)

Volllaststunden/Jahr (+ / −)
→ nächste Seite

Seite 3 von 8 – Erweiterte Parameter

Raumtemperatur (°C) (Slider 18–28, + / −)

Auslegungstemperatur außen (°C) (Slider −20–0 oder Auto via PLZ-Tabelle)

Heiztage/Jahr (Slider 130–350, + / −)

Heizsystem-Vorlauf → FBH 35 °C, Wand 40 °C, Radiatoren 55 °C, Alt-Radiatoren 70 °C
→ nächste Seite

Seite 4 von 8 – Heizlastberechnung

Heizlast berechnen → Anzeige:

Heizlast (kW), spez. Heizlast (W/m²), energetische Qualität

Status: gespeichert → nächste Seite

Seite 5 von 8 – Wärmepumpen-Auswahl

Benötigte Heizleistung (kW) (aus Seite 4)

Wärmepumpentyp → Luft-Wasser, Sole-Wasser, Wasser-Wasser, Luft-Luft

Installationsart → Außen, Innen, Split, Dach

Hersteller-Präferenz (Dropdown)

Budget → Economy, Standard, Premium

Erweiterungen:

Dimensionierungsfaktor (0,50–3,00 %)

Warmwasserspeicher (Liter) (200–1.000)

Backup-Heizstab (Checkbox), Smart-Grid-Ready (Checkbox)

Wärmepumpe suchen → Anzeige: Hersteller, Modell, Leistung (kW), COP (A2/W35), SCOP, dB(A), L×B×H, kg

Berechnung speichern → gespeichert
→ nächste Seite

Seite 6 von 8 – Wirtschaftlichkeitsanalyse

Energiepreise: Strom (ct/kWh) (optional auto aus PV), Gas (ct/kWh), Öl (ct/kWh)

Förderung & Kosten: BEG (€) (manuell/auto), Installationskosten (€), Wartung/Jahr (€)

Wirtschaftlichkeit berechnen → Anzeige:

Gesamtinvestition (€), jährliche Ersparnis (€), Amortisation (Jahre), 20-Jahre-Ersparnis (€)

Kostenaufstellung: Position, Betrag

Cashflow-Diagramm

Status: gespeichert
→ nächste Seite

Seite 7 von 8 – Komponenten & Angebot

Basispreis (auto): Material (€), Arbeit (€), Summe Netto (€)

Rabatte / Aufpreise: je % und € → auto: Nachlass/Zuschlag, Rabatt gesamt, Aufpreis gesamt

BEG-Förderlogik:

Grundförderung 30 %

Natürliches Kältemittel (+5 %)

Heizungstausch (+20 %)

Einkommen < 40.000 €/a (+20 %)

Deckel: max. 70 % (auch wenn Eingaben > 70 %)

Auto-Anzeige: Förder-%, Förderbetrag (€), Nettosumme nach Förderung (€)

Speichern → gespeichert
→ nächste Seite

Seite 8 von 8 – Ergebnisse Wärmepumpen-Simulation

KPIs: Wohnfläche (m²), WP-Leistung (kW), Invest (€), Ersparnis/Jahr (€), Heizlast (kW), SCOP, Amortisation (Jahre)

Ergebnisse speichern → gespeichert → zurück ins Hauptmenü

D) Ergebnisse & Dashboard

Seite 1 von 2 – Ergebnisse der Analyse (KPIs)

Gesamtinvestition Brutto (€)

PV-Anlagengröße (kWp), Stromproduktion (kWh/Jahr)

Autarkiegrad (%), Eigenverbrauchsquote (%)

Jährlicher finanzieller Vorteil (€), Amortisationszeit (Jahre)

Monatlicher Vergleich: Produktion vs. Verbrauch

Stromkosten 10/20 Jahre kumuliert (mit/ohne Preissteigerung)

Eigenverbrauch vs. Netzbezug, Aufteilung erzeugter Strom

Kumulierter Cashflow, Laufzeit

ROI, NPV, IRR

Deckungsgrad (%), kWp-spez. Ertrag, Performance Ratio (%)

CO₂-Bilanz, ges. CO₂-Einsparung, Äquivalent Bäume, CO₂-Amortisation, vermiedene Autokilometer

Netzeinspeisung (kWh), Netzbezug, Netzunabhängigkeit

Wetterbereinigte Jahreserzeugung, Leistung nach 10/20 Jahren, Gesamtenergieverlust

Kapitalwert, Speicherladung/-nutzung, mit/ohne Speicher

Rabatte, Aufpreise, jährliche Gesamteinsparung (€)

Batterieüberschuss, Einspeisevergütung, Stromtarif, Stromkosten jährlich, Stromverbrauch jährlich

Wochen/Monat/Tag-Produktion, monatliche Einspeisevergütung, Tarifsvergleich, Investitionsnutzwert, Szenarienvergleich, Speicherwirkung

Ergebnisse speichern → gespeichert
→ nächste Seite

Seite 2 von 2 – Dashboard (Charts & Visualisierungen)

Charts/Diagramme zu allen oben genannten KPIs

Interaktive Filter: Zeiträume, Szenarien, mit/ohne Speicher

Export: PNG/PDF der Charts

E) CRM

Seite 1 von 3 – Leads & Kontakte (CRUD)

Lead-Erfassung (Formular/Import), Status, Quelle

Kontakt-Stammdaten, Kommunikationshistorie, Tags

Zuordnung zu Projekten/Angeboten

Seite 2 von 3 – Opportunities & Pipeline (CRUD)

Phasen: Qualifiziert → Angebot → Verhandlung → Gewonnen/Verloren

Angebotsverknüpfung (PV/WP/Kombi), Wert, Abschlusswahrsch.

Aufgaben & Erinnerungen

Seite 3 von 3 – Termine & Notizen

Kalenderansicht, Terminliste

Notizen/Dateien pro Lead/Opportunity

(Erweiterbar um Planungs-Module)

F) Dokumentenerstellung

Seite 1 von 6 – Modus & Quelle

Berechnungsart: Photovoltaik, Wärmepumpe, PV + WP

Datenquelle: zuletzt gespeicherte Ergebnisse wählen

Theme/Schriftarten/Farben (Preview)

Seite 2 von 6 – PV Standardausgabe (7 Seiten)

Template-Auswahl

YML-Positionsdateien (Koordinaten, Schriftart, Schriftgröße, Eigenschaften)

Alle Inhalte als dynamische Keys mit PDF-Bytes; pro Key optional ein-/ausblendbar

Seite 3 von 6 – WP Standardausgabe (16 Seiten)

Gleiches Prinzip: Templates + YML (Positionen, Typografie)

Dynamische Keys mit PDF-Bytes, optional ein-/ausblendbar

Seite 4 von 6 – Erweiterte Inhalte (PV & WP)

Optionale Diagramme, Finanzierungsinfos, Berechnungen

Regel: Standardseiten immer zuerst; optionale Seiten anhängen

Reihenfolge via Drag & Drop konfigurierbar

Seite 5 von 6 – Multi-PDF (Firmenrotation)

Mehrfachauswahl von Firmen aus Firmendatenbank

Ergebnis: N Firmen → N Angebote

Firmenspezifisch: Logos, Daten, Dokumente, Bilder, Produkte, Preise

Rotations-Algorithmus: pro Firma abweichende Produktkombination & Preise

Parameter/Rotationseinstellungen konfigurierbar (z. B. Variation, Gewichtung)

Seite 6 von 6 – Rendern & Export

ICC-Farbmanagement, Kompression, Metadaten/QR

Auto-Repair (XREF, Fonts, Bilder)

Preview (Zoom, Seiten, Layer-Overlay)

Export PDF & Batch/Headless

Speichern: PDF-Bytes je Key verfügbar

G) Einstellungen & Adminbereich (Passwortgeschützt; CRUD überall)

Seite 1 von 10 – Firmenverwaltung

Neue Firma anlegen, Standardfirma setzen

Firmendatenbank (CRUD): Dokumente, Angaben, Bilder, Logos

Seite 2 von 10 – Produktverwaltung

BULK-Upload: XLSX/CSV/XLS/JSON (Drag & Drop)

Neues Produkt manuell (alle Eigenschaften)

Produkt-CRUD, Bilder-Upload (JPG/PNG), Datenblatt-PDF Upload

Seite 3 von 10 – Preis-Matrix

Upload/Ersetzen/Bearbeiten/Löschen (XLS/XLSX/CSV)

Manuelle Bearbeitung (CRUD)

Logik: Excel INDEX/VERGLEICH

Beispiel: =INDEX(Y110:CP204;VERGLEICH('Auswahl der Technik'!C37;Y110:Y289;0);VERGLEICH('Auswahl der Technik'!C65;Y110:CP110;0))

Treiber: Anzahl Module & Speichermodell

Seite 4 von 10 – Einspeisetarife
Teileinspeisung:

0,00–10,00 kWp → 7,90 ct/kWh

10,01–40,00 kWp → 6,80 ct/kWh

40,01–100,00 kWp → 5,30 ct/kWh
Volleinspeisung:

0,00–10,00 kWp → 12,90 ct/kWh

10,01–40,00 kWp → 10,80 ct/kWh

40,01–100,00 kWp → 10,80 ct/kWh

Speichern / Bearbeiten / Löschen

Seite 5 von 10 – PDF-Einstellungen

Design/Themes (Farben)

Vorlagen-DB: Titel, Anschreiben, Titelbilder

Schriftarten (Familie, Größe, Fallbacks)

Seite 6 von 10 – Erweiterte Berechnungsparameter

Mehrwertsteuer (%)

Leistungsdegradation (%/a)

Jährliche Wartungspauschale (€ netto)

Inflationsrate (%), Wartungskosten-Steigerung (% p. a.)

Variable Wartungskosten (€/kWp p. a., netto)

Alternativanlage Zinsrate (%)

Seite 7 von 10 – Ertrag & Simulation

Globale Ertragsanpassung (%)

Referenz-Spezialertrag (kWh/kWp/a)

Spezifische Jahreserträge (Ausrichtung/Neigung-Tabelle)

Mehrjahressimulation: Dauer (Jahre), Strompreissteigerung (%)

Seite 8 von 10 – Cheat-Amortisationszeit (optional)

Modus: absolute_reduction / percentage_reduction / fixed_reduction

Feste Jahre (J), Prozentuale Reduktion (%)

Seite 9 von 10 – API-Keys

Google Maps, Bing Maps, OpenStreetMap Nominatim E-Mail

Schlüsselbereiche verwalten (manuell)

Seite 10 von 10 – Lokalisierung, Debug & Reset

Texte (JSON-Editor) → {} → Texte speichern

Debug-Modus (App-weit)

Daten zurücksetzen:

Optionen anzeigen (Checkbox)

Warnhinweis („nicht rückgängig…“)

Bestätigung: ALLES ENDGÜLTIG LÖSCHEN

Button: App-Daten zurücksetzen

Globale Regeln & Datenhaltung

Jedes Eingabefeld, jede Auswahl, jede Berechnung, jedes Ergebnis, jede Visualisierung, jede Datenbankzeile, jedes Bild/Dokument erzeugt einen dynamischen Key und parallel PDF-Bytes.

Alle Keys sind optional ein-/ausblendbar und individuell kombinierbar (für Standard- und erweiterte PDF-Ausgaben).

Alle Datenbanken (Firmen, Produkte, Preise, Tarife, Vorlagen, Lokalisierung) unterstützen CRUD.

Sidemenü (Drawer) überall verfügbar: Live-Vorschau, Simulationsdauer, Strompreissteigerung, Rabatte/Aufpreise (%, €), Zurück/Nächste/Hauptmenü.

Multi-PDF: N ausgewählte Firmen ⇒ N firmenspezifische Angebote (Logos, Produkte, Preise), via Rotations-Algorithmus parametrierbar.

UI-Komponenten (PrimeReact – vollständig verwenden)

Upload

Cards

Breadcrumb

ContextMenu

Dock

MegaMenu

Menu

Menubar

PanelMenu

Steps

TabMenu

TieredMenu

Chart

Chart.js

Messages

Message

Messages

Toast

Media

Carousel

Galleria

Image

Misc

Avatar

Badge

BlockUI

Chip

Inplace

MeterGroup

ScrollTop

Skeleton

ProgressBar

ProgressSpinner

Ripple

StyleClass

Tag

Terminal

Input

AutoComplete

Calendar

CascadeSelect

Checkbox

Chips

ColorPicker

Dropdown

Editor

FloatLabel

IconField

InputGroup

InputMask

InputSwitch

InputNumber

InputOtp

InputText

InputTextarea

KeyFilter

Knob

Listbox

Mention

MultiSelect

MultiStateCheckbox

Password

RadioButton

Rating

SelectButton

Slider

TreeSelect

TriStateCheckbox

ToggleButton

Button

Button

Speed Dial

SplitButton

Data

DataTable

DataView

DataScroller

OrderList

Org Chart

Paginator

PickList

Tree

TreeTable

Timeline

VirtualScroller

Panel

Accordion

Card

Deferred

Divider

Fieldset

Panel

ScrollPanel

Splitter

Stepper

TabView

Toolbar

Overlay

ConfirmDialog

ConfirmPopup

Dialog

OverlayPanel

Sidebar

Tooltip