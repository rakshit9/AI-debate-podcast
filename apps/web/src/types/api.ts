export type EpisodeFormat = "debate" | "interview" | "panel";

export type EpisodeStatus =
  | "queued"
  | "researching"
  | "scripting"
  | "debating"
  | "fact_checking"
  | "synthesizing"
  | "mixing"
  | "publishing"
  | "completed"
  | "failed";

export type VoiceProvider = "elevenlabs" | "openai" | "coqui";

export interface Episode {
  id: string;
  show_id: string;
  topic: string;
  format: EpisodeFormat;
  status: EpisodeStatus;
  script: Record<string, unknown>;
  audio_url: string | null;
  transcript: string | null;
  duration_seconds: number | null;
  cost_usd: string;
  published_at: string | null;
  created_at: string;
}

export interface Show {
  id: string;
  owner_id: string;
  name: string;
  description: string;
  style_guide: string;
  default_format: EpisodeFormat;
  host_ids: string[];
  rss_feed_url: string | null;
  artwork_url: string | null;
  created_at: string;
}

export interface Host {
  id: string;
  name: string;
  personality_prompt: string;
  voice_id: string;
  voice_provider: VoiceProvider;
  temperature: number;
  model: string;
  created_at: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface EpisodeProgressEvent {
  episode_id: string;
  status: EpisodeStatus;
  node: string;
  message: string;
  timestamp: string;
}
