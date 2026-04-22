"use client";

import { use } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { ArrowLeft, Play, RefreshCw } from "lucide-react";
import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EpisodeStatusBadge } from "@/components/episodes/episode-status-badge";
import { EpisodePipeline } from "@/components/episodes/episode-pipeline";
import { AudioPlayer } from "@/components/episodes/audio-player";
import { getEpisode, generateEpisode } from "@/lib/api";
import { formatDate, formatDuration, formatCost } from "@/lib/utils";
import { useEpisodeStream } from "@/hooks/use-episode-stream";
import { toast } from "@/hooks/use-toast";

interface Props {
  params: Promise<{ id: string }>;
}

const IN_PROGRESS_STATUSES = new Set([
  "researching", "scripting", "debating", "fact_checking",
  "synthesizing", "mixing", "publishing",
]);

export default function EpisodeDetailPage({ params }: Props) {
  const { id } = use(params);
  const qc = useQueryClient();

  const { data: episode, isLoading } = useQuery({
    queryKey: ["episodes", id],
    queryFn: () => getEpisode(id),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (!status || IN_PROGRESS_STATUSES.has(status)) return 5_000;
      return false;
    },
  });

  const isActive = !!episode && IN_PROGRESS_STATUSES.has(episode.status);
  const { events, connected } = useEpisodeStream(id, isActive);

  const generate = useMutation({
    mutationFn: () => generateEpisode(id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["episodes", id] });
      toast({ title: "Episode queued for generation" });
    },
  });

  if (isLoading) return <div className="p-6 text-muted-foreground">Loading...</div>;
  if (!episode) return <div className="p-6 text-destructive">Episode not found</div>;

  const effectiveStatus = events.length > 0 && events[events.length - 1]
    ? events[events.length - 1]!.status
    : episode.status;

  return (
    <div>
      <Header title="Episode" />
      <div className="p-6 space-y-6 max-w-3xl">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" asChild>
            <Link href="/episodes">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Episodes
            </Link>
          </Button>
          {connected && (
            <Badge variant="info" className="gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-blue-600 animate-pulse" />
              Live
            </Badge>
          )}
        </div>

        <Card>
          <CardHeader className="flex flex-row items-start justify-between gap-2">
            <div>
              <CardTitle className="text-xl leading-tight">{episode.topic}</CardTitle>
              <div className="flex items-center gap-3 mt-2 flex-wrap">
                <EpisodeStatusBadge status={effectiveStatus} />
                <Badge variant="outline">{episode.format}</Badge>
                <span className="text-sm text-muted-foreground">{formatDate(episode.created_at)}</span>
              </div>
            </div>
            {(episode.status === "queued" || episode.status === "failed") && (
              <Button
                size="sm"
                onClick={() => generate.mutate()}
                disabled={generate.isPending}
              >
                {generate.isPending ? (
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Play className="h-4 w-4 mr-2" />
                )}
                {episode.status === "failed" ? "Retry" : "Generate"}
              </Button>
            )}
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-6 text-sm">
              <div>
                <p className="text-muted-foreground">Duration</p>
                <p className="font-medium">{formatDuration(episode.duration_seconds)}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Cost</p>
                <p className="font-medium">{formatCost(episode.cost_usd)}</p>
              </div>
              {episode.published_at && (
                <div>
                  <p className="text-muted-foreground">Published</p>
                  <p className="font-medium">{formatDate(episode.published_at)}</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {(isActive || events.length > 0) && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Generation Progress</CardTitle>
            </CardHeader>
            <CardContent>
              <EpisodePipeline currentStatus={effectiveStatus} events={events} />
            </CardContent>
          </Card>
        )}

        {episode.audio_url && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Audio</CardTitle>
            </CardHeader>
            <CardContent>
              <AudioPlayer src={episode.audio_url} title={episode.topic} />
            </CardContent>
          </Card>
        )}

        {episode.transcript && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Transcript</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm leading-relaxed whitespace-pre-wrap max-h-96 overflow-y-auto bg-muted rounded-md p-4 font-mono text-xs">
                {episode.transcript}
              </div>
            </CardContent>
          </Card>
        )}

        {Object.keys(episode.script).length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Script</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-xs bg-muted rounded-md p-4 overflow-auto max-h-96 whitespace-pre-wrap">
                {JSON.stringify(episode.script, null, 2)}
              </pre>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
