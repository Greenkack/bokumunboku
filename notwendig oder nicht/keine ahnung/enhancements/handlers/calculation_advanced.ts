/*
 * IPC handler with a lightweight queue, timeout, and logging.
 * This module registers handlers for performing calculations and
 * live previews. It spawns the Python CLI as a child process and
 * communicates using JSON via stdin/stdout. Results are returned
 * as parsed objects. Errors are logged and propagated.
 */

import { ipcMain } from 'electron';
import { spawn } from 'node:child_process';
import { z } from 'zod';
import { logger } from '../logging/logger';
import { IPC_CHANNELS } from '../ipc/channelNames';
import { ProjectConfigurationSchema } from '../shared/schemas';

// Timeout in milliseconds for Python calculations. Extend if necessary.
const PYTHON_TIMEOUT_MS = 60_000;

/**
 * Execute a Python CLI script with the given payload. The payload
 * is written to stdin as a JSON string. The script should write
 * its result as JSON to stdout. If the process fails to exit or
 * output parseable JSON within the timeout, the promise rejects.
 */
function runPythonCLI(
  scriptPath: string,
  payload: unknown,
  timeout = PYTHON_TIMEOUT_MS,
): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const py = spawn('python', [scriptPath], { stdio: ['pipe', 'pipe', 'pipe'] });

    // Start timeout timer.
    const timer = setTimeout(() => {
      py.kill('SIGKILL');
      reject(new Error(`Python calculation timed out after ${timeout} ms`));
    }, timeout);

    let stdout = '';
    let stderr = '';

    py.stdout.on('data', (data) => (stdout += String(data)));
    py.stderr.on('data', (data) => (stderr += String(data)));

    py.on('error', (err) => {
      clearTimeout(timer);
      logger.error('Failed to start Python process', { err });
      reject(err);
    });

    py.on('close', (code) => {
      clearTimeout(timer);
      if (code !== 0) {
        logger.error('Python exited with non-zero code', { code, stderr });
        return reject(new Error(stderr || `Python exited with code ${code}`));
      }
      try {
        const json = JSON.parse(stdout);
        resolve(json);
      } catch (err) {
        logger.error('Failed to parse Python JSON output', { err, stdout });
        reject(err);
      }
    });

    // Write payload to stdin and close.
    py.stdin.write(JSON.stringify(payload));
    py.stdin.end();
  });
}

/**
 * Simple FIFO queue that serializes tasks. Each task returns a
 * promise. The queue ensures only one Python process runs at a
 * time, preventing concurrency issues with external resources.
 */
class SimpleQueue {
  private p: Promise<void> = Promise.resolve();
  enqueue<T>(task: () => Promise<T>): Promise<T> {
    // Chain the new task off the end of the queue.
    const next = this.p.then(() => task(), () => task());
    // When next resolves/rejects, reset queue state.
    this.p = next.then(() => undefined, () => undefined);
    return next;
  }
}

const queue = new SimpleQueue();

/**
 * Register IPC handlers for calculations and live preview. The
 * handlers parse inputs, queue Python calls, log activities, and
 * return parsed results. The caller must provide the path to
 * the Python CLI script.
 */
export function registerCalculationIpcHandlers(options: {
  pythonCliPath: string;
}) {
  const { pythonCliPath } = options;

  ipcMain.handle(IPC_CHANNELS.PERFORM_CALCULATIONS, async (_evt, raw) => {
    // Validate input; exceptions propagate to renderer.
    const payload = ProjectConfigurationSchema.parse(raw);
    return queue.enqueue(async () => {
      logger.info('perform-calculations called');
      const result = await runPythonCLI(pythonCliPath, {
        op: 'perform_calculations',
        payload,
      });
      logger.info('perform-calculations done');
      return result;
    });
  });

  ipcMain.handle(IPC_CHANNELS.GET_LIVE_PREVIEW, async (_evt, raw) => {
    // Accept partial configuration; validate loosely.
    const partial = z.any().parse(raw);
    return queue.enqueue(async () => {
      logger.info('get-live-preview called');
      const result = await runPythonCLI(pythonCliPath, {
        op: 'get_live_preview',
        payload: partial,
      });
      logger.info('get-live-preview done');
      return result;
    });
  });
}