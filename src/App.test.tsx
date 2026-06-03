import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { I18nProvider } from "./i18n";
import App from "./App";
import type { PdfPage } from "./types";

const { loadPdf, mergePages, downloadBytes } = vi.hoisted(() => ({
  loadPdf: vi.fn(),
  mergePages: vi.fn(),
  downloadBytes: vi.fn(),
}));

vi.mock("./lib/pdf", () => ({ loadPdf, mergePages }));
vi.mock("./lib/download", () => ({ downloadBytes }));

function makePages(fileId: string, name: string, count: number): PdfPage[] {
  return Array.from({ length: count }, (_, i) => ({
    id: `${fileId}-${i}`,
    fileId,
    fileName: name,
    pageIndex: i,
    thumbnail: "data:image/jpeg;base64,",
  }));
}

const pdfFile = (name: string) => new File(["%PDF-1.4"], name, { type: "application/pdf" });

function renderApp() {
  render(<I18nProvider><App /></I18nProvider>);
}

async function addFile(name: string) {
  await userEvent.upload(screen.getByLabelText("Add files"), pdfFile(name));
}

describe("App", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    loadPdf.mockResolvedValue({ fileId: "f1", bytes: new Uint8Array([1]), pages: makePages("f1", "a.pdf", 2) });
    mergePages.mockResolvedValue(new Uint8Array([9, 9]));
  });

  it("shows the empty state initially", () => {
    renderApp();
    expect(screen.getByText(/No pages yet/)).toBeInTheDocument();
  });

  it("loads pages from an added file", async () => {
    renderApp();
    await addFile("a.pdf");
    expect(await screen.findByLabelText("a.pdf Page 1")).toBeInTheDocument();
    expect(screen.getByLabelText("a.pdf Page 2")).toBeInTheDocument();
  });

  it("moves a deleted page into the trash and restores it", async () => {
    renderApp();
    await addFile("a.pdf");
    const firstCard = await screen.findByLabelText("a.pdf Page 1");
    await userEvent.click(within(firstCard).getByLabelText("Delete"));

    expect(screen.queryByLabelText("a.pdf Page 1")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Trash \(1\)/ })).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Trash \(1\)/ }));
    const dialog = screen.getByRole("dialog");
    await userEvent.click(within(dialog).getByRole("button", { name: "Restore" }));
    await userEvent.click(screen.getByRole("button", { name: "Close" }));

    expect(screen.getByLabelText("a.pdf Page 1")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Trash \(0\)/ })).toBeInTheDocument();
  });

  it("merges pages and triggers a download on save", async () => {
    renderApp();
    await addFile("a.pdf");
    await screen.findByLabelText("a.pdf Page 1");
    await userEvent.click(screen.getByRole("button", { name: "Save PDF" }));

    expect(mergePages).toHaveBeenCalledOnce();
    const passedPages = mergePages.mock.calls[0][0] as PdfPage[];
    expect(passedPages).toHaveLength(2);
    expect(downloadBytes).toHaveBeenCalledWith(expect.any(Uint8Array), "merged.pdf");
  });

  it("shows an error when a file cannot be read", async () => {
    loadPdf.mockRejectedValueOnce(new Error("bad"));
    renderApp();
    await addFile("broken.pdf");
    expect(await screen.findByRole("alert")).toHaveTextContent("Could not read PDF: broken.pdf");
  });
});
