import React, { useEffect, useRef, useState } from 'react';
import { Button } from 'primereact/button';
// @ts-ignore: pdfjs-dist TypeScript declarations sind optional
import { getDocument, GlobalWorkerOptions } from 'pdfjs-dist';

// Setze den Worker‑Pfad – dieser Pfad muss in deinem Build angepasst werden.
// Bei Verwendung von create-react-app oder Vite muss der Pfad unter public/ liegen.
GlobalWorkerOptions.workerSrc = 'pdfjs-dist/build/pdf.worker.min.js';

interface PDFViewerProps {
  /**
   * PDF‑Inhalt als Uint8Array. Du erhältst diese Bytes vom Backend über
   * perform-calculations() oder aus der PDF‑Generierung.
   */
  pdfBytes: Uint8Array;
}

/**
 * Einfache PDF‑Viewer‑Komponente mit Paginierung.
 *
 * Dieses Beispiel rendert die aktuelle Seite in ein Canvas. Mit
 * “Vorherige” und “Nächste” kannst du blättern. Es wird die Anzahl
 * der Seiten angezeigt. Du kannst das Layout anpassen oder eine
 * Thumbnail‑Navigation hinzufügen.
 */
export const PDFViewer: React.FC<PDFViewerProps> = ({ pdfBytes }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [numPages, setNumPages] = useState(0);

  useEffect(() => {
    const renderPdf = async () => {
      if (!pdfBytes || !canvasRef.current) return;
      const loadingTask = getDocument({ data: pdfBytes });
      const pdf = await loadingTask.promise;
      setNumPages(pdf.numPages);
      const page = await pdf.getPage(pageNumber);
      const viewport = page.getViewport({ scale: 1.3 });
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      if (!context) return;
      canvas.height = viewport.height;
      canvas.width = viewport.width;
      const renderContext = {
        canvasContext: context,
        viewport,
      };
      await page.render(renderContext).promise;
    };
    renderPdf().catch(console.error);
  }, [pdfBytes, pageNumber]);

  const goPrev = () => setPageNumber((p) => Math.max(1, p - 1));
  const goNext = () => setPageNumber((p) => Math.min(numPages, p + 1));

  return (
    <div style={{ maxWidth: '100%' }}>
      <canvas ref={canvasRef} style={{ width: '100%' }} />
      <div className="p-d-flex p-jc-center p-ai-center p-mt-2">
        <Button label="Vorherige" onClick={goPrev} disabled={pageNumber <= 1} className="p-mr-2" />
        <span>
          Seite {pageNumber} / {numPages}
        </span>
        <Button label="Nächste" onClick={goNext} disabled={pageNumber >= numPages} className="p-ml-2" />
      </div>
    </div>
  );
};