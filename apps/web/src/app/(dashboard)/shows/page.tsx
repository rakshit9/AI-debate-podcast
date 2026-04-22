"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { Plus, Trash2, Radio } from "lucide-react";
import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { listShows, deleteShow } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import { toast } from "@/hooks/use-toast";

export default function ShowsPage() {
  const qc = useQueryClient();
  const { data: shows = [], isLoading } = useQuery({ queryKey: ["shows"], queryFn: listShows });

  const del = useMutation({
    mutationFn: deleteShow,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["shows"] });
      toast({ title: "Show deleted" });
    },
  });

  return (
    <div>
      <Header title="Shows" />
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <p className="text-sm text-muted-foreground">{shows.length} shows</p>
          <Button asChild>
            <Link href="/shows/new">
              <Plus className="h-4 w-4 mr-2" />
              New Show
            </Link>
          </Button>
        </div>

        {isLoading ? (
          <p className="text-muted-foreground text-sm">Loading...</p>
        ) : shows.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <Radio className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="font-medium">No shows yet</p>
              <p className="text-sm text-muted-foreground mt-1 mb-4">
                Create your first podcast show
              </p>
              <Button asChild>
                <Link href="/shows/new">Create Show</Link>
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {shows.map((show) => (
              <Card key={show.id} className="hover:border-primary/40 transition-colors">
                <CardHeader className="flex flex-row items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <CardTitle className="text-base truncate">
                      <Link href={`/shows/${show.id}`} className="hover:underline">
                        {show.name}
                      </Link>
                    </CardTitle>
                    <CardDescription className="mt-1 line-clamp-2">
                      {show.description || "No description"}
                    </CardDescription>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="shrink-0 text-muted-foreground hover:text-destructive"
                    onClick={() => del.mutate(show.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </CardHeader>
                <CardContent className="flex items-center justify-between">
                  <Badge variant="outline">{show.default_format}</Badge>
                  <span className="text-xs text-muted-foreground">{formatDate(show.created_at)}</span>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
