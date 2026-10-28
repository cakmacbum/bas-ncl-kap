// STUB (D06) — D08 dolduracak: ayaklar (boru/profil) + ped + taban plakası
// Şimdilik şekil üretmez: null döner + CATALOG_MISS uyarısı; worker null'ı atlar.
import type { PartModule } from "../../geometryContract";
import type { Support } from "../../types";

export const legs: PartModule<Support> = {
  build(params, _frame, ctx) {
    ctx.warn?.({
      partId: `support:${params.support_id}`,
      code: "CATALOG_MISS",
      message: "legs parçası henüz uygulanmadı (D08)",
    });
    return null;
  },
};
