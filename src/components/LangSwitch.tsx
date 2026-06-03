import { languages, useI18n, type Lang } from "../i18n";

export default function LangSwitch() {
  const { lang, setLang } = useI18n();
  return (
    <div className="lang" role="group" aria-label="Language">
      {(Object.keys(languages) as Lang[]).map((code) => (
        <button
          key={code}
          className={code === lang ? "active" : ""}
          aria-pressed={code === lang}
          onClick={() => setLang(code)}
        >
          {code.toUpperCase()}
        </button>
      ))}
    </div>
  );
}
