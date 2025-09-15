/*
 * Centralized IPC channel names for Electron.
 * Defining channel names in a single file avoids scattering
 * literal strings throughout the codebase. This makes it easy
 * to audit, rename, and search for channels across the project.
 */

export const IPC_CHANNELS = {
  /**
   * Channel invoked to perform heavy calculations in the Python backend.
   * The handler returns the full analysis result based on provided
   * project configuration.
   */
  PERFORM_CALCULATIONS: 'perform-calculations',

  /**
   * Channel invoked to get a live preview of the analysis while
   * the user edits parameters. This may return a partial set of
   * calculated fields.
   */
  GET_LIVE_PREVIEW: 'get-live-preview',
} as const;

export type IpcChannel =
  (typeof IPC_CHANNELS)[keyof typeof IPC_CHANNELS];