import { describe, it, expect } from "vitest";
import { pagesReducer, type PagesState } from "./pagesReducer";
import type { PdfPage } from "../types";

const page = (id: string): PdfPage => ({
  id,
  fileId: "f",
  fileName: "a.pdf",
  pageIndex: 0,
  thumbnail: "",
});

const empty: PagesState = { pages: [], deleted: [] };

describe("pagesReducer", () => {
  it("adds pages", () => {
    const next = pagesReducer(empty, { type: "add", pages: [page("1"), page("2")] });
    expect(next.pages.map((p) => p.id)).toEqual(["1", "2"]);
  });

  it("moves a page to the trash on remove", () => {
    const start = pagesReducer(empty, { type: "add", pages: [page("1"), page("2")] });
    const next = pagesReducer(start, { type: "remove", id: "1" });
    expect(next.pages.map((p) => p.id)).toEqual(["2"]);
    expect(next.deleted.map((p) => p.id)).toEqual(["1"]);
  });

  it("is idempotent under repeated invocation (StrictMode-safe)", () => {
    const start = pagesReducer(empty, { type: "add", pages: [page("1")] });
    const a = pagesReducer(start, { type: "remove", id: "1" });
    const b = pagesReducer(start, { type: "remove", id: "1" });
    expect(a).toEqual(b);
    expect(a.deleted).toHaveLength(1);
  });

  it("restores a page from the trash", () => {
    const start = pagesReducer({ pages: [], deleted: [page("1")] }, { type: "restore", id: "1" });
    expect(start.pages.map((p) => p.id)).toEqual(["1"]);
    expect(start.deleted).toHaveLength(0);
  });

  it("ignores remove/restore for unknown ids", () => {
    expect(pagesReducer(empty, { type: "remove", id: "x" })).toBe(empty);
    expect(pagesReducer(empty, { type: "restore", id: "x" })).toBe(empty);
  });

  it("reorders pages", () => {
    const start = pagesReducer(empty, { type: "add", pages: [page("1"), page("2"), page("3")] });
    const next = pagesReducer(start, { type: "move", from: 0, to: 2 });
    expect(next.pages.map((p) => p.id)).toEqual(["2", "3", "1"]);
  });
});
