import { useState, type DragEvent } from "react";
import { useI18n } from "../i18n";
import type { PdfPage } from "../types";

interface Props {
  pages: PdfPage[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onRemove: (id: string) => void;
  onMove: (from: number, to: number) => void;
}

export default function PageGrid({ pages, selectedId, onSelect, onRemove, onMove }: Props) {
  const { t } = useI18n();
  const [dragIndex, setDragIndex] = useState<number | null>(null);

  function onDrop(e: DragEvent, to: number) {
    e.preventDefault();
    if (dragIndex !== null) onMove(dragIndex, to);
    setDragIndex(null);
  }

  return (
    <ul className="grid" aria-label="pages">
      {pages.map((page, index) => (
        <li
          key={page.id}
          className={page.id === selectedId ? "card selected" : "card"}
          draggable
          aria-label={`${page.fileName} ${t("page")} ${page.pageIndex + 1}`}
          onClick={() => onSelect(page.id)}
          onDragStart={() => setDragIndex(index)}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => onDrop(e, index)}
        >
          <span className="num">{index + 1}</span>
          <button
            className="card-del"
            aria-label={t("delete")}
            onClick={(e) => {
              e.stopPropagation();
              onRemove(page.id);
            }}
          >
            ×
          </button>
          <img src={page.thumbnail} alt="" draggable={false} />
          <span className="label">
            {page.fileName}
            <br />
            {t("page")} {page.pageIndex + 1}
          </span>
        </li>
      ))}
    </ul>
  );
}
