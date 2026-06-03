import { useCallback, useEffect, useReducer, useRef, useState } from "react";
import { useI18n } from "./i18n";
import { loadPdf, mergePages } from "./lib/pdf";
import { downloadBytes } from "./lib/reorder";
import { pagesReducer } from "./lib/pagesReducer";
import LangSwitch from "./components/LangSwitch";
import DropZone from "./components/DropZone";
import PageGrid from "./components/PageGrid";
import TrashDialog from "./components/TrashDialog";

export default function App() {
  const { t } = useI18n();
  const [{ pages, deleted }, dispatch] = useReducer(pagesReducer, { pages: [], deleted: [] });
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [trashOpen, setTrashOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bytesByFile = useRef(new Map<string, Uint8Array>());

  const addFiles = useCallback(async (files: File[]) => {
    setBusy(true);
    setError(null);
    try {
      for (const file of files) {
        try {
          const { fileId, bytes, pages: newPages } = await loadPdf(file);
          bytesByFile.current.set(fileId, bytes);
          dispatch({ type: "add", pages: newPages });
        } catch {
          setError(t("errorLoad", { name: file.name }));
        }
      }
    } finally {
      setBusy(false);
    }
  }, [t]);

  const removePage = useCallback((id: string) => {
    dispatch({ type: "remove", id });
    setSelectedId((cur) => (cur === id ? null : cur));
  }, []);

  const restorePage = useCallback((id: string) => {
    dispatch({ type: "restore", id });
  }, []);

  const movePage = useCallback((from: number, to: number) => {
    dispatch({ type: "move", from, to });
  }, []);

  const save = useCallback(async () => {
    if (pages.length === 0) return;
    setBusy(true);
    setError(null);
    try {
      const bytes = await mergePages(pages, bytesByFile.current);
      downloadBytes(bytes, "merged.pdf");
    } catch {
      setError(t("errorSave"));
    } finally {
      setBusy(false);
    }
  }, [pages, t]);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.key === "Delete" || e.key === "Backspace") && selectedId) {
        removePage(selectedId);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [selectedId, removePage]);

  return (
    <main className="app">
      <header>
        <div>
          <h1>{t("title")}</h1>
          <p className="subtitle">{t("subtitle")}</p>
        </div>
        <LangSwitch />
      </header>

      <DropZone onFiles={addFiles} />

      {error && <p className="error" role="alert">{error}</p>}
      {busy && <p className="status">{t("loading")}</p>}

      {pages.length === 0 && !busy ? (
        <p className="empty">{t("empty")}</p>
      ) : (
        <>
          <p className="hint">{t("reorderHint")}</p>
          <PageGrid
            pages={pages}
            selectedId={selectedId}
            onSelect={setSelectedId}
            onRemove={removePage}
            onMove={movePage}
          />
        </>
      )}

      <div className="bar">
        <button className="btn" onClick={() => setTrashOpen(true)}>
          {t("trash")} ({deleted.length})
        </button>
        <button className="btn primary" disabled={pages.length === 0 || busy} onClick={save}>
          {busy ? t("merging") : t("save")}
        </button>
      </div>

      {trashOpen && (
        <TrashDialog
          pages={deleted}
          onRestore={(id) => {
            restorePage(id);
          }}
          onClose={() => setTrashOpen(false)}
        />
      )}
    </main>
  );
}
