import { useRef, useState, type DragEvent } from "react";
import { useI18n } from "../i18n";

export default function DropZone({ onFiles }: { onFiles: (files: File[]) => void }) {
  const { t } = useI18n();
  const inputRef = useRef<HTMLInputElement>(null);
  const [over, setOver] = useState(false);

  function pickFiles(list: FileList | null) {
    if (!list) return;
    const pdfs = Array.from(list).filter((f) => f.type === "application/pdf");
    if (pdfs.length) onFiles(pdfs);
  }

  function onDrop(e: DragEvent) {
    e.preventDefault();
    setOver(false);
    pickFiles(e.dataTransfer.files);
  }

  return (
    <div
      className={over ? "drop over" : "drop"}
      onDragOver={(e) => {
        e.preventDefault();
        setOver(true);
      }}
      onDragLeave={() => setOver(false)}
      onDrop={onDrop}
    >
      <span>{t("dropHint")}</span>
      <button className="btn" onClick={() => inputRef.current?.click()}>
        {t("addFiles")}
      </button>
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        multiple
        hidden
        aria-label={t("addFiles")}
        onChange={(e) => {
          pickFiles(e.target.files);
          e.target.value = "";
        }}
      />
    </div>
  );
}
