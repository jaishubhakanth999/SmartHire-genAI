"use client";

import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { apiPostJson } from "@/lib/api";
import type { ChatMessage } from "@/types";

export default function MentorPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send() {
    const question = input.trim();
    if (!question || sending) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setSending(true);
    try {
      const data = await apiPostJson("/api/mentor/chat", {
        message: question,
        session_id: sessionId,
      });
      setSessionId(data.session_id);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
          grounded: data.grounded,
          blocked: data.blocked,
        },
      ]);
    } catch (e) {
      setMessages((prev) => [...prev, { role: "assistant", content: `Error: ${(e as Error).message}` }]);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-57px)] max-w-3xl flex-col px-6 py-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">🤖 AI Career Mentor</h1>
        <p className="mt-1 text-sm text-slate-500">
          Answers are grounded in a curated career-notes knowledge base — ask career questions, not
          general trivia. The mentor will say &ldquo;I don&apos;t know&rdquo; if the answer isn&apos;t in its documents.
        </p>
      </div>

      <div className="mt-6 flex-1 space-y-4 overflow-y-auto pr-1">
        {messages.length === 0 && (
          <p className="text-sm text-slate-400">Try: &ldquo;How do I switch into a Data Analyst role?&rdquo;</p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[85%] rounded-xl px-4 py-2.5 text-sm ${
                m.role === "user" ? "bg-indigo-600 text-white" : "bg-white border border-slate-200 text-slate-800"
              }`}
            >
              {m.role === "assistant" ? (
                <div className="prose prose-sm max-w-none prose-slate">
                  <ReactMarkdown>{m.content}</ReactMarkdown>
                </div>
              ) : (
                m.content
              )}
              {m.sources && m.sources.length > 0 && (
                <p className="mt-2 text-xs text-slate-400">📚 Sources: {m.sources.join(", ")}</p>
              )}
              {m.grounded === false && (
                <p className="mt-1 text-xs text-amber-600">⚠️ May not be fully grounded in the documents.</p>
              )}
            </div>
          </div>
        ))}
        {sending && <p className="text-sm text-slate-400">Thinking…</p>}
        <div ref={bottomRef} />
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send();
        }}
        className="mt-4 flex gap-2"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a career question…"
          className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        <button
          type="submit"
          disabled={sending}
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
}
