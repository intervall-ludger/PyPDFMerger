import { PDFDocument, StandardFonts } from "pdf-lib";
import { writeFileSync, mkdirSync } from "node:fs";

mkdirSync(new URL("./fixtures", import.meta.url), { recursive: true });

async function build(name, labels) {
  const doc = await PDFDocument.create();
  const font = await doc.embedFont(StandardFonts.Helvetica);
  for (const label of labels) {
    const page = doc.addPage([300, 400]);
    page.drawText(label, { x: 40, y: 200, size: 28, font });
  }
  const bytes = await doc.save();
  writeFileSync(new URL(`./fixtures/${name}`, import.meta.url), bytes);
}

await build("doc-a.pdf", ["A1", "A2"]);
await build("doc-b.pdf", ["B1"]);
console.log("fixtures written");
