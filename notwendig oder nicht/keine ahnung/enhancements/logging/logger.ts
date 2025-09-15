/*
 * Winston logger configuration. Logging is centralized here so
 * multiple modules can reuse the same logger with consistent
 * formatting and transports. Logs are output in JSON with
 * timestamps, making them easy to ingest by cloud log
 * aggregators and to filter locally during debugging.
 */

import winston from 'winston';

// Determine log level from environment. Default to 'info'.
const logLevel = process.env.LOG_LEVEL ?? 'info';

export const logger = winston.createLogger({
  level: logLevel,
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json(),
  ),
  transports: [
    new winston.transports.Console(),
  ],
});

// Optional: Add file transport if LOG_FILE env var is set.
const logFilePath = process.env.LOG_FILE;
if (logFilePath) {
  logger.add(
    new winston.transports.File({ filename: logFilePath }),
  );
}