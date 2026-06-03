import { describe, it, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { I18nProvider, useI18n } from ".";

function Probe() {
  const { t, lang, setLang } = useI18n();
  return (
    <div>
      <span data-testid="lang">{lang}</span>
      <span data-testid="save">{t("save")}</span>
      <span data-testid="err">{t("errorLoad", { name: "x.pdf" })}</span>
      <button onClick={() => setLang("de")}>de</button>
    </div>
  );
}

describe("i18n", () => {
  beforeEach(() => localStorage.clear());

  it("defaults to english and translates keys", () => {
    render(<I18nProvider><Probe /></I18nProvider>);
    expect(screen.getByTestId("lang")).toHaveTextContent("en");
    expect(screen.getByTestId("save")).toHaveTextContent("Save PDF");
  });

  it("interpolates variables", () => {
    render(<I18nProvider><Probe /></I18nProvider>);
    expect(screen.getByTestId("err")).toHaveTextContent("Could not read PDF: x.pdf");
  });

  it("switches language and persists the choice", async () => {
    render(<I18nProvider><Probe /></I18nProvider>);
    await userEvent.click(screen.getByText("de"));
    expect(screen.getByTestId("save")).toHaveTextContent("PDF speichern");
    expect(localStorage.getItem("pdfmerger.lang")).toBe("de");
  });
});
