import { describe, expect, it } from "vitest";
import { formatValidationDetail } from "../apiErrors";

describe("formatValidationDetail", () => {
  it("bilinen alan: allowable_stress greater_than için 0 veya negatif yönlendirmesi", () => {
    const detail = [
      {
        loc: ["body", "materials", 0, "allowable_stress"],
        msg: "Input should be greater than 0",
        type: "greater_than",
        ctx: { gt: 0 },
      },
    ];
    const res = formatValidationDetail(detail);
    expect(res).toBe("Malzeme için izin verilen gerilme değeri 0 veya negatif olamaz; pozitif bir değer girin.");
  });

  it("bilinen alan: allowable_stress missing için eksik yönlendirmesi", () => {
    const detail = [
      {
        loc: ["body", "materials", 0, "allowable_stress"],
        msg: "Field required",
        type: "missing",
      },
    ];
    const res = formatValidationDetail(detail);
    expect(res).toBe("Malzeme için izin verilen gerilme değeri girilmemiş. Malzeme adımında değeri girin.");
  });

  it("bilinen alan: allowable_stress tip hatasında genel mesaja düşer", () => {
    const detail = [
      {
        loc: ["body", "materials", 0, "allowable_stress"],
        msg: "Input should be a valid number",
        type: "string_type",
      },
    ];
    const res = formatValidationDetail(detail);
    expect(res).toBe("malzeme 1.İzin verilen gerilme: Input should be a valid number");
  });

  it("bilinen alan: yield_strength greater_than ve missing için farklı metinler", () => {
    const detailGt = [
      {
        loc: ["body", "materials", 0, "yield_strength"],
        msg: "Input should be greater than 0",
        type: "greater_than",
      },
    ];
    expect(formatValidationDetail(detailGt)).toBe(
      "Malzeme için akma değeri 0 veya negatif olamaz; pozitif bir değer girin."
    );

    const detailMissing = [
      {
        loc: ["body", "materials", 0, "yield_strength"],
        msg: "Field required",
        type: "missing",
      },
    ];
    expect(formatValidationDetail(detailMissing)).toBe(
      "Malzeme için akma değeri girilmemiş. Malzeme adımında değeri girin."
    );
  });

  it("bilinen alan: tensile_strength greater_than ve missing için farklı metinler", () => {
    const detailGt = [
      {
        loc: ["body", "materials", 0, "tensile_strength"],
        msg: "Input should be greater than 0",
        type: "greater_than",
      },
    ];
    expect(formatValidationDetail(detailGt)).toBe(
      "Malzeme için çekme değeri 0 veya negatif olamaz; pozitif bir değer girin."
    );

    const detailMissing = [
      {
        loc: ["body", "materials", 0, "tensile_strength"],
        msg: "Field required",
        type: "missing",
      },
    ];
    expect(formatValidationDetail(detailMissing)).toBe(
      "Malzeme için çekme değeri girilmemiş. Malzeme adımında değeri girin."
    );
  });

  it("bilinen alan sözlüğü: design_conditions.design_pressure Türkçe etiket ile gösterilir", () => {
    const detail = [
      {
        loc: ["body", "design_conditions", "design_pressure"],
        msg: "Input should be greater than 0",
        type: "greater_than",
        ctx: { gt: 0 },
      },
    ];
    const res = formatValidationDetail(detail);
    expect(res).toContain("Tasarım basıncı");
    expect(res).toContain("büyük olmalı");
    expect(res).toBe("Tasarım basıncı: Değer 0 sınırından büyük olmalı.");
    expect(res).not.toContain('{"');
    expect(res).not.toContain("}");
  });

  it("ctx yokken uydurma sınır yazılmaz", () => {
    const detail = [
      {
        loc: ["body", "design_conditions", "design_pressure"],
        msg: "Input should be greater than 0",
        type: "greater_than",
      },
    ];
    const res = formatValidationDetail(detail);
    expect(res).toBe("Tasarım basıncı: Değer alt sınırın üzerinde olmalı.");
    expect(res).not.toContain("0");
  });

  it("dizi indeksleri 1 tabanlı gösterilir ve bilinen/bilinmeyen yollar düzgün biçimlendirilir", () => {
    const knownColl = [
      {
        loc: ["body", "shell_sections", 0, "inside_diameter"],
        msg: "Field required",
        type: "missing",
      },
    ];
    expect(formatValidationDetail(knownColl)).toBe("gövde 1.İç çap: Zorunlu alan eksik.");

    const unknownColl = [
      {
        loc: ["body", "custom_items", 0, "foo"],
        msg: "Field required",
        type: "missing",
      },
    ];
    expect(formatValidationDetail(unknownColl)).toBe("custom_items.1.foo: Zorunlu alan eksik.");
  });

  it("bilinmeyen alan: alan yolu ve sadeleştirilmiş mesaj gösterilir, ham JSON basılmaz", () => {
    const detail = [
      {
        loc: ["body", "custom_module", "setting"],
        msg: "Input should be greater than 10",
        type: "greater_than",
        ctx: { gt: 10 },
      },
    ];
    const res = formatValidationDetail(detail);
    expect(res).toBe("custom_module.setting: Değer 10 sınırından büyük olmalı.");
    expect(res).not.toContain('{"');
    expect(res).not.toContain("}");
  });

  it("bilinmeyen zorunlu alan: missing için sadeleştirilmiş mesaj", () => {
    const detail = [
      {
        loc: ["body", "project_name"],
        msg: "Field required",
        type: "missing",
      },
    ];
    const res = formatValidationDetail(detail);
    expect(res).toBe("project_name: Zorunlu alan eksik.");
  });

  it("detail string olduğunda doğrudan döndürülür", () => {
    const text = "Özel sunucu doğrulama hatası";
    expect(formatValidationDetail(text)).toBe(text);
  });

  it("gövde JSON değilken veya detail boşken fallback kullanılır", () => {
    expect(formatValidationDetail(undefined, "Unprocessable Entity")).toBe("Unprocessable Entity");
    expect(formatValidationDetail(null, "Unprocessable Entity")).toBe("Unprocessable Entity");
    expect(formatValidationDetail([], "Fallback")).toBe("Fallback");
  });

  it("birden fazla hata olduğunda satır satır birleştirilir", () => {
    const detail = [
      {
        loc: ["body", "materials", 0, "allowable_stress"],
        msg: "Input should be greater than 0",
        type: "greater_than",
      },
      {
        loc: ["body", "materials", 0, "yield_strength"],
        msg: "Input should be greater than 0",
        type: "greater_than",
      },
    ];
    const res = formatValidationDetail(detail);
    const lines = res.split("\n");
    expect(lines).toHaveLength(2);
    expect(lines[0]).toContain("izin verilen gerilme");
    expect(lines[1]).toContain("akma");
  });

  it("greater_than_equal ctx.ge=5 için en az <ge> sınırını gösterir", () => {
    const detail = [
      {
        loc: ["body", "design_conditions", "design_pressure"],
        msg: "Input should be greater than or equal to 5",
        type: "greater_than_equal",
        ctx: { ge: 5 },
      },
    ];
    const res = formatValidationDetail(detail);
    expect(res).toBe("Tasarım basıncı: Değer en az 5 olmalı.");
  });

  it("less_than_equal ctx.le=100 için en çok <le> sınırını gösterir", () => {
    const detail = [
      {
        loc: ["body", "design_conditions", "design_temperature"],
        msg: "Input should be less than or equal to 100",
        type: "less_than_equal",
        ctx: { le: 100 },
      },
    ];
    const res = formatValidationDetail(detail);
    expect(res).toBe("Tasarım sıcaklığı: Değer en çok 100 olmalı.");
  });

  it("ctx'siz ge ve le durumlarında genel sınır ifadesi kullanılır", () => {
    const detailGe = [
      {
        loc: ["body", "design_conditions", "design_pressure"],
        msg: "Input should be greater than or equal to 5",
        type: "greater_than_equal",
      },
    ];
    expect(formatValidationDetail(detailGe)).toBe("Tasarım basıncı: Değer alt sınırın üzerinde olmalı.");

    const detailLe = [
      {
        loc: ["body", "design_conditions", "design_temperature"],
        msg: "Input should be less than or equal to 100",
        type: "less_than_equal",
      },
    ];
    expect(formatValidationDetail(detailLe)).toBe("Tasarım sıcaklığı: Değer üst sınırın altında olmalı.");
  });

  it("malzeme alanında type=value_error ('greater than' geçen mesajla) genel mesaja düşer", () => {
    const detail = [
      {
        loc: ["body", "materials", 0, "allowable_stress"],
        msg: "Value error, allowable_stress must be greater than yield_strength",
        type: "value_error",
      },
    ];
    const res = formatValidationDetail(detail);
    expect(res).toBe("malzeme 1.İzin verilen gerilme: allowable_stress must be greater than yield_strength");
  });

  it("malzeme alanında greater_than_equal ctx.ge=0 için negatif olamaz yönlendirmesi", () => {
    const detail = [
      {
        loc: ["body", "materials", 0, "allowable_stress"],
        msg: "Input should be greater than or equal to 0",
        type: "greater_than_equal",
        ctx: { ge: 0 },
      },
    ];
    const res = formatValidationDetail(detail);
    expect(res).toBe("Malzeme için izin verilen gerilme değeri negatif olamaz.");
    expect(res).toContain("negatif olamaz");
    expect(res).not.toContain("0 veya negatif");

    const detailYield = [
      {
        loc: ["body", "materials", 0, "yield_strength"],
        msg: "Input should be greater than or equal to 0",
        type: "greater_than_equal",
        ctx: { ge: 0 },
      },
    ];
    expect(formatValidationDetail(detailYield)).toBe("Malzeme için akma değeri negatif olamaz.");
  });

  it("malzeme alanında greater_than_equal ctx.ge > 0 için en az <ge> genel metni kullanılır", () => {
    const detail = [
      {
        loc: ["body", "materials", 0, "allowable_stress"],
        msg: "Input should be greater than or equal to 5",
        type: "greater_than_equal",
        ctx: { ge: 5 },
      },
    ];
    const res = formatValidationDetail(detail);
    expect(res).toBe("malzeme 1.İzin verilen gerilme: Değer en az 5 olmalı.");
  });

  it("type boşken mesaj regex yedeğinde or equal önceliklidir", () => {
    const detailGe = [
      {
        loc: ["body", "design_conditions", "design_pressure"],
        msg: "Input should be greater than or equal to 5",
        ctx: { ge: 5 },
      },
    ];
    expect(formatValidationDetail(detailGe)).toBe("Tasarım basıncı: Değer en az 5 olmalı.");

    const detailLe = [
      {
        loc: ["body", "design_conditions", "design_temperature"],
        msg: "Input should be less than or equal to 100",
        ctx: { le: 100 },
      },
    ];
    expect(formatValidationDetail(detailLe)).toBe("Tasarım sıcaklığı: Değer en çok 100 olmalı.");
  });
});
