import { useEffect, useRef } from "react";
import {
  Bot,
  MessageSquare,
  ShieldCheck,
} from "lucide-react";

export default function ChatPanel({
  conversation = [],
  connected = false,
}) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [conversation]);

  const isAgentA = (agent) => agent === "Agent A";

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950">

      {/* Header */}
      <div className="flex items-center gap-3 border-b border-slate-800 p-4">
        <MessageSquare size={20} className="text-blue-400" />
        <h2 className="text-lg font-semibold text-white">
          Secure Agent Conversation
        </h2>
        {connected && (
          <span className="ml-auto flex items-center gap-1.5 rounded-full bg-green-500/10 px-3 py-1 text-xs font-medium text-green-400">
            <ShieldCheck size={14} />
            Encrypted
          </span>
        )}
      </div>

      {/* Messages */}
      <div className="h-[420px] overflow-y-auto p-4 space-y-4">

        {conversation.length === 0 && (
          <div className="flex h-full items-center justify-center text-slate-500">
            Start the backend to begin the secure AI conversation
          </div>
        )}

        {conversation.map((msg, index) => (
          <div
            key={index}
            className={`flex gap-2 ${isAgentA(msg.agent) ? "flex-row-reverse" : ""}`}
          >
            <div
              className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
                isAgentA(msg.agent)
                  ? "bg-blue-600/20"
                  : "bg-green-600/20"
              }`}
            >
              <Bot
                size={16}
                className={isAgentA(msg.agent) ? "text-blue-400" : "text-green-400"}
              />
            </div>

            <div
              className={`max-w-[70%] rounded-xl px-4 py-2 ${
                isAgentA(msg.agent)
                  ? "bg-blue-600 text-white"
                  : "border border-slate-700 bg-slate-900 text-slate-200"
              }`}
            >
              <div className="mb-1 text-xs font-semibold opacity-70">
                {msg.agent}
              </div>
              {msg.text}
            </div>
          </div>
        ))}

        <div ref={bottomRef} />

      </div>

    </div>
  );
}