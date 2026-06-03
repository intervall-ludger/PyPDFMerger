import { describe, it, expect } from "vitest";
import { reorder } from "./reorder";

describe("reorder", () => {
  it("moves an item forward", () => {
    expect(reorder(["a", "b", "c", "d"], 0, 2)).toEqual(["b", "c", "a", "d"]);
  });

  it("moves an item backward", () => {
    expect(reorder(["a", "b", "c", "d"], 3, 1)).toEqual(["a", "d", "b", "c"]);
  });

  it("returns the same content when from equals to", () => {
    expect(reorder(["a", "b", "c"], 1, 1)).toEqual(["a", "b", "c"]);
  });

  it("ignores out-of-range indices", () => {
    expect(reorder(["a", "b"], 0, 5)).toEqual(["a", "b"]);
    expect(reorder(["a", "b"], -1, 1)).toEqual(["a", "b"]);
  });

  it("does not mutate the input", () => {
    const input = ["a", "b", "c"];
    reorder(input, 0, 2);
    expect(input).toEqual(["a", "b", "c"]);
  });
});
