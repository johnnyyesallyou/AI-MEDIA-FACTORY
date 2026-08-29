// Wizard API types
export interface WizardSuggestRequest {
  name: string;
  description?: string;
}

export interface WizardSuggestResponse {
  content_type: string;
  topic: string;
  language: string;
  profile_key: string;
  sources: string[];
  confidence: number;
  reasoning: string;
}

export interface WizardConfigRequest {
  content_type: string;
  topic: string;
  language?: string;
  profile_key: string;
  sources: string[];
  name?: string;
  platform?: string;
  schedule_cron?: string;
  job_type?: string;
}

export interface WizardValidateResponse {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

export interface CreateFromWizardRequest {
  name: string;
  config: WizardConfigRequest;
  chat_id?: string;
  bot_token?: string;
  vk_group_id?: string;
  vk_access_token?: string;
}

export interface CreateFromWizardResponse {
  id: string;
  name: string;
  platform: string;
  content_type: string;
  topic: string;
  profile_key: string;
  sources: string[];
  schedule_cron: string;
  status: string;
}

// Channel Control types
export interface ChannelStartResponse {
  id: string;
  name: string;
  status: string;
  message: string;
}

export interface ChannelStatusResponse {
  id: string;
  name: string;
  platform: string;
  is_connected: boolean;
  is_active: boolean;
  content_type?: string;
  topic?: string;
  profile_key?: string;
  sources: string[];
  schedule_cron?: string;
  last_run?: string;
  next_run?: string;
  today_published: number;
  today_failed: number;
}

export interface DashboardChannel {
  id: string;
  name: string;
  platform: string;
  is_connected: boolean;
  is_active: boolean;
  content_type?: string;
  topic?: string;
  published_24h: number;
}

export interface DashboardResponse {
  total_channels: number;
  active_channels: number;
  channels: DashboardChannel[];
}

// Posts API types
export interface PostGenerateRequest {
  topic: string;
  content?: Record<string, any>;
  content_type?: string;
}

export interface PostGenerateResponse {
  id: string;
  text: string;
  media_type: string;
  image_url?: string;
  video_url?: string;
  ready_to_publish: boolean;
}

export interface PostHistoryResponse {
  id: string;
  channel_id: string;
  platform?: string;
  text?: string;
  image_url?: string;
  video_url?: string;
  media_type?: string;
  message_id?: string;
  posted_at?: string;
}

export interface ChannelMetricsResponse {
  channel_id: string;
  period_days: number;
  total_posts: number;
  total_views: number;
  total_likes: number;
  avg_views_per_post: number;
  avg_likes_per_post: number;
  top_patterns: string[];
}

export interface ChannelLearning {
  pattern: string;
  score: number;
  evidence_count: number;
  last_updated?: string;
}

// Sources API types
export interface SourceDefinition {
  id: string;
  name: string;
  content_types: string[];
  topics: string[];
  languages: string[];
  capabilities: string[];
}