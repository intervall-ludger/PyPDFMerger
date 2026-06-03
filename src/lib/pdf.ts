import * as pdfjs from "pdfjs-dist";
import workerUrl from "pdfjs-dist/build/pdf.worker.min.mjs?url";
import { PDFDocument } from "pdf-lib";
import type { PdfPage } from "../types";

pdfjs.GlobalWorkerOptions.workerSrc = workerUrl;

const THUMB_SCALE = 0.4;

export interface LoadedPdf {
  fileId: string;
  bytes: Uint8Array;
  pages: PdfPage[];
}

export async function loadPdf(file: File): Promise<LoadedPdf> {
  const bytes = new Uint8Array(await file.arrayBuffer());
  const fileId = crypto.randomUUID();
  const doc = await pdfjs.getDocument({ data: bytes.slice() }).promise;

  const pages: PdfPage[] = [];
  for (let i = 1; i <= doc.numPages; i++) {
    const page = await doc.getPage(i);
    const viewport = page.getViewport({ scale: THUMB_SCALE });
    const canvas = document.createElement("canvas");
    canvas.width = viewport.width;
    canvas.height = viewport.height;
    const ctx = canvas.getContext("2d")!;
    await page.render({ canvasContext: ctx, viewport }).promise;
    pages.push({
      id: crypto.randomUUID(),
      fileName: file.name,
      fileId,
      pageIndex: i - 1,
      thumbnail: canvas.toDataURL("image/jpeg", 0.7),
    });
  }
  doc.destroy();
  return { fileId, bytes, pages };
}

export async function mergePages(
  pages: PdfPage[],
  bytesByFile: Map<string, Uint8Array>,
): Promise<Uint8Array> {
  const mergedDoc = await PDFDocument.create();
  const sourceDocs = new Map<string, PDFDocument>();

  for (const page of pages) {
    let sourceDoc = sourceDocs.get(page.fileId);
    if (!sourceDoc) {
      const bytes = bytesByFile.get(page.fileId);
      if (!bytes) {
        console.warn(`No bytes cached for file ${page.fileId}, skipping page ${page.pageIndex}`);
        continue;
      }
      sourceDoc = await PDFDocument.load(bytes);
      sourceDocs.set(page.fileId, sourceDoc);
    }
    const [copied] = await mergedDoc.copyPages(sourceDoc, [page.pageIndex]);
    mergedDoc.addPage(copied);
  }
  return mergedDoc.save();
}
