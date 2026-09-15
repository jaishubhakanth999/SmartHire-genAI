"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { apiDelete, apiGet, apiPostJson } from "@/lib/api";
import type { ChatMessage } from "@/types";

type Session = { id: string; title?: string | null; created_at: string };
type SessionDetail = Session & { messages: Array<ChatMessage & { created_at?: string }> };

export default function MentorPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [loadingSessions, setLoadingSessions] = useState(true);
  const [loadingChat, setLoadingChat] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  async function loadSessions() {
    setLoadingSessions(true);
    try {
      const data = await apiGet("/api/mentor/sessions");
      setSessions((data.sessions || []) as Session[]);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoadingSessions(false);
    }
  }

  useEffect(() => { void loadSessions(); }, []);

  async function openSession(id: string) {
    setLoadingChat(true);
    setError(null);
    try {
      const data = (await apiGet(`/api/mentor/sessions/${id}`)) as SessionDetail;
      setSessionId(data.id);
      setMessages(data.messages.map((message) => ({ id: message.id, role: message.role, content: message.content, sources: message.sources, grounded: message.grounded, blocked: message.blocked })));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoadingChat(false);
    }
  }

  function newChat() {
    setSessionId(null);
    setMessages([]);
    setError(null);
  }

  async function deleteSession(id: string) {
    setError(null);
    try {
      await apiDelete(`/api/mentor/sessions/${id}`);
      const remaining = sessions.filter((session) => session.id !== id);
      setSessions(remaining);
      if (sessionId === id) newChat();
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function send() {
    const question = input.trim();
    if (!question || sending) return;
    setInput("");
    setError(null);
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setSending(true);
    try {
      const data = await apiPostJson("/api/mentor/chat", { message: question, session_id: sessionId });
      setSessionId(data.session_id);
      setMessages((prev) => [...prev, { role: "assistant", content: data.answer, sources: data.sources, grounded: data.grounded, blocked: data.blocked }]);
      try {
        await loadSessions();
      } catch {
        // The answer is already usable; session-list refresh should not fail the chat.
      }
    } catch (e) {
      setError((e as Error).message);
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setSending(false);
    }
  }

  return (
    <main className="min-h-[calc(100vh-64px)] bg-slate-50/70 px-5 py-6 sm:px-6 sm:py-8">
      <div className="mx-auto grid max-w-6xl gap-5 lg:grid-cols-[280px_1fr]">
        <aside className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="flex items-center justify-between gap-3">
            <div><div className="text-xs font-bold uppercase tracking-wider text-indigo-600">Career mentor</div><h1 className="mt-1 text-lg font-black text-slate-950">Your chats</h1></div>
            <button onClick={newChat} className="rounded-xl bg-indigo-600 px-3 py-2 text-xs font-bold text-white hover:bg-indigo-500">New chat</button>
          </div>
          <div className="mt-4 space-y-2">
            {loadingSessions ? <p className="text-sm text-slate-400">Loading…</p> : sessions.length === 0 ? <p className="text-sm leading-6 text-slate-400">Your mentor conversations will be saved here.</p> : sessions.map((session) => (
              <div key={session.id} className={`rounded-2xl border p-3 ${sessionId === session.id ? "border-indigo-200 bg-indigo-50/60" : "border-slate-200"}`}>
                <button className="w-full text-left" onClick={() => void openSession(session.id)}><div className="line-clamp-2 text-sm font-bold text-slate-800">{session.title || "Career chat"}</div><div className="mt-1 text-xs text-slate-400">{new Date(session.created_at).toLocaleString()}</div></button>
                <button onClick={() => void deleteSession(session.id)} className="mt-2 text-xs font-semibold text-rose-600 hover:text-rose-500">Delete</button>
              </div>
            ))}
          </div>
        </aside>

        <section className="flex min-h-[calc(100vh-112px)] flex-col rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-7">
          <div className="border-b border-slate-100 pb-5">
            <h2 className="text-2xl font-black text-slate-950">🤖 AI Career Mentor</h2>
            <p className="mt-1 max-w-2xl text-sm leading-6 text-slate-500">Ask career questions and get answers directly from Sarvam AI. Your private conversation history is saved to your account.</p>
          </div>

          {error && <div role="alert" className="mt-4 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">{error}</div>}

          <div className="mt-5 flex-1 space-y-4 overflow-y-auto pr-1">
            {loadingChat && <p className="text-sm text-slate-400">Loading conversation…</p>}
            {messages.length === 0 && !loadingChat && <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-5 text-sm text-slate-500">Try asking: <span className="font-semibold text-slate-700">“How should I prepare for a Data Analyst interview?”</span></div>}
            {messages.map((m, i) => (
              <div key={m.id || `${m.role}-${i}`} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[88%] rounded-2xl px-4 py-3 text-sm ${m.role === "user" ? "bg-indigo-600 text-white" : "border border-slate-200 bg-slate-50 text-slate-800"}`}>
                  {m.role === "assistant" ? <div className="prose prose-sm max-w-none prose-slate"><ReactMarkdown>{m.content}</ReactMarkdown></div> : <p className="whitespace-pre-wrap">{m.content}</p>}
                  {m.blocked && <p className="mt-1 text-xs font-semibold text-rose-600">This request was blocked by the safety filter.</p>}
                </div>
              </div>
            ))}
            {sending && <div className="text-sm text-slate-400">Thinking…</div>}
            <div ref={bottomRef} />
          </div>

          <form onSubmit={(e) => { e.preventDefault(); void send(); }} className="mt-5 flex gap-2 border-t border-slate-100 pt-5">
            <input value={input} onChange={(e) => setInput(e.target.value)} disabled={sending} maxLength={2000} placeholder="Ask a career question…" className="min-w-0 flex-1 rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 disabled:bg-slate-50" />
            <button type="submit" disabled={sending || !input.trim()} className="rounded-xl bg-indigo-600 px-5 py-3 text-sm font-bold text-white hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50">Send</button>
          </form>
        </section>
      </div>
    </main>
  );
}
