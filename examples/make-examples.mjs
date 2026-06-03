import { PDFDocument, StandardFonts, rgb } from "pdf-lib";
import { writeFileSync } from "node:fs";

const blue = rgb(0.106, 0.247, 0.682);
const red = rgb(0.886, 0.137, 0.102);
const ink = rgb(0.067, 0.067, 0.067);

async function build(name, title, pages) {
  const doc = await PDFDocument.create();
  const bold = await doc.embedFont(StandardFonts.HelveticaBold);
  const font = await doc.embedFont(StandardFonts.Helvetica);

  pages.forEach((heading, i) => {
    const page = doc.addPage([420, 595]);
    page.drawRectangle({ x: 0, y: 545, width: 420, height: 50, color: blue });
    page.drawText(title, { x: 32, y: 562, size: 18, font: bold, color: rgb(1, 1, 1) });
    page.drawText(heading, { x: 32, y: 470, size: 30, font: bold, color: ink });
    page.drawRectangle({ x: 32, y: 455, width: 80, height: 6, color: red });
    page.drawText(`Page ${i + 1} of ${pages.length}`, { x: 32, y: 40, size: 11, font, color: ink });
  });

  writeFileSync(new URL(`./${name}`, import.meta.url), await doc.save());
}

await build("cover-letter.pdf", "ACME Corp", ["Cover Letter"]);
await build("report.pdf", "Quarterly Report", ["Summary", "Figures", "Outlook"]);
await build("invoice.pdf", "Invoice 2026-042", ["Items", "Terms"]);
console.log("example PDFs written");
