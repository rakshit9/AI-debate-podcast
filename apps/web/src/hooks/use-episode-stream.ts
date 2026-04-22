"use client";

import { useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { getAccessToken } from "@/lib/auth";
import type { EpisodeProgressEvent, EpisodeStatus } from "@/types/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface StreamState {
  events: EpisodeProgressEvent[];
  status: EpisodeStatus | null;
  connected: boolean;
}

export function useEpisodeStream(episodeId: string, active: boolean) {
  const qc = useQueryClient();
  const esRef = useRef<EventSource | null>(null);
  const [state, setState] = useState<StreamState>({ events: [], status: null, connected: false });

  useEffect(() => {
    if (!active) return;

    const token = getAccessToken();
    const url = `${API_URL}/api/v1/episodes/${episodeId}/stream${token ? `?token=${encodeURIComponent(token)}` : ""}`;
    const es = new EventSource(url);
    esRef.current = es;

    es.onopen = () => setState((s) => ({ ...s, connected: true }));

    es.onmessage = (ev: MessageEvent<string>) => {
      try {
        const event = JSON.parse(ev.data) as EpisodeProgressEvent & { type?: string };
        if (event.type === "connected") return;

        setState((s) => ({
          ...s,
          events: [...s.events, event],
          status: event.status ?? s.status,
        }));

        if (event.type === "completed" || event.type === "error") {
          void qc.invalidateQueries({ queryKey: ["episodes", episodeId] });
          void qc.invalidateQueries({ queryKey: ["episodes"] });
          es.close();
          setState((s) => ({ ...s, connected: false }));
        }
      } catch {
        // non-JSON; ignore
      }
    };

    es.onerror = () => setState((s) => ({ ...s, connected: false }));

    return () => {
      es.close();
    };
  }, [episodeId, active, qc]);

  return state;
}
