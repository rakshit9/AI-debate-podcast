"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { createEpisode, generateEpisode, listShows, ApiError } from "@/lib/api";
import { toast } from "@/hooks/use-toast";

const schema = z.object({
  show_id: z.string().uuid("Select a show"),
  topic: z.string().min(3, "Min 3 characters"),
  format: z.enum(["debate", "interview", "panel"]).default("debate"),
  generate: z.boolean().default(true),
});

type FormData = z.infer<typeof schema>;

function NewEpisodeForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const qc = useQueryClient();
  const [loading, setLoading] = useState(false);

  const { data: shows = [] } = useQuery({ queryKey: ["shows"], queryFn: listShows });

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      show_id: searchParams.get("show_id") ?? "",
      format: "debate",
      generate: true,
    },
  });

  const shouldGenerate = watch("generate");

  async function onSubmit(data: FormData) {
    setLoading(true);
    try {
      const ep = await createEpisode({ show_id: data.show_id, topic: data.topic, format: data.format });
      await qc.invalidateQueries({ queryKey: ["episodes"] });

      if (data.generate) {
        await generateEpisode(ep.id);
        toast({ title: "Episode queued for generation" });
      } else {
        toast({ title: "Episode created" });
      }

      router.push(`/episodes/${ep.id}`);
    } catch (err) {
      toast({
        variant: "destructive",
        title: "Failed",
        description: err instanceof ApiError ? err.message : "Unexpected error",
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <Header title="New Episode" />
      <div className="p-6 max-w-xl">
        <Button variant="ghost" size="sm" asChild className="mb-4">
          <Link href="/episodes">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Episodes
          </Link>
        </Button>
        <form onSubmit={handleSubmit(onSubmit)}>
          <Card>
            <CardHeader>
              <CardTitle>Generate Episode</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Show</Label>
                <Select
                  defaultValue={searchParams.get("show_id") ?? ""}
                  onValueChange={(v) => setValue("show_id", v)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a show" />
                  </SelectTrigger>
                  <SelectContent>
                    {shows.map((s) => (
                      <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.show_id && <p className="text-xs text-destructive">{errors.show_id.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="topic">Topic</Label>
                <Input
                  id="topic"
                  placeholder="e.g. Is AI replacing software engineers?"
                  {...register("topic")}
                />
                {errors.topic && <p className="text-xs text-destructive">{errors.topic.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Format</Label>
                <Select
                  defaultValue="debate"
                  onValueChange={(v) => setValue("format", v as "debate" | "interview" | "panel")}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="debate">Debate</SelectItem>
                    <SelectItem value="interview">Interview</SelectItem>
                    <SelectItem value="panel">Panel</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  className="rounded"
                  defaultChecked
                  {...register("generate")}
                />
                <span className="text-sm">Start generation immediately</span>
              </label>
            </CardContent>
            <CardFooter className="gap-2">
              <Button type="submit" disabled={loading}>
                {loading ? "Creating..." : shouldGenerate ? "Create & Generate" : "Create Episode"}
              </Button>
              <Button variant="outline" asChild>
                <Link href="/episodes">Cancel</Link>
              </Button>
            </CardFooter>
          </Card>
        </form>
      </div>
    </div>
  );
}

export default function NewEpisodePage() {
  return (
    <Suspense>
      <NewEpisodeForm />
    </Suspense>
  );
}
