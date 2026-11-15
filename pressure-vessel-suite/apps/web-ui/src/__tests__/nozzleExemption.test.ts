import { beforeEach, describe, expect, it } from "vitest";
import { defaultProject, useStore } from "../store";

describe("Küçük açıklık muafiyeti (UG-36(c)(3)) kullanıcı beyanı alanları", () => {
  beforeEach(() => {
    useStore.setState({ project: defaultProject(), selection: null, geoSubStep: 0 });
  });

  it("defaultProject içindeki varsayılan nozul üç beyanı da false olarak içerir", () => {
    const project = defaultProject();
    const nz = project.nozzles[0];
    expect(nz).toBeDefined();
    expect(nz.no_rapid_pressure_fluctuation_confirmed).toBe(false);
    expect(nz.opening_spacing_confirmed).toBe(false);
    expect(nz.welded_attachment_confirmed).toBe(false);
  });

  it("addNozzle ile eklenen yeni nozulda üç beyan da false başlar", () => {
    useStore.getState().addNozzle();
    const nozzles = useStore.getState().project.nozzles;
    const added = nozzles[nozzles.length - 1];
    expect(added.no_rapid_pressure_fluctuation_confirmed).toBe(false);
    expect(added.opening_spacing_confirmed).toBe(false);
    expect(added.welded_attachment_confirmed).toBe(false);
  });

  it("addPipeNozzle ile eklenen nozulda üç beyan da false başlar", () => {
    const hostId = useStore.getState().project.shell_sections[0].section_id;
    useStore.getState().addPipeNozzle({
      host_component_id: hostId,
      nozzle_type: "flanged",
      nps: "4",
      schedule: "SCH40",
      rating_class: "CL150",
      axial_position: 500,
      circumferential_angle: 0,
    });
    const nozzles = useStore.getState().project.nozzles;
    const added = nozzles[nozzles.length - 1];
    expect(added.no_rapid_pressure_fluctuation_confirmed).toBe(false);
    expect(added.opening_spacing_confirmed).toBe(false);
    expect(added.welded_attachment_confirmed).toBe(false);
  });

  it("addCoupling ile eklenen manşonda üç beyan da false başlar", () => {
    const hostId = useStore.getState().project.shell_sections[0].section_id;
    useStore.getState().addCoupling({
      host_component_id: hostId,
      nozzle_type: "coupling",
      nps: "1",
      rating_class: "3000#",
      coupling_form: "full",
      axial_position: 400,
      circumferential_angle: 45,
    });
    const nozzles = useStore.getState().project.nozzles;
    const added = nozzles[nozzles.length - 1];
    expect(added.no_rapid_pressure_fluctuation_confirmed).toBe(false);
    expect(added.opening_spacing_confirmed).toBe(false);
    expect(added.welded_attachment_confirmed).toBe(false);
  });

  it("JSON.stringify(project) serileştirmesinde üç beyan alanı API gövdesine taşınır", () => {
    const st = useStore.getState();
    st.updateNozzle(0, {
      no_rapid_pressure_fluctuation_confirmed: true,
      opening_spacing_confirmed: true,
      welded_attachment_confirmed: false,
    });
    const json = JSON.stringify(useStore.getState().project);
    const parsed = JSON.parse(json);
    const nz = parsed.nozzles[0];
    expect(nz.no_rapid_pressure_fluctuation_confirmed).toBe(true);
    expect(nz.opening_spacing_confirmed).toBe(true);
    expect(nz.welded_attachment_confirmed).toBe(false);
  });
});
