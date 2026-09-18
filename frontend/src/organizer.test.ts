import { describe, expect, it } from "vitest";
import { buildPlan, classifyFilename, extensionOf, planToCsv } from "./organizer";

describe("classificação", () => {
  it("ignora maiúsculas e usa fallback", () => {
    expect(classifyFilename("FOTO.PNG")).toBe("Imagens");
    expect(classifyFilename("arquivo.sem-regra")).toBe("Outros");
    expect(extensionOf(".gitignore")).toBe("");
  });
});

describe("planejamento web", () => {
  it("sinaliza conteúdo duplicado e resolve nomes repetidos", async () => {
    const files = [
      new File(["mesmo"], "a.txt", { lastModified: 1 }),
      new File(["mesmo"], "copia.txt", { lastModified: 2 }),
      new File(["outro"], "a.txt", { lastModified: 3 }),
    ];

    const plan = await buildPlan(files);

    expect(plan.map((item) => item.status)).toEqual(["planned", "planned", "duplicate"]);
    expect(plan[1].target).toContain("a (1).txt");
    expect(plan[2].message).toContain("a.txt");
  });

  it("exporta o contrato CSV esperado", async () => {
    const plan = await buildPlan([new File(["conteúdo"], "nota.txt")]);
    const csv = planToCsv(plan);

    expect(csv.split("\r\n")[0]).toBe("timestamp,source,target,category,action,status,sha256,message");
    expect(csv).toContain('"Documentos"');
  });
});
