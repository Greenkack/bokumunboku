/*
 * Preload script for the Electron application. This file runs in the
 * context isolated preload environment and exposes a small, curated
 * API to the renderer via contextBridge. Only functions explicitly
 * defined here are accessible from window.electronAPI. This
 * improves security by avoiding the default Node integration.
 */

import { contextBridge, ipcRenderer } from 'electron';
import { z } from 'zod';
import {
  ProjectConfigurationSchema,
  AnalysisResultsSchema,
} from './shared/schemas';
import { IPC_CHANNELS } from './ipc/channelNames';

// Handler wrapper for performing calculations. It parses
// the incoming data against the shared schema, invokes the main
// process handler, and validates the returned data. If the
// validation fails, an exception is thrown and propagated to
// the renderer.
const performCalculations = async (projectData: unknown) => {
  const parsed = ProjectConfigurationSchema.parse(projectData);
  const result = await ipcRenderer.invoke(
    IPC_CHANNELS.PERFORM_CALCULATIONS,
    parsed,
  );
  return AnalysisResultsSchema.parse(result);
};

// Handler wrapper for retrieving a live preview. Accepts
// partial project configuration and returns a partial analysis result.
const getLivePreview = async (partial: unknown) => {
  const parsed = ProjectConfigurationSchema.partial().parse(partial);
  const result = await ipcRenderer.invoke(
    IPC_CHANNELS.GET_LIVE_PREVIEW,
    parsed,
  );
  return AnalysisResultsSchema.partial().parse(result);
};

// Expose a safe API to the renderer. Only functions explicitly
// defined here will be available under window.electronAPI.
contextBridge.exposeInMainWorld('electronAPI', {
  performCalculations,
  getLivePreview,
});