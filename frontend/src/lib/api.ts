export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type Source = {
  episode: string;
  guest: string;
  timestamp?: string | null;
  score: number;
  source_path?: string;
};

export type Message = {
  id?: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};

export async function createSession() {
  const response = await fetch(`${API_URL}/api/sessions`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({}),
  });
  if (!response.ok) throw new Error("Could not create session");
  return response.json() as Promise<{ id: string; title: string }>;
}

export async function loadSession(id: string) {
  const response = await fetch(`${API_URL}/api/sessions/${id}`);
  if (!response.ok) throw new Error("Could not load session");
  return response.json() as Promise<{ id: string; title: string; messages: Message[] }>;
}
