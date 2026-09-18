export type PlanStatus = "planned" | "duplicate" | "skipped";

export interface CategoryRule {
  name: string;
  extensions: readonly string[];
  tone: "lime" | "blue" | "orange" | "violet" | "neutral";
}

export interface WebPlanItem {
  id: string;
  source: string;
  filename: string;
  target: string;
  category: string;
  size: number;
  action: "move" | "skip";
  status: PlanStatus;
  sha256: string;
  message: string;
}
