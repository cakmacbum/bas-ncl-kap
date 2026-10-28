// STUB (D06) — D07 dolduracak: coupling / socket_welded — B16.11 manşon
// Şimdilik şekil üretmez: null döner + CATALOG_MISS uyarısı; worker null'ı atlar.
import type { PartModule } from "../../geometryContract";
import type { Nozzle } from "../../types";

export const coupling: PartModule<Nozzle> = {
  build(params, _frame, ctx) {
    ctx.warn?.({
      partId: `nozzle:${params.tag}`,
      code: "CATALOG_MISS",
      message: "coupling parçası henüz uygulanmadı (D07)",
    });
    return null;
  },
};
