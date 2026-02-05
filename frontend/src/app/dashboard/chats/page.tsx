/**
 * Chat History page - displays paginated chat logs with detail modal.
 */

"use client";

import { useState, useEffect, useCallback } from "react";
import { MessageCircle, X, User, Bot, Loader2 } from "lucide-react";
import { getChatLogs, getChatLogDetail } from "@/lib/api/chats";
import type {
  ChatLogSummary,
  ChatLogsResponse,
  ChatLogDetail,
} from "@/types/analytics";

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function ChatDetailModal({
  chat,
  onClose,
}: {
  chat: ChatLogDetail;
  onClose: () => void;
}) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[80vh] flex flex-col shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-zinc-200">
          <div>
            <h2 className="text-lg font-bold text-zinc-900">Chat Details</h2>
            <p className="text-sm text-zinc-500 mt-1">
              {formatDate(chat.started_at)}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-zinc-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-zinc-500" />
          </button>
        </div>

        {/* Chat info */}
        <div className="p-4 bg-zinc-50 border-b border-zinc-200 flex gap-4 text-sm">
          <div>
            <span className="text-zinc-500">Messages:</span>{" "}
            <span className="font-semibold text-zinc-900">
              {chat.total_messages}
            </span>
          </div>
          {chat.intent && (
            <div>
              <span className="text-zinc-500">Intent:</span>{" "}
              <span className="font-semibold text-zinc-900">{chat.intent}</span>
            </div>
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {chat.messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.role !== "user" && (
                <div className="w-8 h-8 rounded-full bg-teal-100 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-teal-600" />
                </div>
              )}
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-2.5 ${
                  msg.role === "user"
                    ? "bg-teal-600 text-white"
                    : "bg-zinc-100 text-zinc-900"
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">
                  {msg.content || "(no content)"}
                </p>
                <p
                  className={`text-xs mt-1 ${msg.role === "user" ? "text-teal-100" : "text-zinc-400"}`}
                >
                  {formatDate(msg.created_at)}
                </p>
              </div>
              {msg.role === "user" && (
                <div className="w-8 h-8 rounded-full bg-zinc-200 flex items-center justify-center flex-shrink-0">
                  <User className="w-4 h-4 text-zinc-600" />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Summary */}
        {chat.summary && (
          <div className="p-4 border-t border-zinc-200 bg-zinc-50">
            <p className="text-xs font-semibold text-zinc-500 uppercase mb-1">
              Summary
            </p>
            <p className="text-sm text-zinc-700">{chat.summary}</p>
          </div>
        )}
      </div>
    </div>
  );
}

function ChatLogRow({
  chat,
  onView,
}: {
  chat: ChatLogSummary;
  onView: () => void;
}) {
  return (
    <tr className="hover:bg-zinc-50 transition-colors">
      <td className="px-4 py-3 text-sm text-zinc-900" suppressHydrationWarning>
        {formatDate(chat.started_at)}
      </td>
      <td className="px-4 py-3 text-sm text-zinc-900 text-center">
        {chat.total_messages}
      </td>
      <td className="px-4 py-3">
        {chat.intent ? (
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-700">
            {chat.intent}
          </span>
        ) : (
          <span className="text-zinc-400 text-sm">-</span>
        )}
      </td>
      <td className="px-4 py-3">
        <button
          onClick={onView}
          className="text-teal-600 hover:text-teal-700 text-sm font-medium hover:underline"
        >
          View
        </button>
      </td>
    </tr>
  );
}

function Pagination({
  page,
  totalPages,
  onPageChange,
}: {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}) {
  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-between px-4 py-3 border-t border-zinc-200">
      <p className="text-sm text-zinc-500">
        Page {page} of {totalPages}
      </p>
      <div className="flex gap-2">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
          className="px-3 py-1.5 text-sm font-medium rounded-lg border border-zinc-200 text-zinc-700 hover:bg-zinc-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages}
          className="px-3 py-1.5 text-sm font-medium rounded-lg border border-zinc-200 text-zinc-700 hover:bg-zinc-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
        </button>
      </div>
    </div>
  );
}

export default function ChatHistoryPage() {
  const [chats, setChats] = useState<ChatLogsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [selectedChat, setSelectedChat] = useState<ChatLogDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const fetchChats = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getChatLogs(page, 20);
      setChats(data);
    } catch (err) {
      console.error("Failed to fetch chat logs:", err);
      setError("Failed to load chat logs. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => {
    fetchChats();
  }, [fetchChats]);

  const handleViewChat = async (chatId: string) => {
    setLoadingDetail(true);
    try {
      const detail = await getChatLogDetail(chatId);
      setSelectedChat(detail);
    } catch (err) {
      console.error("Failed to fetch chat detail:", err);
    } finally {
      setLoadingDetail(false);
    }
  };

  return (
    <div className="max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-nunito font-bold text-zinc-900 flex items-center gap-3">
          <MessageCircle className="w-8 h-8 text-teal-600" />
          Chat History
        </h1>
        <p className="text-zinc-600 mt-1">
          View chat conversations and message history
        </p>
      </div>

      {loading && !chats ? (
        <div className="bg-white rounded-xl border border-zinc-200 p-12 shadow-sm flex items-center justify-center">
          <Loader2 className="w-8 h-8 text-teal-600 animate-spin" />
        </div>
      ) : error ? (
        <div className="bg-white rounded-xl border border-zinc-200 p-12 shadow-sm text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={fetchChats}
            className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
          >
            Retry
          </button>
        </div>
      ) : chats && chats.items.length === 0 ? (
        <div className="bg-white rounded-xl border border-zinc-200 p-12 shadow-sm text-center">
          <MessageCircle className="w-16 h-16 text-zinc-300 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-zinc-900 mb-2">
            No Chats Yet
          </h2>
          <p className="text-zinc-600">
            Chat conversations will appear here once customers start chatting.
          </p>
        </div>
      ) : chats ? (
        <div className="bg-white rounded-xl border border-zinc-200 shadow-sm overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="bg-zinc-50 border-b border-zinc-200">
                <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 uppercase tracking-wide">
                  Time
                </th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-zinc-500 uppercase tracking-wide">
                  Messages
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 uppercase tracking-wide">
                  Intent
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 uppercase tracking-wide">
                  Action
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-100">
              {chats.items.map((chat) => (
                <ChatLogRow
                  key={chat.id}
                  chat={chat}
                  onView={() => handleViewChat(chat.id)}
                />
              ))}
            </tbody>
          </table>
          <Pagination
            page={page}
            totalPages={chats.total_pages}
            onPageChange={setPage}
          />
        </div>
      ) : null}

      {/* Loading overlay for detail */}
      {loadingDetail && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 shadow-xl flex items-center gap-3">
            <Loader2 className="w-5 h-5 text-teal-600 animate-spin" />
            <span className="text-zinc-700">Loading chat...</span>
          </div>
        </div>
      )}

      {/* Chat detail modal */}
      {selectedChat && (
        <ChatDetailModal
          chat={selectedChat}
          onClose={() => setSelectedChat(null)}
        />
      )}
    </div>
  );
}
