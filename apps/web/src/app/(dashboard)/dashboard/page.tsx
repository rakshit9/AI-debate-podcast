"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Radio, FileAudio, Mic2, TrendingUp, Plus } from "lucide-react";
import { Header } from "@/components/layout/header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { listEpisodes, listShows, listHosts } from "@/lib/api";
import { formatDate, formatCost } from "@/lib/utils";
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

export default function DashboardPage() {
  const { data: episodes = [] } = useQuery({ queryKey: ["episodes"], queryFn: listEpisodes });
  const { data: shows = [] } = useQuery({ queryKey: ["shows"], queryFn: listShows });
  const { data: hosts = [] } = useQuery({ queryKey: ["hosts"], queryFn: listHosts });

  const totalCost = episodes.reduce((sum, e) => sum + parseFloat(e.cost_usd), 0);
  const completed = episodes.filter((e) => e.status === "completed").length;
  const inProgress = episodes.filter(
    (e) => !["completed", "failed", "queued"].includes(e.status),
  ).length;

  const stats = [
    { label: "Shows", value: shows.length, icon: Radio, href: "/shows" },
    { label: "Episodes", value: episodes.length, icon: FileAudio, href: "/episodes" },
    { label: "Hosts", value: hosts.length, icon: Mic2, href: "/hosts" },
    { label: "Total Cost", value: `$${totalCost.toFixed(2)}`, icon: TrendingUp, href: "/episodes" },
  ];

  const recent = [...episodes]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5);

  return (
    <div>
      <Header title="Dashboard" />
      <div className="p-6 space-y-6">
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {stats.map(({ label, value, icon: Icon, href }) => (
            <Link key={label} href={href}>
              <Card className="hover:border-primary/40 transition-colors cursor-pointer">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">{label}</CardTitle>
                  <Icon className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{value}</div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Recent Episodes</CardTitle>
                <CardDescription>
                  {completed} completed · {inProgress} in progress
                </CardDescription>
              </div>
              <Button asChild size="sm">
                <Link href="/episodes/new">
                  <Plus className="h-4 w-4 mr-1" />
                  New
                </Link>
              </Button>
            </CardHeader>
            <CardContent>
              {recent.length === 0 ? (
                <p className="text-sm text-muted-foreground py-4 text-center">No episodes yet</p>
              ) : (
                <ul className="space-y-3">
                  {recent.map((ep) => (
                    <li key={ep.id} className="flex items-center justify-between gap-2">
                      <Link
                        href={`/episodes/${ep.id}`}
                        className="text-sm font-medium hover:underline truncate flex-1"
                      >
                        {ep.topic}
                      </Link>
                      <Badge variant={STATUS_VARIANT[ep.status]}>{ep.status}</Badge>
                      <span className="text-xs text-muted-foreground whitespace-nowrap">
                        {formatDate(ep.created_at)}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Shows</CardTitle>
                <CardDescription>{shows.length} podcast shows</CardDescription>
              </div>
              <Button asChild size="sm">
                <Link href="/shows/new">
                  <Plus className="h-4 w-4 mr-1" />
                  New
                </Link>
              </Button>
            </CardHeader>
            <CardContent>
              {shows.length === 0 ? (
                <p className="text-sm text-muted-foreground py-4 text-center">No shows yet</p>
              ) : (
                <ul className="space-y-3">
                  {shows.map((show) => (
                    <li key={show.id} className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                        <Radio className="h-4 w-4 text-primary" />
                      </div>
                      <Link
                        href={`/shows/${show.id}`}
                        className="text-sm font-medium hover:underline flex-1 truncate"
                      >
                        {show.name}
                      </Link>
                      <Badge variant="outline">{show.default_format}</Badge>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Cost Summary</CardTitle>
            <CardDescription>Episode generation costs</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-8">
              <div>
                <p className="text-sm text-muted-foreground">Total spent</p>
                <p className="text-2xl font-bold">{formatCost(totalCost.toString())}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Avg per episode</p>
                <p className="text-2xl font-bold">
                  {episodes.length > 0
                    ? formatCost((totalCost / episodes.length).toString())
                    : "$0.00"}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Episodes completed</p>
                <p className="text-2xl font-bold">{completed}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
