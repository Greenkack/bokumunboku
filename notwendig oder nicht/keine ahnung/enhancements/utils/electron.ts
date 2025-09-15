/*
 * Renderer-side helper functions for invoking IPC methods. This file
 * declares the shape of window.electronAPI exposed by preload.js
 * and provides wrapper functions that return typed promises. Use
 * these helpers instead of calling window.electronAPI directly in
 * components or services.
 */

import type {
  ProjectConfiguration,
  AnalysisResults,
} from '../shared/schemas';

// Declare types for the global Electron API injected in preload.
declare global {
  interface Window {
    electronAPI: {
      performCalculations: (
        projectData: ProjectConfiguration,
      ) => Promise<AnalysisResults>;
      getLivePreview: (
        partial: Partial<ProjectConfiguration>,
      ) => Promise<Partial<AnalysisResults>>;
    };
  }
}

// Wrapper for performing full calculations. Returns full analysis.
export const callCalculations = async (
  projectData: ProjectConfiguration,
): Promise<AnalysisResults> => {
  return window.electronAPI.performCalculations(projectData);
};

// Wrapper for requesting a live preview; returns partial results.
export const callLivePreview = async (
  partial: Partial<ProjectConfiguration>,
): Promise<Partial<AnalysisResults>> => {
  return window.electronAPI.getLivePreview(partial);
};