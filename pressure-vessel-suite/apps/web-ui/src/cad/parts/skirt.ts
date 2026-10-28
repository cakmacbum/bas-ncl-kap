// STUB (D06) — D08 dolduracak: etek + taban halkası + ankraj delikleri
// Şimdilik şekil üretmez: null döner + CATALOG_MISS uyarısı; worker null'ı atlar.
import type { PartModule } from "../../geometryContract";
import type { Support } from "../../types";

export const skirt: PartModule<Support> = {
  build(params, _frame, ctx) {
    ctx.warn?.({
      partId: `support:${params.support_id}`,
      code: "CATALOG_MISS",
      message: "skirt parçası henüz uygulanmadı (D08)",
    });
    return null;
  },
};
