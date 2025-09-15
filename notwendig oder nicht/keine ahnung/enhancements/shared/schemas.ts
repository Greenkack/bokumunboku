/*
 * Shared validation schemas for the project. The same schema file is
 * imported by both the Electron main process and the renderer to
 * validate IPC messages. Using a single schema definition helps
 * ensure type consistency across process boundaries. We use Zod for
 * runtime validation and TypeScript type inference.
 */

import { z } from 'zod';

/**
 * Schema for the overall configuration of a PV project. Fields are
 * intentionally optional to support partial updates when the user
 * edits values in the UI. Use `strict()` to disallow unknown
 * properties, which helps catch typos early.
 */
export const ProjectConfigurationSchema = z
  .object({
    /** Arbitrary customer metadata. Keys map to unknown values. */
    customer_data: z.record(z.any()).optional(),

    /**
     * Parameters describing the PV system. The nested object uses
     * default empty values so that missing values still produce
     * defined keys. Zod's `coerce` ensures numeric inputs are
     * converted from strings.
     */
    project_details: z
      .object({
        module_quantity: z.coerce.number().int().min(0).default(0),
        selected_module_id: z.string().optional(),
        inverter_id: z.string().optional(),
        battery_capacity_kwh: z
          .number()
          .nonnegative()
          .optional(),
      })
      .partial()
      .default({}),

    /** Economic assumptions for the PV project. */
    economic_data: z
      .object({
        electricity_price_ct_per_kwh: z.number().positive().optional(),
        feed_in_tariff_ct_per_kwh: z.number().nonnegative().optional(),
      })
      .partial()
      .default({}),
  })
  .strict();

export type ProjectConfiguration = z.infer<typeof ProjectConfigurationSchema>;

/**
 * Schema describing the analysis results returned from the backend.
 * Only a small subset of KPIs is defined here for brevity. Additional
 * fields in the analysis can still be returned thanks to `catchall`.
 */
export const AnalysisResultsSchema = z
  .object({
    anlage_kwp: z.number().optional(),
    annual_pv_production_kwh: z.number().optional(),
    total_investment_netto: z.number().optional(),
    total_investment_brutto: z.number().optional(),
    self_supply_rate_percent: z.number().optional(),
    amortization_time_years: z.number().optional(),
    annual_financial_benefit_year1: z.number().optional(),
    npv_value: z.number().optional(),
    simple_roi_percent: z.number().optional(),
    annual_co2_savings_kg: z.number().optional(),
  })
  // Accept additional KPI fields that may be returned by the Python
  // backend without failing validation. This gives the backend
  // flexibility to evolve without breaking the UI.
  .catchall(z.any());

export type AnalysisResults = z.infer<typeof AnalysisResultsSchema>;