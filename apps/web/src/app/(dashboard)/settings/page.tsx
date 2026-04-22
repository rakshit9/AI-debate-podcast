"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Copy, Key, Trash2, Eye, EyeOff } from "lucide-react";
import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { createApiKey, revokeApiKey, getMe } from "@/lib/api";
import { toast } from "@/hooks/use-toast";

export default function SettingsPage() {
  const [rawKey, setRawKey] = useState<string | null>(null);
  const [showKey, setShowKey] = useState(false);
  const [keyLoading, setKeyLoading] = useState(false);
  const [revokeLoading, setRevokeLoading] = useState(false);

  const { data: user } = useQuery({ queryKey: ["me"], queryFn: getMe });

  async function handleCreateKey() {
    setKeyLoading(true);
    try {
      const { raw_key } = await createApiKey();
      setRawKey(raw_key);
      toast({ title: "API key created", description: "Copy it now — it won't be shown again." });
    } catch {
      toast({ variant: "destructive", title: "Failed to create API key" });
    } finally {
      setKeyLoading(false);
    }
  }

  async function handleRevokeKey() {
    setRevokeLoading(true);
    try {
      await revokeApiKey();
      setRawKey(null);
      toast({ title: "API key revoked" });
    } catch {
      toast({ variant: "destructive", title: "Failed to revoke API key" });
    } finally {
      setRevokeLoading(false);
    }
  }

  function copyKey() {
    if (!rawKey) return;
    void navigator.clipboard.writeText(rawKey);
    toast({ title: "Copied to clipboard" });
  }

  return (
    <div>
      <Header title="Settings" />
      <div className="p-6 max-w-2xl space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Account</CardTitle>
            <CardDescription>Your account details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <Label>Email</Label>
              <Input value={user?.email ?? ""} readOnly className="bg-muted" />
            </div>
            <div className="space-y-2">
              <Label>User ID</Label>
              <Input value={user?.id ?? ""} readOnly className="bg-muted font-mono text-xs" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Key className="h-4 w-4" />
              API Key
            </CardTitle>
            <CardDescription>
              Use this key to authenticate CLI and programmatic access
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {rawKey ? (
              <div className="space-y-2">
                <Label>Your new API key</Label>
                <div className="flex items-center gap-2">
                  <Input
                    value={showKey ? rawKey : rawKey.replace(/./g, "•")}
                    readOnly
                    className="font-mono text-xs bg-muted"
                  />
                  <Button variant="ghost" size="icon" onClick={() => setShowKey(!showKey)}>
                    {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                  <Button variant="ghost" size="icon" onClick={copyKey}>
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground">
                  This key will only be shown once. Store it securely.
                </p>
              </div>
            ) : null}

            <Separator />
            <div className="flex gap-3">
              <Button onClick={handleCreateKey} disabled={keyLoading} variant="outline">
                {keyLoading ? "Generating..." : "Generate New Key"}
              </Button>
              <Button
                variant="destructive"
                onClick={handleRevokeKey}
                disabled={revokeLoading}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                {revokeLoading ? "Revoking..." : "Revoke Key"}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Platform Info</CardTitle>
          </CardHeader>
          <CardContent className="text-sm space-y-2">
            <div className="flex justify-between">
              <span className="text-muted-foreground">API endpoint</span>
              <span className="font-mono text-xs">{process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Version</span>
              <span>v0.1.0</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
