// STUB (D06) — D07 dolduracak: flanged / slip_on / pad_reinforced — boru + B16.5 flanş (+ ped)
// Şimdilik şekil üretmez: null döner + CATALOG_MISS uyarısı; worker null'ı atlar.
import type { PartModule } from "../../geometryContract";
import type { Nozzle } from "../../types";

export const flangedNozzle: PartModule<Nozzle> = {
  build(params, _frame, ctx) {
    ctx.warn?.({
      partId: `nozzle:${params.tag}`,
      code: "CATALOG_MISS",
      message: "flangedNozzle parçası henüz uygulanmadı (D07)",
    });
    return null;
  },
};
