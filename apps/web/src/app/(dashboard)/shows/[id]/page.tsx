"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { ArrowLeft, Plus, FileAudio } from "lucide-react";
import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getShow, listEpisodes } from "@/lib/api";
import { formatDate, formatDuration, formatCost } from "@/lib/utils";
import type { EpisodeStatus } from "@/types/api";

const STATUS_VARIANT: Record<EpisodeStatus, "default" | "secondary" | "success" | "warning" | "info" | "destructive" | "outline"> = {
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

interface Props {
  params: Promise<{ id: string }>;
}

export default function ShowDetailPage({ params }: Props) {
  const resolvedParams = use(params);
  const { data: show, isLoading } = useQuery({
    queryKey: ["shows", resolvedParams.id],
    queryFn: () => getShow(resolvedParams.id),
  });

  const { data: allEpisodes = [] } = useQuery({ queryKey: ["episodes"], queryFn: listEpisodes });
  const episodes = allEpisodes.filter((e) => e.show_id === resolvedParams.id);

  if (isLoading) return <div className="p-6 text-muted-foreground">Loading...</div>;
  if (!show) return <div className="p-6 text-destructive">Show not found</div>;

  return (
    <div>
      <Header title={show.name} />
      <div className="p-6 space-y-6 max-w-3xl">
        <Button variant="ghost" size="sm" asChild>
          <Link href="/shows">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Shows
          </Link>
        </Button>

        <Card>
          <CardHeader>
            <CardTitle>{show.name}</CardTitle>
            <CardDescription>{show.description || "No description"}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex gap-4 flex-wrap text-sm">
              <span>
                <span className="text-muted-foreground">Format: </span>
                <Badge variant="outline">{show.default_format}</Badge>
              </span>
              <span>
                <span className="text-muted-foreground">Created: </span>
                {formatDate(show.created_at)}
              </span>
              {show.rss_feed_url && (
                <span>
                  <span className="text-muted-foreground">RSS: </span>
                  <a href={show.rss_feed_url} className="text-primary underline underline-offset-4" target="_blank" rel="noreferrer">
                    Feed
                  </a>
                </span>
              )}
            </div>
            {show.style_guide && (
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">Style Guide</p>
                <p className="text-sm bg-muted rounded-md p-3">{show.style_guide}</p>
              </div>
            )}
          </CardContent>
        </Card>

        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold">Episodes ({episodes.length})</h2>
            <Button asChild size="sm">
              <Link href={`/episodes/new?show_id=${show.id}`}>
                <Plus className="h-4 w-4 mr-2" />
                New Episode
              </Link>
            </Button>
          </div>
          {episodes.length === 0 ? (
            <Card className="text-center py-8">
              <CardContent>
                <FileAudio className="h-10 w-10 text-muted-foreground mx-auto mb-3" />
                <p className="text-sm text-muted-foreground">No episodes for this show yet</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-2">
              {episodes.map((ep) => (
                <Link key={ep.id} href={`/episodes/${ep.id}`}>
                  <Card className="hover:border-primary/40 transition-colors">
                    <CardContent className="flex items-center justify-between py-4">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{ep.topic}</p>
                        <p className="text-xs text-muted-foreground">
                          {formatDate(ep.created_at)} · {formatDuration(ep.duration_seconds)} · {formatCost(ep.cost_usd)}
                        </p>
                      </div>
                      <Badge variant={STATUS_VARIANT[ep.status]}>{ep.status}</Badge>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

import { use } from "react";
