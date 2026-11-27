export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

export interface AnalyzeResult {
  risk_score: number;
  threat_level: "An toàn" | "Đáng ngờ" | "Nguy cơ cao" | string;
  detected_tactic: string;
  explanation: string;
  psychological_traps: string[];
  action_recommendations: string[];
  url_analysis?: {
    urls: string[];
    domains: string[];
    warnings: string[];
  };
  matched_article?: {
    id: number | string;
    title: string;
    source: string;
    url?: string;
    category_name?: string;
    summary?: string;
  } | null;
}

export interface FakeBillResult {
  is_fake: boolean;
  confidence_score: number;
  conclusion: string;
  forensic_notes?: string;
  model_used?: string;
  suspicious_points?: string[];
  layer_1_typography?: string[];
  layer_2_pixel_forensics?: string[];
  transaction_info?: {
    bank?: string;
    recipient?: string;
    account_number?: string;
    amount?: string;
    transaction_time?: string;
  };
  technical_metadata?: {
    format?: string;
    resolution?: string;
    file_size_kb?: number;
    software_signatures?: string[];
    layout_warnings?: string[];
    pixel_forensics?: {
      mean_edge_intensity?: number;
      mean_color_saturation?: number;
    };
  };
  error?: string;
}

export interface EmergencyPayload {
  title: string;
  subtitle: string;
  checklist: {
    step: string;
    icon: string;
    action: string;
    priority: string;
  }[];
  hotlines: {
    bank: string;
    hotline: string;
    desc: string;
  }[];
  police: {
    name: string;
    hotline: string;
    display: string;
    desc: string;
  };
  spam_portal: {
    name: string;
    hotline: string;
    desc: string;
    portal_url: string;
  };
}

export interface LibraryCase {
  id: number | string;
  title: string;
  source: string;
  url?: string;
  category_name: string;
  summary: string;
  keywords: string[];
  source_type: "official" | "learned";
}

export interface LibraryResponse {
  total: number;
  official_count: number;
  learned_count: number;
  filtered_count: number;
  categories: string[];
  items: LibraryCase[];
}

export interface GameOption {
  text: string;
  level: "safe" | "neutral" | "risky";
  feedback: string;
  red_flag?: string;
}

export interface GameStage {
  scammer?: string;
  scammer_message?: string;
  hint?: string;
  red_flag?: string;
  options: GameOption[];
  safe_keywords?: string[];
  risky_keywords?: string[];
}

export interface GameScenario {
  id: string;
  icon?: string;
  title: string;
  subtitle?: string;
  brief?: string;
  category?: string;
  category_name?: string;
  difficulty?: string;
  channel?: string;
  persona?: string;
  persona_avatar?: string;
  scammer_persona?: string;
  context?: string;
  description?: string;
  stages: GameStage[];
}

export interface EvaluateGameResponse {
  level: "safe" | "neutral" | "risky";
  label: string;
  title: string;
  score_delta: number;
  hp_delta: number;
  user_reply: string;
  feedback: string;
  red_flag: string;
  is_last_stage: boolean;
}

export async function fetchHealth(): Promise<{ status: string; has_env_gemini_key: boolean }> {
  const res = await fetch(`${API_BASE}/api/health`, { cache: "no-store" });
  if (!res.ok) throw new Error("Backend không phản hồi");
  return res.json();
}

export async function analyzeMessageApi(params: {
  text: string;
  apiKey?: string;
  image?: File | null;
}): Promise<AnalyzeResult> {
  const form = new FormData();
  form.append("text", params.text);
  if (params.apiKey) form.append("api_key", params.apiKey);
  if (params.image) form.append("image", params.image);

  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Lỗi phân tích tin nhắn" }));
    throw new Error(err.detail || "Lỗi phân tích tin nhắn");
  }
  return res.json();
}

export async function analyzeFakeBillApi(params: {
  sampleType?: "fake" | "real";
  image?: File | null;
  apiKey?: string;
}): Promise<FakeBillResult> {
  const form = new FormData();
  if (params.sampleType) form.append("sample_type", params.sampleType);
  if (params.apiKey) form.append("api_key", params.apiKey);
  if (params.image) form.append("image", params.image);

  const res = await fetch(`${API_BASE}/api/fake-bill/analyze`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Lỗi giám định biên lai" }));
    throw new Error(err.detail || "Lỗi giám định biên lai");
  }
  return res.json();
}

export async function fetchEmergencyApi(): Promise<EmergencyPayload> {
  const res = await fetch(`${API_BASE}/api/emergency`, { cache: "no-store" });
  if (!res.ok) throw new Error("Không tải được dữ liệu cấp cứu");
  return res.json();
}

export async function fetchLibraryApi(params?: {
  sourceType?: "all" | "official" | "learned";
  category?: string;
  q?: string;
}): Promise<LibraryResponse> {
  const sp = new URLSearchParams();
  if (params?.sourceType) sp.set("source_type", params.sourceType);
  if (params?.category) sp.set("category", params.category);
  if (params?.q) sp.set("q", params.q);
  const res = await fetch(`${API_BASE}/api/library?${sp.toString()}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Không tải được thư viện cảnh báo");
  return res.json();
}

export async function fetchGameScenariosApi(): Promise<{
  total: number;
  categories: string[];
  scenarios: GameScenario[];
}> {
  const res = await fetch(`${API_BASE}/api/game/scenarios`, { cache: "no-store" });
  if (!res.ok) throw new Error("Không tải được danh sách tình huống");
  return res.json();
}

export async function evaluateGameAnswerApi(payload: {
  scenario_id: string;
  stage_index: number;
  option_index?: number;
  free_text?: string;
}): Promise<EvaluateGameResponse> {
  const res = await fetch(`${API_BASE}/api/game/evaluate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Lỗi chấm điểm" }));
    throw new Error(err.detail || "Lỗi chấm điểm");
  }
  return res.json();
}

