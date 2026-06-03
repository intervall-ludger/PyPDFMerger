import { createContext, useContext, useState, useCallback, type ReactNode } from "react";
import en from "./en.json";
import de from "./de.json";

// To add a language: import its JSON and register it here.
export const languages = { en, de } as const;

export type Lang = keyof typeof languages;
export type TranslationKey = keyof typeof en;

const STORAGE_KEY = "pdfmerger.lang";

function detectLang(): Lang {
  const stored = localStorage.getItem(STORAGE_KEY) as Lang | null;
  if (stored && stored in languages) return stored;
  return navigator.language.startsWith("de") ? "de" : "en";
}

interface I18nValue {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: (key: TranslationKey, vars?: Record<string, string>) => string;
}

const I18nContext = createContext<I18nValue | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(detectLang);

  const setLang = useCallback((next: Lang) => {
    localStorage.setItem(STORAGE_KEY, next);
    setLangState(next);
  }, []);

  const t = useCallback(
    (key: TranslationKey, vars?: Record<string, string>) => {
      let text: string = languages[lang][key] ?? languages.en[key] ?? key;
      if (vars) {
        for (const [name, value] of Object.entries(vars)) {
          text = text.replace(`{${name}}`, value);
        }
      }
      return text;
    },
    [lang],
  );

  return <I18nContext.Provider value={{ lang, setLang, t }}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nValue {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within I18nProvider");
  return ctx;
}
