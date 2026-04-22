"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { Plus, Trash2, Mic2 } from "lucide-react";
import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { listHosts, deleteHost } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import { toast } from "@/hooks/use-toast";

export default function HostsPage() {
  const qc = useQueryClient();
  const { data: hosts = [], isLoading } = useQuery({ queryKey: ["hosts"], queryFn: listHosts });

  const del = useMutation({
    mutationFn: deleteHost,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["hosts"] });
      toast({ title: "Host deleted" });
    },
  });

  return (
    <div>
      <Header title="Hosts" />
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <p className="text-sm text-muted-foreground">{hosts.length} hosts</p>
          <Button asChild>
            <Link href="/hosts/new">
              <Plus className="h-4 w-4 mr-2" />
              New Host
            </Link>
          </Button>
        </div>

        {isLoading ? (
          <p className="text-muted-foreground text-sm">Loading...</p>
        ) : hosts.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <Mic2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="font-medium">No hosts yet</p>
              <p className="text-sm text-muted-foreground mt-1 mb-4">
                Create AI host personalities for your shows
              </p>
              <Button asChild>
                <Link href="/hosts/new">Create Host</Link>
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {hosts.map((host) => (
              <Card key={host.id} className="hover:border-primary/40 transition-colors">
                <CardHeader className="flex flex-row items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                        <Mic2 className="h-4 w-4 text-primary" />
                      </div>
                      <CardTitle className="text-base truncate">{host.name}</CardTitle>
                    </div>
                    <CardDescription className="mt-2 line-clamp-2 text-xs">
                      {host.personality_prompt}
                    </CardDescription>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="shrink-0 text-muted-foreground hover:text-destructive"
                    onClick={() => del.mutate(host.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </CardHeader>
                <CardContent className="flex items-center gap-2 flex-wrap">
                  <Badge variant="outline">{host.voice_provider}</Badge>
                  <Badge variant="secondary">temp: {host.temperature}</Badge>
                  <span className="text-xs text-muted-foreground ml-auto">{formatDate(host.created_at)}</span>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
