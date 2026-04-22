"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { createHost, ApiError } from "@/lib/api";
import { toast } from "@/hooks/use-toast";

const schema = z.object({
  name: z.string().min(1, "Name required"),
  personality_prompt: z.string().min(10, "Min 10 characters"),
  voice_id: z.string().min(1, "Voice ID required"),
  voice_provider: z.enum(["elevenlabs", "openai", "coqui"]).default("elevenlabs"),
  temperature: z.coerce.number().min(0).max(2).default(0.7),
  model: z.string().default("claude-sonnet-4-6"),
});

type FormData = z.infer<typeof schema>;

export default function NewHostPage() {
  const router = useRouter();
  const qc = useQueryClient();
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { voice_provider: "elevenlabs", temperature: 0.7, model: "claude-sonnet-4-6" },
  });

  async function onSubmit(data: FormData) {
    setLoading(true);
    try {
      await createHost(data);
      await qc.invalidateQueries({ queryKey: ["hosts"] });
      toast({ title: "Host created" });
      router.push("/hosts");
    } catch (err) {
      toast({
        variant: "destructive",
        title: "Failed to create host",
        description: err instanceof ApiError ? err.message : "Unexpected error",
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <Header title="New Host" />
      <div className="p-6 max-w-xl">
        <Button variant="ghost" size="sm" asChild className="mb-4">
          <Link href="/hosts">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Hosts
          </Link>
        </Button>
        <form onSubmit={handleSubmit(onSubmit)}>
          <Card>
            <CardHeader>
              <CardTitle>Create AI Host</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Name</Label>
                <Input id="name" placeholder="Alex Chen" {...register("name")} />
                {errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="personality_prompt">Personality Prompt</Label>
                <Textarea
                  id="personality_prompt"
                  placeholder="You are a skeptical tech journalist who challenges conventional wisdom..."
                  rows={4}
                  {...register("personality_prompt")}
                />
                {errors.personality_prompt && (
                  <p className="text-xs text-destructive">{errors.personality_prompt.message}</p>
                )}
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Voice Provider</Label>
                  <Select
                    defaultValue="elevenlabs"
                    onValueChange={(v) => setValue("voice_provider", v as "elevenlabs" | "openai" | "coqui")}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="elevenlabs">ElevenLabs</SelectItem>
                      <SelectItem value="openai">OpenAI TTS</SelectItem>
                      <SelectItem value="coqui">Coqui</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="voice_id">Voice ID</Label>
                  <Input id="voice_id" placeholder="ElevenLabs voice ID" {...register("voice_id")} />
                  {errors.voice_id && (
                    <p className="text-xs text-destructive">{errors.voice_id.message}</p>
                  )}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="temperature">Temperature</Label>
                  <Input id="temperature" type="number" step="0.1" min="0" max="2" {...register("temperature")} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="model">LLM Model</Label>
                  <Input id="model" placeholder="claude-sonnet-4-6" {...register("model")} />
                </div>
              </div>
            </CardContent>
            <CardFooter className="gap-2">
              <Button type="submit" disabled={loading}>
                {loading ? "Creating..." : "Create Host"}
              </Button>
              <Button variant="outline" asChild>
                <Link href="/hosts">Cancel</Link>
              </Button>
            </CardFooter>
          </Card>
        </form>
      </div>
    </div>
  );
}
