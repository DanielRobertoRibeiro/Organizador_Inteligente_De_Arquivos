import projectConfig from "../../config.example.json";
import type { CategoryRule, WebPlanItem } from "./types";

const CATEGORY_TONES: Record<string, CategoryRule["tone"]> = {
  Imagens: "lime",
  Documentos: "blue",
  Planilhas: "orange",
  Compactados: "violet",
  Código: "neutral",
};

export const DEFAULT_RULES: readonly CategoryRule[] = Object.entries(projectConfig.categories).map(
  ([name, extensions]) => ({
    name,
    extensions,
    tone: CATEGORY_TONES[name] ?? "neutral",
  }),
);

export const DEFAULT_CATEGORY = projectConfig.default_category;

export function extensionOf(filename: string): string {
  const cleanName = filename.split(/[\\/]/).at(-1) ?? filename;
  const dot = cleanName.lastIndexOf(".");
  return dot <= 0 ? "" : cleanName.slice(dot).toLocaleLowerCase("pt-BR");
}

export function classifyFilename(
  filename: string,
  rules: readonly CategoryRule[] = DEFAULT_RULES,
  fallback = DEFAULT_CATEGORY,
): string {
  const extension = extensionOf(filename);
  return rules.find((rule) => rule.extensions.includes(extension))?.name ?? fallback;
}

export function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const value = bytes / 1024 ** index;
  return `${value >= 10 || index === 0 ? value.toFixed(0) : value.toFixed(1)} ${units[index]}`;
}

async function sha256(file: File): Promise<string> {
  const buffer = await file.arrayBuffer();
  const digest = await crypto.subtle.digest("SHA-256", buffer);
  return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
}

function sourcePath(file: File): string {
  const relativePath = (file as File & { webkitRelativePath?: string }).webkitRelativePath;
  return relativePath || file.name;
}

function splitFilename(filename: string): { stem: string; suffix: string } {
  const dot = filename.lastIndexOf(".");
  if (dot <= 0) return { stem: filename, suffix: "" };
  return { stem: filename.slice(0, dot), suffix: filename.slice(dot) };
}

function uniqueFilename(filename: string, category: string, occupied: Set<string>): string {
  const { stem, suffix } = splitFilename(filename);
  let candidate = filename;
  let counter = 1;
  while (occupied.has(`${category}/${candidate}`.toLocaleLowerCase("pt-BR"))) {
    candidate = `${stem} (${counter})${suffix}`;
    counter += 1;
  }
  occupied.add(`${category}/${candidate}`.toLocaleLowerCase("pt-BR"));
  return candidate;
}

export async function buildPlan(
  incomingFiles: readonly File[],
  rules: readonly CategoryRule[] = DEFAULT_RULES,
): Promise<WebPlanItem[]> {
  const files = [...incomingFiles].sort((left, right) =>
    sourcePath(left).localeCompare(sourcePath(right), "pt-BR", { sensitivity: "base" }),
  );
  const hashes = await Promise.all(files.map(sha256));
  const firstByHash = new Map<string, string>();
  const occupied = new Set<string>();

  return files.map((file, index) => {
    const hash = hashes[index];
    const firstSource = firstByHash.get(hash);
    const category = classifyFilename(file.name, rules);
    const source = sourcePath(file);

    if (firstSource) {
      return {
        id: `${index}-${file.name}-${file.lastModified}`,
        source,
        filename: file.name,
        target: `Arquivos organizados/${category}/${file.name}`,
        category,
        size: file.size,
        action: "skip",
        status: "duplicate",
        sha256: hash,
        message: `Mesmo conteúdo de ${firstSource}`,
      };
    }

    firstByHash.set(hash, source);
    const targetName = uniqueFilename(file.name, category, occupied);
    return {
      id: `${index}-${file.name}-${file.lastModified}`,
      source,
      filename: file.name,
      target: `Arquivos organizados/${category}/${targetName}`,
      category,
      size: file.size,
      action: "move",
      status: "planned",
      sha256: hash,
      message: "Simulação — nenhuma alteração realizada",
    };
  });
}

function csvCell(value: string | number): string {
  const normalized = String(value).replaceAll('"', '""');
  return `"${normalized}"`;
}

export function planToCsv(items: readonly WebPlanItem[]): string {
  const timestamp = new Date().toISOString();
  const header = ["timestamp", "source", "target", "category", "action", "status", "sha256", "message"];
  const rows = items.map((item) =>
    [timestamp, item.source, item.target, item.category, item.action, item.status, item.sha256, item.message]
      .map(csvCell)
      .join(","),
  );
  return [header.join(","), ...rows].join("\r\n");
}
