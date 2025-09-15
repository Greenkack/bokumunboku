/*
 * Error boundary component for the React renderer. This wraps
 * children components and displays a fallback UI if a runtime
 * error occurs. Using an error boundary prevents errors from
 * breaking the entire React tree and provides a user-friendly
 * message for debugging and support.
 */

import React from 'react';
import { ErrorBoundary } from 'react-error-boundary';

// Fallback UI displayed when an uncaught error bubbles to the boundary.
function Fallback({ error }: { error: Error }) {
  return (
    <div
      style={{ padding: 16, color: 'var(--red-600, #dc2626)' }}
      role="alert"
    >
      <h3>Es ist ein unerwarteter Fehler aufgetreten.</h3>
      <p>Bitte laden Sie die Seite neu oder kontaktieren Sie den Support.</p>
      <pre
        style={{ whiteSpace: 'pre-wrap', color: 'var(--gray-700, #374151)' }}
      >
        {error.message}
      </pre>
    </div>
  );
}

/**
 * Top-level error boundary component. Use it to wrap your routing or
 * page components to prevent white screens on runtime errors.
 */
export const AppErrorBoundary: React.FC<React.PropsWithChildren> = ({
  children,
}) => {
  return <ErrorBoundary FallbackComponent={Fallback}>{children}</ErrorBoundary>;
};