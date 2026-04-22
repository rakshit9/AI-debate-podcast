"use client";

import { CheckCircle2, Circle, Loader2, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import type { EpisodeStatus, EpisodeProgressEvent } from "@/types/api";

const STAGES: { status: EpisodeStatus; label: string }[] = [
  { status: "researching", label: "Research" },
  { status: "scripting", label: "Script" },
  { status: "debating", label: "Debate" },
  { status: "fact_checking", label: "Fact Check" },
  { status: "synthesizing", label: "Synthesize" },
  { status: "mixing", label: "Mix" },
  { status: "publishing", label: "Publish" },
];

const ORDER: EpisodeStatus[] = [
  "queued",
  "researching",
  "scripting",
  "debating",
  "fact_checking",
  "synthesizing",
  "mixing",
  "publishing",
  "completed",
  "failed",
];

function stageIndex(status: EpisodeStatus) {
  return ORDER.indexOf(status);
}

interface Props {
  currentStatus: EpisodeStatus;
  events: EpisodeProgressEvent[];
}

export function EpisodePipeline({ currentStatus, events }: Props) {
  const currentIdx = stageIndex(currentStatus);
  const failed = currentStatus === "failed";

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-1 flex-wrap">
        {STAGES.map(({ status, label }, i) => {
          const idx = stageIndex(status);
          const done = !failed && currentIdx > idx;
          const active = currentIdx === idx && !failed;
          const isFailed = failed && currentIdx === idx;

          return (
            <div key={status} className="flex items-center gap-1">
              <div
                className={cn(
                  "flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium",
                  done && "bg-green-100 text-green-800",
                  active && "bg-blue-100 text-blue-800",
                  isFailed && "bg-red-100 text-red-800",
                  !done && !active && !isFailed && "bg-muted text-muted-foreground",
                )}
              >
                {done ? (
                  <CheckCircle2 className="h-3 w-3" />
                ) : active ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : isFailed ? (
                  <XCircle className="h-3 w-3" />
                ) : (
                  <Circle className="h-3 w-3" />
                )}
                {label}
              </div>
              {i < STAGES.length - 1 && (
                <div className={cn("h-px w-3 bg-border", done && "bg-green-300")} />
              )}
            </div>
          );
        })}
      </div>

      {events.length > 0 && (
        <div className="bg-muted rounded-md p-3 max-h-40 overflow-y-auto space-y-1">
          {events.slice(-20).map((ev, i) => (
            <p key={i} className="text-xs text-muted-foreground font-mono">
              <span className="text-foreground/60">[{ev.node}]</span> {ev.message}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
