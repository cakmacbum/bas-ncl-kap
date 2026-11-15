// Pydantic HTTP 422 doğrulama hatalarını kullanıcı dostu Türkçe mesaja dönüştüren saf yardımcı.

export interface PydanticErrorItem {
  loc?: (string | number)[];
  msg?: string;
  type?: string;
  ctx?: Record<string, unknown>;
}

const MATERIAL_STRESS_ERRORS: Record<
  string,
  { missing: string; nonPositive: string; nonNegative: string }
> = {
  allowable_stress: {
    missing: "Malzeme için izin verilen gerilme değeri girilmemiş. Malzeme adımında değeri girin.",
    nonPositive: "Malzeme için izin verilen gerilme değeri 0 veya negatif olamaz; pozitif bir değer girin.",
    nonNegative: "Malzeme için izin verilen gerilme değeri negatif olamaz.",
  },
  yield_strength: {
    missing: "Malzeme için akma değeri girilmemiş. Malzeme adımında değeri girin.",
    nonPositive: "Malzeme için akma değeri 0 veya negatif olamaz; pozitif bir değer girin.",
    nonNegative: "Malzeme için akma değeri negatif olamaz.",
  },
  tensile_strength: {
    missing: "Malzeme için çekme değeri girilmemiş. Malzeme adımında değeri girin.",
    nonPositive: "Malzeme için çekme değeri 0 veya negatif olamaz; pozitif bir değer girin.",
    nonNegative: "Malzeme için çekme değeri negatif olamaz.",
  },
};

const COLLECTION_LABELS: Record<string, string> = {
  materials: "malzeme",
  shell_sections: "gövde",
  heads: "bombe",
  nozzles: "nozul",
  supports: "destek",
  welds: "kaynak",
  flanges: "flanş",
};

const FIELD_LABELS: Record<string, string> = {
  "design_conditions.design_pressure": "Tasarım basıncı",
  "design_conditions.design_temperature": "Tasarım sıcaklığı",
  design_pressure: "Tasarım basıncı",
  design_temperature: "Tasarım sıcaklığı",
  allowable_stress: "İzin verilen gerilme",
  yield_strength: "Akma dayanımı",
  tensile_strength: "Çekme dayanımı",
  thickness: "Kalınlık",
  nominal_thickness: "Nominal kalınlık",
  neck_thickness: "Boyun kalınlığı",
  inside_diameter: "İç çap",
  outside_diameter: "Dış çap",
  corrosion_allowance: "Korozyon payı",
  internal_corrosion_allowance: "İç korozyon payı",
  external_corrosion_allowance: "Dış korozyon payı",
};

export function formatPath(loc: (string | number)[]): string {
  const parts = loc.filter((part) => part !== "body");
  if (parts.length === 0) return "";

  // Tam yol bilinen alan sözlüğünde var mı? (ör. design_conditions.design_pressure)
  const fullKey = parts.join(".");
  if (FIELD_LABELS[fullKey]) {
    return FIELD_LABELS[fullKey];
  }

  // Segment segment işle
  const formattedSegments: string[] = [];
  for (let i = 0; i < parts.length; i++) {
    const curr = parts[i];
    const next = i + 1 < parts.length ? parts[i + 1] : undefined;

    // Dizi indeksi kontrolü
    const isNextIndex =
      next !== undefined &&
      (typeof next === "number" || (typeof next === "string" && /^\d+$/.test(next)));

    if (typeof curr === "string" && COLLECTION_LABELS[curr] && isNextIndex) {
      // Bilinen koleksiyon + indeks -> "malzeme 1", "gövde 2" vb.
      const index1 = Number(next) + 1;
      formattedSegments.push(`${COLLECTION_LABELS[curr]} ${index1}`);
      i++; // indeksi tükettik
      continue;
    }

    // Tek başına indeks mi? (bilinmeyen koleksiyon arkası veya doğrudan dizi)
    const isCurrIndex =
      typeof curr === "number" || (typeof curr === "string" && /^\d+$/.test(curr));
    if (isCurrIndex) {
      // 1 tabanlı indeks yap
      formattedSegments.push(String(Number(curr) + 1));
      continue;
    }

    // Bilinen alan adı mı?
    const currStr = String(curr);
    if (FIELD_LABELS[currStr]) {
      formattedSegments.push(FIELD_LABELS[currStr]);
    } else {
      formattedSegments.push(currStr);
    }
  }

  return formattedSegments.join(".");
}

