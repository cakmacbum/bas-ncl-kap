// STUB (D06) — D07 dolduracak: (host dış yüzey ⊕ t_pad) ∩ silindir(pad_od) − silindir(OD); flangedNozzle çağırır, ayrı varlık değil
// Şimdilik şekil üretmez: null döner + CATALOG_MISS uyarısı; worker null'ı atlar.
import type { PartModule } from "../../geometryContract";
import type { Nozzle } from "../../types";

export const pad: PartModule<Nozzle> = {
  build(params, _frame, ctx) {
    ctx.warn?.({
      partId: `nozzle:${params.tag}`,
      code: "CATALOG_MISS",
      message: "pad parçası henüz uygulanmadı (D07)",
    });
    return null;
  },
};
