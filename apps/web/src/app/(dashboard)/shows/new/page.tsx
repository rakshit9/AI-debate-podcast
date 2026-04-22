"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { createShow, ApiError } from "@/lib/api";
import { toast } from "@/hooks/use-toast";

const schema = z.object({
  name: z.string().min(1, "Name required"),
  description: z.string().default(""),
  style_guide: z.string().default(""),
  default_format: z.enum(["debate", "interview", "panel"]).default("debate"),
});

type FormData = z.infer<typeof schema>;

export default function NewShowPage() {
  const router = useRouter();
  const qc = useQueryClient();
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema), defaultValues: { default_format: "debate" } });

  async function onSubmit(data: FormData) {
    setLoading(true);
    try {
      await createShow(data);
      await qc.invalidateQueries({ queryKey: ["shows"] });
      toast({ title: "Show created" });
      router.push("/shows");
    } catch (err) {
      toast({
        variant: "destructive",
        title: "Failed to create show",
        description: err instanceof ApiError ? err.message : "Unexpected error",
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <Header title="New Show" />
      <div className="p-6 max-w-xl">
        <Button variant="ghost" size="sm" asChild className="mb-4">
          <Link href="/shows">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Shows
          </Link>
        </Button>
        <form onSubmit={handleSubmit(onSubmit)}>
          <Card>
            <CardHeader>
              <CardTitle>Create Podcast Show</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Show Name</Label>
                <Input id="name" placeholder="My AI Podcast" {...register("name")} />
                {errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea id="description" placeholder="What is this show about?" rows={3} {...register("description")} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="style_guide">Style Guide</Label>
                <Textarea
                  id="style_guide"
                  placeholder="Tone, topics, audience persona..."
                  rows={3}
                  {...register("style_guide")}
                />
              </div>
              <div className="space-y-2">
                <Label>Default Format</Label>
                <Select
                  defaultValue="debate"
                  onValueChange={(v) => setValue("default_format", v as "debate" | "interview" | "panel")}
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
            </CardContent>
            <CardFooter className="gap-2">
              <Button type="submit" disabled={loading}>
                {loading ? "Creating..." : "Create Show"}
              </Button>
              <Button variant="outline" asChild>
                <Link href="/shows">Cancel</Link>
              </Button>
            </CardFooter>
          </Card>
        </form>
      </div>
    </div>
  );
}