function simplifyErrorMsg(item: PydanticErrorItem): string {
  const type = item.type ?? "";
  const rawMsg = item.msg ?? "";

  // 1. Tür (type) eşleşmesini esas al
  if (type === "missing") {
    return "Zorunlu alan eksik.";
  }
  if (type === "greater_than_equal" || type.endsWith(".not_ge")) {
    const limit = item.ctx?.ge;
    return limit != null ? `Değer en az ${limit} olmalı.` : "Değer alt sınırın üzerinde olmalı.";
  }
  if (type === "less_than_equal" || type.endsWith(".not_le")) {
    const limit = item.ctx?.le;
    return limit != null ? `Değer en çok ${limit} olmalı.` : "Değer üst sınırın altında olmalı.";
  }
  if (type === "greater_than" || type.endsWith(".not_gt")) {
    const limit = item.ctx?.gt;
    return limit != null ? `Değer ${limit} sınırından büyük olmalı.` : "Değer alt sınırın üzerinde olmalı.";
  }
  if (type === "less_than" || type.endsWith(".not_lt")) {
    const limit = item.ctx?.lt;
    return limit != null ? `Değer ${limit} sınırından küçük olmalı.` : "Değer üst sınırın altında olmalı.";
  }

  // 2. Mesaj regex'ini YALNIZ type boş/bilinmiyorsa yedek olarak kullan
  // "or equal" içeren mesajlarda gt/lt regex'i tetiklenmesin (önce "or equal" kontrolü)
  const isCustomValueError = type === "value_error" || /^Value error,\s*/i.test(rawMsg);
  if (!isCustomValueError) {
    if (/field required/i.test(rawMsg)) {
      return "Zorunlu alan eksik.";
    }
    if (/greater than or equal/i.test(rawMsg)) {
      const limit = item.ctx?.ge;
      return limit != null ? `Değer en az ${limit} olmalı.` : "Değer alt sınırın üzerinde olmalı.";
    }
    if (/less than or equal/i.test(rawMsg)) {
      const limit = item.ctx?.le;
      return limit != null ? `Değer en çok ${limit} olmalı.` : "Değer üst sınırın altında olmalı.";
    }
    if (/greater than/i.test(rawMsg)) {
      const limit = item.ctx?.gt;
      return limit != null ? `Değer ${limit} sınırından büyük olmalı.` : "Değer alt sınırın üzerinde olmalı.";
    }
    if (/less than/i.test(rawMsg)) {
      const limit = item.ctx?.lt;
      return limit != null ? `Değer ${limit} sınırından küçük olmalı.` : "Değer üst sınırın altında olmalı.";
    }
  }

  if (rawMsg) {
    return rawMsg.replace(/^Value error,\s*/i, "");
  }

  return "Geçersiz değer.";
}

function formatSingleItem(item: PydanticErrorItem): string {
  if (!item || typeof item !== "object") {
    return "Doğrulama hatası";
  }

  const loc = Array.isArray(item.loc) ? item.loc : [];
  const type = item.type ?? "";

  // Bilinen malzeme gerilmesi alanları kontrolü:
  // Özel metin YALNIZ type === "missing" ve type === "greater_than" / "greater_than_equal" için.
  const matchedField = Object.keys(MATERIAL_STRESS_ERRORS).find((field) =>
    loc.some((part) => String(part) === field)
  );

  if (matchedField) {
    if (type === "missing") {
      return MATERIAL_STRESS_ERRORS[matchedField].missing;
    }
    if (type === "greater_than") {
      const gt = item.ctx?.gt;
      if (gt === 0 || gt == null) {
        return MATERIAL_STRESS_ERRORS[matchedField].nonPositive;
      }
    }
    if (type === "greater_than_equal") {
      const ge = item.ctx?.ge;
      if (ge === 0) {
        return MATERIAL_STRESS_ERRORS[matchedField].nonNegative;
      }
    }
  }

  const path = formatPath(loc);
  const simplified = simplifyErrorMsg(item);

  return path ? `${path}: ${simplified}` : simplified;
}

export function formatValidationDetail(detail: unknown, fallback?: string): string {
  if (typeof detail === "string") {
    const trimmed = detail.trim();
    if (trimmed.length > 0) return trimmed;
    return fallback || "Doğrulama hatası (HTTP 422)";
  }

  if (Array.isArray(detail)) {
    if (detail.length === 0) {
      return fallback || "Doğrulama hatası (HTTP 422)";
    }
    const formatted = Array.from(new Set(detail.map((d) => formatSingleItem(d as PydanticErrorItem))));
    return formatted.join("\n");
  }

  if (detail && typeof detail === "object") {
    if ("loc" in detail || "msg" in detail) {
      return formatSingleItem(detail as PydanticErrorItem);
    }
    if ("message" in detail && typeof (detail as { message?: unknown }).message === "string") {
      return (detail as { message: string }).message;
    }
  }

  return fallback || "Doğrulama hatası (HTTP 422)";
}
