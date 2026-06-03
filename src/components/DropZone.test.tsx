import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { I18nProvider } from "../i18n";
import DropZone from "./DropZone";

function setup() {
  const onFiles = vi.fn();
  render(<I18nProvider><DropZone onFiles={onFiles} /></I18nProvider>);
  return { onFiles };
}

const pdf = (name: string) => new File(["%PDF-1.4"], name, { type: "application/pdf" });

describe("DropZone", () => {
  it("passes selected PDF files up", async () => {
    const { onFiles } = setup();
    const input = screen.getByLabelText("Add files") as HTMLInputElement;
    await userEvent.upload(input, pdf("a.pdf"));
    expect(onFiles).toHaveBeenCalledWith([expect.objectContaining({ name: "a.pdf" })]);
  });

  it("filters out non-PDF files", async () => {
    const { onFiles } = setup();
    const input = screen.getByLabelText("Add files") as HTMLInputElement;
    await userEvent.upload(input, new File(["x"], "note.txt", { type: "text/plain" }));
    expect(onFiles).not.toHaveBeenCalled();
  });
});
