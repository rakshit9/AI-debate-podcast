import { Badge } from "@/components/ui/badge";
import type { BadgeProps } from "@/components/ui/badge";
import type { EpisodeStatus } from "@/types/api";

const VARIANT_MAP: Record<EpisodeStatus, BadgeProps["variant"]> = {
  queued: "secondary",
  researching: "info",
  scripting: "info",
  debating: "info",
  fact_checking: "warning",
  synthesizing: "warning",
  mixing: "warning",
  publishing: "warning",
  completed: "success",
  failed: "destructive",
};

const LABEL_MAP: Record<EpisodeStatus, string> = {
  queued: "Queued",
  researching: "Researching",
  scripting: "Scripting",
  debating: "Debating",
  fact_checking: "Fact Checking",
  synthesizing: "Synthesizing",
  mixing: "Mixing",
  publishing: "Publishing",
  completed: "Completed",
  failed: "Failed",
};

export function EpisodeStatusBadge({ status }: { status: EpisodeStatus }) {
  return <Badge variant={VARIANT_MAP[status]}>{LABEL_MAP[status]}</Badge>;
}
