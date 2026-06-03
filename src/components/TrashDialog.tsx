import { useI18n } from "../i18n";
import type { PdfPage } from "../types";

interface Props {
  pages: PdfPage[];
  onRestore: (id: string) => void;
  onClose: () => void;
}

export default function TrashDialog({ pages, onRestore, onClose }: Props) {
  const { t } = useI18n();
  return (
    <div className="backdrop" onClick={onClose}>
      <div className="dialog" role="dialog" aria-label={t("trashTitle")} onClick={(e) => e.stopPropagation()}>
        <h2>{t("trashTitle")}</h2>
        {pages.length === 0 ? (
          <p>{t("trashEmpty")}</p>
        ) : (
          <ul className="grid">
            {pages.map((page) => (
              <li key={page.id} className="card">
                <img src={page.thumbnail} alt="" />
                <span className="label">
                  {page.fileName}
                  <br />
                  {t("page")} {page.pageIndex + 1}
                </span>
                <button className="btn" onClick={() => onRestore(page.id)}>
                  {t("restore")}
                </button>
              </li>
            ))}
          </ul>
        )}
        <button className="btn" onClick={onClose}>
          {t("close")}
        </button>
      </div>
    </div>
  );
}
