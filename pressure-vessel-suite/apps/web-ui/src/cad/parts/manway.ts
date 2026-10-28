// STUB (D06) — D07 dolduracak: boyun + B16.5 flanş + kör kapak + saplama/somun + davit
// Şimdilik şekil üretmez: null döner + CATALOG_MISS uyarısı; worker null'ı atlar.
import type { PartModule } from "../../geometryContract";
import type { Nozzle } from "../../types";

export const manway: PartModule<Nozzle> = {
  build(params, _frame, ctx) {
    ctx.warn?.({
      partId: `nozzle:${params.tag}`,
      code: "CATALOG_MISS",
      message: "manway parçası henüz uygulanmadı (D07)",
    });
    return null;
  },
};
