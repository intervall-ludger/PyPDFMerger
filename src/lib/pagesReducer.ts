import type { PdfPage } from "../types";
import { reorder } from "./reorder";

export interface PagesState {
  pages: PdfPage[];
  deleted: PdfPage[];
}

export type PagesAction =
  | { type: "add"; pages: PdfPage[] }
  | { type: "remove"; id: string }
  | { type: "restore"; id: string }
  | { type: "move"; from: number; to: number };

export function pagesReducer(state: PagesState, action: PagesAction): PagesState {
  switch (action.type) {
    case "add":
      return { ...state, pages: [...state.pages, ...action.pages] };
    case "remove": {
      const page = state.pages.find((p) => p.id === action.id);
      if (!page) return state;
      return {
        pages: state.pages.filter((p) => p.id !== action.id),
        deleted: [...state.deleted, page],
      };
    }
    case "restore": {
      const page = state.deleted.find((p) => p.id === action.id);
      if (!page) return state;
      return {
        pages: [...state.pages, page],
        deleted: state.deleted.filter((p) => p.id !== action.id),
      };
    }
    case "move":
      return { ...state, pages: reorder(state.pages, action.from, action.to) };
  }
}
