import { beforeEach, describe, expect, it } from "vitest";
import { DEFAULT_LUG } from "../inputs/LiftingLugInputs";
import { defaultProject, useStore } from "../store";

beforeEach(() => useStore.setState({ project: defaultProject() }));

describe("kaldırma kulağı girdisi", () => {
  it("varsayılan projede kulak tanımsızdır", () => {
    expect(useStore.getState().project.lifting_lugs ?? null).toBeNull();
  });
  it("setProject ile eklenir ve kaldırılır", () => {
    useStore.getState().setProject((p) => ({ ...p, lifting_lugs: { ...DEFAULT_LUG } }));
    expect(useStore.getState().project.lifting_lugs?.lug_count).toBe(2);
    useStore.getState().setProject((p) => ({ ...p, lifting_lugs: null }));
    expect(useStore.getState().project.lifting_lugs).toBeNull();
  });
});
