// STUB (D06) — D08 dolduracak: aşınma plakası, web, 4 kaburga, taban
// Şimdilik şekil üretmez: null döner + CATALOG_MISS uyarısı; worker null'ı atlar.
import type { PartModule } from "../../geometryContract";
import type { Support } from "../../types";

export const saddle: PartModule<Support> = {
  build(params, _frame, ctx) {
    ctx.warn?.({
      partId: `support:${params.support_id}`,
      code: "CATALOG_MISS",
      message: "saddle parçası henüz uygulanmadı (D08)",
    });
    return null;
  },
};
