"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { Plus, Trash2, FileAudio } from "lucide-react";
import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { EpisodeStatusBadge } from "@/components/episodes/episode-status-badge";
import { listEpisodes, deleteEpisode } from "@/lib/api";
import { formatDate, formatDuration, formatCost } from "@/lib/utils";
import { toast } from "@/hooks/use-toast";
import type { EpisodeStatus } from "@/types/api";
import { Badge } from "@/components/ui/badge";

const ALL_STATUSES: EpisodeStatus[] = [
  "queued", "researching", "scripting", "debating", "fact_checking",
  "synthesizing", "mixing", "publishing", "completed", "failed",
];

export default function EpisodesPage() {
  const qc = useQueryClient();
  const [filter, setFilter] = useState<EpisodeStatus | "all">("all");

  const { data: episodes = [], isLoading } = useQuery({
    queryKey: ["episodes"],
    queryFn: listEpisodes,
    refetchInterval: 10_000,
  });

  const del = useMutation({
    mutationFn: deleteEpisode,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["episodes"] });
      toast({ title: "Episode deleted" });
    },
  });

  const filtered = filter === "all" ? episodes : episodes.filter((e) => e.status === filter);

  return (
    <div>
      <Header title="Episodes" />
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <p className="text-sm text-muted-foreground">{filtered.length} episodes</p>
          <Button asChild>
            <Link href="/episodes/new">
              <Plus className="h-4 w-4 mr-2" />
              New Episode
            </Link>
          </Button>
        </div>

        <div className="flex gap-2 flex-wrap mb-6">
          <button
            onClick={() => setFilter("all")}
            className={`text-xs rounded-full px-3 py-1 border transition-colors ${
              filter === "all" ? "bg-primary text-primary-foreground border-primary" : "bg-background border-border hover:bg-accent"
            }`}
          >
            All ({episodes.length})
          </button>
          {ALL_STATUSES.map((s) => {
            const count = episodes.filter((e) => e.status === s).length;
            if (count === 0) return null;
            return (
              <button
                key={s}
                onClick={() => setFilter(s)}
                className={`text-xs rounded-full px-3 py-1 border transition-colors ${
                  filter === s ? "bg-primary text-primary-foreground border-primary" : "bg-background border-border hover:bg-accent"
                }`}
              >
                {s} ({count})
              </button>
            );
          })}
        </div>

        {isLoading ? (
          <p className="text-muted-foreground text-sm">Loading...</p>
        ) : filtered.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <FileAudio className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="font-medium">No episodes yet</p>
              <p className="text-sm text-muted-foreground mt-1 mb-4">
                Generate your first AI podcast episode
              </p>
              <Button asChild>
                <Link href="/episodes/new">New Episode</Link>
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-2">
            {filtered.map((ep) => (
              <Card key={ep.id} className="hover:border-primary/40 transition-colors">
                <CardContent className="flex items-center gap-4 py-4">
                  <div className="flex-1 min-w-0">
                    <Link href={`/episodes/${ep.id}`} className="text-sm font-medium hover:underline block truncate">
                      {ep.topic}
                    </Link>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {formatDate(ep.created_at)}
                      {ep.duration_seconds ? ` · ${formatDuration(ep.duration_seconds)}` : ""}
                      {` · ${formatCost(ep.cost_usd)}`}
                    </p>
                  </div>
                  <Badge variant="outline">{ep.format}</Badge>
                  <EpisodeStatusBadge status={ep.status} />
                  <Button
                    variant="ghost"
                    size="icon"
                    className="shrink-0 text-muted-foreground hover:text-destructive"
                    onClick={() => del.mutate(ep.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
