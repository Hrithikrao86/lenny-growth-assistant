"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { Artifact, ArtifactViewer } from "../components/Artifact/ArtifactViewer";
import { API_URL, Message, Source, createSession, loadSession } from "../lib/api";

const STORAGE_KEY = "lenny-growth-session";

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [query, setQuery] = useState("");
  const [provider, setProvider] = useState("ollama");
  const [mode, setMode] = useState("default");
  const [sources, setSources] = useState<Source[]>([]);
  const [artifact, setArtifact] = useState<Artifact | null>(null);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState("Ready");
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    const saved = window.localStorage.getItem(STORAGE_KEY);
    if (saved) {
      loadSession(saved)
        .then((data) => {
          setSessionId(data.id);
          setMessages(data.messages);
          const latest = [...data.messages].reverse().find((m) => m.sources?.length);
          setSources(latest?.sources || []);
        })
        .catch(() => window.localStorage.removeItem(STORAGE_KEY));
    }
  }, []);

  async function newChat() {
    abortRef.current?.abort();
    const session = await createSession();
    window.localStorage.setItem(STORAGE_KEY, session.id);
    setSessionId(session.id);
    setMessages([]);
    setSources([]);
    setArtifact(null);
    setStatus("Ready");
  }

  async function ask(event?: FormEvent) {
    event?.preventDefault();
    if (!query.trim() || busy) return;
    let id = sessionId;
    if (!id) {
      const session = await createSession();
      id = session.id;
      setSessionId(id);
      window.localStorage.setItem(STORAGE_KEY, id);
    }

    const userText = query.trim();
    setQuery("");
    setBusy(true);
    setSources([]);
    setArtifact(null);
    setStatus("Retrieving transcripts…");
    setMessages((prev) => [...prev, { role: "user", content: userText }]);

    const assistantIndex = messages.length + 1;
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);
    abortRef.current = new AbortController();

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ session_id: id, message: userText, provider, mode }),
        signal: abortRef.current.signal,
      });
      if (!response.ok || !response.body) throw new Error(await response.text());

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const payload = line.slice(6);
          if (payload === "[DONE]") continue;
          const data = JSON.parse(payload);
          if (data.type === "status") setStatus(data.content);
          if (data.type === "sources") setSources(data.sources || []);
          if (data.type === "artifact") setArtifact(data.artifact);
          if (data.type === "token") {
            setMessages((prev) =>
              prev.map((message, index) =>
                index === assistantIndex ? { ...message, content: message.content + data.content } : message,
              ),
            );
          }
          if (data.type === "error") throw new Error(data.content);
        }
      }
      setStatus("Ready");
    } catch (error) {
      if ((error as Error).name !== "AbortError") {
        setStatus((error as Error).message || "Request failed");
        setMessages((prev) =>
          prev.map((message, index) =>
            index === assistantIndex ? { ...message, content: `Error: ${(error as Error).message}` } : message,
          ),
        );
      }
    } finally {
      setBusy(false);
    }
  }

  const latestSources = useMemo(() => sources.slice(0, 5), [sources]);

  return (
    <main className="workspace">
      <section className="chat-pane">
        <header className="topbar">
          <div>
            <div className="brand"><span className="brand-mark">L</span> Lenny Growth Assistant</div>
            <div className="subbrand">Transcript-grounded product & growth research</div>
          </div>
          <button className="ghost-button" onClick={newChat}>＋ New chat</button>
        </header>

        <div className="controls">
          <label>Model <select value={provider} onChange={(e) => setProvider(e.target.value)} disabled={busy}>
            <option value="ollama">Ollama · local</option>
            <option value="claude">Claude · cloud</option>
            <option value="claude_agent">Claude Agent SDK</option>
          </select></label>
          <label>Mode <select value={mode} onChange={(e) => setMode(e.target.value)} disabled={busy}>
            <option value="default">Grounded answer</option>
            <option value="ship30">Ship 30 essay</option>
          </select></label>
          <span className="status"><i /> {status}</span>
        </div>

        <div className="messages">
          {messages.length === 0 && (
            <div className="welcome">
              <span className="welcome-kicker">RESEARCH WORKSPACE</span>
              <h1>What are you trying to solve?</h1>
              <p>Ask a product or growth question. Answers are grounded in Lenny&apos;s Podcast transcripts and show the sources used.</p>
              <div className="suggestions">
                {['How should a startup find product-market fit?', 'What makes a strong growth loop?', 'How do great PMs prioritize?'].map((text) => (
                  <button key={text} onClick={() => setQuery(text)}>{text}<span>→</span></button>
                ))}
              </div>
            </div>
          )}
          {messages.map((message, index) => (
            <div className={`message ${message.role}`} key={`${message.role}-${index}`}>
              <div className="avatar">{message.role === "user" ? "You" : "L"}</div>
              <div className="message-body">
                <div className="message-label">{message.role === "user" ? "You" : "Lenny Assistant"}</div>
                <div className="message-content">{message.content || (busy && index === messages.length - 1 ? "Thinking…" : "")}</div>
              </div>
            </div>
          ))}
        </div>

        <form className="composer" onSubmit={ask}>
          <textarea value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); ask(); } }} placeholder="Ask about product, growth, leadership…" rows={2} />
          <div className="composer-footer"><span>Enter to send · Shift+Enter for newline</span><button disabled={busy || !query.trim()}>{busy ? "Working…" : "Ask Lenny →"}</button></div>
        </form>
      </section>

      <aside className="artifact-pane">
        <ArtifactViewer artifact={artifact} />
        <div className="sources-panel">
          <div className="sources-title"><span>Sources</span><span>{latestSources.length}</span></div>
          {latestSources.length === 0 ? <p>No transcript sources yet.</p> : latestSources.map((source, index) => (
            <div className="source" key={`${source.source_path}-${index}`}>
              <div className="source-number">{index + 1}</div>
              <div><strong>{source.episode}</strong><small>{source.guest} · {source.timestamp || "topic context"}</small></div>
              <em>{source.score}</em>
            </div>
          ))}
        </div>
      </aside>
    </main>
  );
}
