/**
 * Chat History page - displays chat analytics and paginated logs with detail modal.
 */

"use client";

import { useState, useEffect, useCallback } from "react";
import {
  MessageCircle,
  X,
  User,
  Bot,
  Loader2,
  TrendingUp,
  CheckCircle,
  BarChart3,
  Activity,
} from "lucide-react";
import { getChatLogs, getChatLogDetail, getChatAnalytics } from "@/lib/api/chats";
import type {
  ChatLogSummary,
  ChatLogsResponse,
  ChatLogDetail,
  EnhancedChatAnalytics,
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

function SentimentBadge({ sentiment }: { sentiment: string | null }) {
  if (!sentiment) return <span className="text-zinc-400 text-sm">-</span>;

  const colors: Record<string, string> = {
    positive: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
    neutral: "bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400",
    negative: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${colors[sentiment] || "bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400"}`}
    >
      {sentiment}
    </span>
  );
}

function ResolutionBadge({ status }: { status: string | null }) {
  if (!status) return <span className="text-zinc-400 text-sm">-</span>;

  const colors: Record<string, string> = {
    resolved: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
    unresolved: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
    partial: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
    escalated: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${colors[status] || "bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400"}`}
    >
      {status}
    </span>
  );
}

function StatsCard({
  title,
  value,
  subtitle,
  icon: Icon,
  color,
}: {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}) {
  const colorClasses: Record<string, { bg: string; icon: string }> = {
    teal: { bg: "bg-teal-50 dark:bg-teal-900/30", icon: "text-teal-600 dark:text-teal-400" },
    blue: { bg: "bg-blue-50 dark:bg-blue-900/30", icon: "text-blue-600 dark:text-blue-400" },
    emerald: { bg: "bg-emerald-50 dark:bg-emerald-900/30", icon: "text-emerald-600 dark:text-emerald-400" },
    purple: { bg: "bg-purple-50 dark:bg-purple-900/30", icon: "text-purple-600 dark:text-purple-400" },
    orange: { bg: "bg-orange-50 dark:bg-orange-900/30", icon: "text-orange-600 dark:text-orange-400" },
  };
  const c = colorClasses[color] || colorClasses.teal;

  return (
    <div className="bg-white dark:bg-[#1E2530] rounded-xl border border-zinc-200 dark:border-zinc-700 p-5 shadow-sm">
      <div className="flex items-center gap-3 mb-2">
        <div className={`p-2 ${c.bg} rounded-lg`}>
          <Icon className={`w-5 h-5 ${c.icon}`} />
        </div>
        <p className="text-xs text-zinc-600 dark:text-zinc-400 font-semibold uppercase tracking-wide">
          {title}
        </p>
      </div>
      <p className="text-2xl font-black text-zinc-900 dark:text-white font-nunito">{value}</p>
      {subtitle && (
        <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">{subtitle}</p>
      )}
    </div>
  );
}

function ChatSentimentCard({
  sentiment,
}: {
  sentiment: EnhancedChatAnalytics["sentiment"];
}) {
  if (!sentiment) return null;

  const total =
    sentiment.positive_chats + sentiment.neutral_chats + sentiment.negative_chats;
  if (total === 0) return null;

  const pct = (n: number) => (total > 0 ? Math.round((n / total) * 100) : 0);

  return (
    <div className="bg-white dark:bg-[#1E2530] rounded-xl border border-zinc-200 dark:border-zinc-700 p-5 shadow-sm">
      <h3 className="text-sm font-semibold text-zinc-900 dark:text-white mb-4 flex items-center gap-2">
        <TrendingUp className="w-4 h-4 text-teal-600 dark:text-teal-400" />
        Chat Sentiment
      </h3>
      <div className="space-y-3">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-zinc-600 dark:text-zinc-400">Positive</span>
            <span className="font-semibold text-emerald-600 dark:text-emerald-400">
              {sentiment.positive_chats} ({pct(sentiment.positive_chats)}%)
            </span>
          </div>
          <div className="w-full bg-zinc-100 dark:bg-zinc-700 rounded-full h-2">
            <div
              className="bg-emerald-500 h-2 rounded-full transition-all"
              style={{ width: `${pct(sentiment.positive_chats)}%` }}
            />
          </div>
        </div>
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-zinc-600 dark:text-zinc-400">Neutral</span>
            <span className="font-semibold text-zinc-600 dark:text-zinc-400">
              {sentiment.neutral_chats} ({pct(sentiment.neutral_chats)}%)
            </span>
          </div>
          <div className="w-full bg-zinc-100 dark:bg-zinc-700 rounded-full h-2">
            <div
              className="bg-zinc-400 h-2 rounded-full transition-all"
              style={{ width: `${pct(sentiment.neutral_chats)}%` }}
            />
          </div>
        </div>
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-zinc-600 dark:text-zinc-400">Negative</span>
            <span className="font-semibold text-red-600 dark:text-red-400">
              {sentiment.negative_chats} ({pct(sentiment.negative_chats)}%)
            </span>
          </div>
          <div className="w-full bg-zinc-100 dark:bg-zinc-700 rounded-full h-2">
            <div
              className="bg-red-500 h-2 rounded-full transition-all"
              style={{ width: `${pct(sentiment.negative_chats)}%` }}
            />
          </div>
        </div>
      </div>
      <div className="mt-4 pt-3 border-t border-zinc-100 dark:border-zinc-700">
        <div className="flex justify-between text-sm">
          <span className="text-zinc-500 dark:text-zinc-400">Avg Score</span>
          <span className="font-semibold text-zinc-900 dark:text-white">
            {sentiment.average_sentiment_score.toFixed(2)}
          </span>
        </div>
      </div>
    </div>
  );
}

function TopTopicsCard({
  topics,
}: {
  topics: EnhancedChatAnalytics["top_topics"];
}) {
  if (!topics || topics.length === 0) return null;

  const maxCount = Math.max(...topics.map((t) => t.count as number));

  return (
    <div className="bg-white dark:bg-[#1E2530] rounded-xl border border-zinc-200 dark:border-zinc-700 p-5 shadow-sm">
      <h3 className="text-sm font-semibold text-zinc-900 dark:text-white mb-4 flex items-center gap-2">
        <BarChart3 className="w-4 h-4 text-purple-600 dark:text-purple-400" />
        Top Topics
      </h3>
      <div className="space-y-2.5">
        {topics.map((t) => (
          <div key={t.topic as string}>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-zinc-700 dark:text-zinc-300 truncate max-w-[70%]">
                {(t.topic as string).replace(/_/g, " ")}
              </span>
              <span className="font-semibold text-zinc-900 dark:text-white">{t.count}</span>
            </div>
            <div className="w-full bg-zinc-100 dark:bg-zinc-700 rounded-full h-1.5">
              <div
                className="bg-purple-500 h-1.5 rounded-full transition-all"
                style={{
                  width: `${maxCount > 0 ? ((t.count as number) / maxCount) * 100 : 0}%`,
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
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
      <div className="bg-white dark:bg-[#1E2530] rounded-2xl w-full max-w-2xl max-h-[80vh] flex flex-col shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-zinc-200 dark:border-zinc-700">
          <div>
            <h2 className="text-lg font-bold text-zinc-900 dark:text-white">Chat Details</h2>
            <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
              {formatDate(chat.started_at)}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-zinc-100 dark:hover:bg-zinc-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-zinc-500 dark:text-zinc-400" />
          </button>
        </div>

        {/* Chat info */}
        <div className="p-4 bg-zinc-50 dark:bg-[#232A35] border-b border-zinc-200 dark:border-zinc-700 flex flex-wrap gap-4 text-sm">
          <div>
            <span className="text-zinc-500 dark:text-zinc-400">Messages:</span>{" "}
            <span className="font-semibold text-zinc-900 dark:text-white">
              {chat.total_messages}
            </span>
          </div>
          {chat.intent && (
            <div>
              <span className="text-zinc-500 dark:text-zinc-400">Intent:</span>{" "}
              <span className="font-semibold text-zinc-900 dark:text-white">{chat.intent}</span>
            </div>
          )}
          {chat.analysis && (
            <>
              <div>
                <span className="text-zinc-500 dark:text-zinc-400">Sentiment:</span>{" "}
                <SentimentBadge sentiment={chat.analysis.sentiment} />
              </div>
              <div>
                <span className="text-zinc-500 dark:text-zinc-400">Resolution:</span>{" "}
                <ResolutionBadge status={chat.analysis.resolution_status} />
              </div>
            </>
          )}
        </div>

        {/* Analysis section */}
        {chat.analysis && (
          <div className="p-4 bg-teal-50/50 dark:bg-teal-900/10 border-b border-zinc-200 dark:border-zinc-700 space-y-3">
            <p className="text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase">
              AI Analysis
            </p>
            {chat.analysis.key_points.length > 0 && (
              <div>
                <p className="text-xs font-medium text-zinc-600 dark:text-zinc-400 mb-1">Key Points:</p>
                <ul className="list-disc list-inside text-sm text-zinc-700 dark:text-zinc-300 space-y-0.5">
                  {chat.analysis.key_points.map((point, i) => (
                    <li key={i}>{point}</li>
                  ))}
                </ul>
              </div>
            )}
            {chat.analysis.suggested_followup && (
              <div>
                <p className="text-xs font-medium text-zinc-600 dark:text-zinc-400 mb-1">
                  Suggested Follow-up:
                </p>
                <p className="text-sm text-zinc-700 dark:text-zinc-300">
                  {chat.analysis.suggested_followup}
                </p>
              </div>
            )}
            <div className="flex flex-wrap gap-2">
              <span className="text-xs text-zinc-500 dark:text-zinc-400">
                Satisfaction: <span className="font-medium text-zinc-700 dark:text-zinc-300">{chat.analysis.user_satisfaction}</span>
              </span>
              <span className="text-xs text-zinc-500 dark:text-zinc-400">
                Topic: <span className="font-medium text-zinc-700 dark:text-zinc-300">{chat.analysis.primary_topic.replace(/_/g, " ")}</span>
              </span>
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {chat.messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.role !== "user" && (
                <div className="w-8 h-8 rounded-full bg-teal-100 dark:bg-teal-900/30 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-teal-600 dark:text-teal-400" />
                </div>
              )}
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-2.5 ${
                  msg.role === "user"
                    ? "bg-teal-600 text-white"
                    : "bg-zinc-100 dark:bg-[#232A35] text-zinc-900 dark:text-zinc-200"
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
                <div className="w-8 h-8 rounded-full bg-zinc-200 dark:bg-zinc-700 flex items-center justify-center flex-shrink-0">
                  <User className="w-4 h-4 text-zinc-600 dark:text-zinc-400" />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Summary */}
        {chat.summary && (
          <div className="p-4 border-t border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-[#232A35]">
            <p className="text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase mb-1">
              Summary
            </p>
            <p className="text-sm text-zinc-700 dark:text-zinc-300">{chat.summary}</p>
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
    <tr className="hover:bg-zinc-50 dark:hover:bg-[#252D3A] transition-colors">
      <td className="px-4 py-3 text-sm text-zinc-900 dark:text-zinc-200" suppressHydrationWarning>
        {formatDate(chat.started_at)}
      </td>
      <td className="px-4 py-3 text-sm text-zinc-900 dark:text-zinc-200 text-center">
        {chat.total_messages}
      </td>
      <td className="px-4 py-3">
        <SentimentBadge sentiment={chat.sentiment} />
      </td>
      <td className="px-4 py-3">
        {chat.primary_topic ? (
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400">
            {chat.primary_topic.replace(/_/g, " ")}
          </span>
        ) : chat.intent ? (
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400">
            {chat.intent}
          </span>
        ) : (
          <span className="text-zinc-400 text-sm">-</span>
        )}
      </td>
      <td className="px-4 py-3">
        <ResolutionBadge status={chat.resolution_status} />
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
    <div className="flex items-center justify-between px-4 py-3 border-t border-zinc-200 dark:border-zinc-700">
      <p className="text-sm text-zinc-500 dark:text-zinc-400">
        Page {page} of {totalPages}
      </p>
      <div className="flex gap-2">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
          className="px-3 py-1.5 text-sm font-medium rounded-lg border border-zinc-200 dark:border-zinc-600 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages}
          className="px-3 py-1.5 text-sm font-medium rounded-lg border border-zinc-200 dark:border-zinc-600 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
        </button>
      </div>
    </div>
  );
}

export default function ChatHistoryPage() {
  const [chats, setChats] = useState<ChatLogsResponse | null>(null);
  const [analytics, setAnalytics] = useState<EnhancedChatAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [selectedChat, setSelectedChat] = useState<ChatLogDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [chatData, analyticsData] = await Promise.all([
        getChatLogs(page, 20),
        getChatAnalytics(),
      ]);
      setChats(chatData);
      setAnalytics(analyticsData);
    } catch (err) {
      console.error("Failed to fetch chat data:", err);
      setError("Failed to load chat data. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

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
        <h1 className="text-3xl font-nunito font-bold text-zinc-900 dark:text-white flex items-center gap-3">
          <MessageCircle className="w-8 h-8 text-teal-600" />
          Chat History
        </h1>
        <p className="text-zinc-600 dark:text-zinc-400 mt-1">
          Chat analytics and conversation history
        </p>
      </div>

      {loading && !chats ? (
        <div className="bg-white dark:bg-[#1E2530] rounded-xl border border-zinc-200 dark:border-zinc-700 p-12 shadow-sm flex items-center justify-center">
          <Loader2 className="w-8 h-8 text-teal-600 animate-spin" />
        </div>
      ) : error ? (
        <div className="bg-white dark:bg-[#1E2530] rounded-xl border border-zinc-200 dark:border-zinc-700 p-12 shadow-sm text-center">
          <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
          >
            Retry
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Stats Cards Row */}
          {analytics && (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
              <StatsCard
                title="Total Chats"
                value={analytics.total_chats}
                subtitle={`+${analytics.chats_today} today`}
                icon={MessageCircle}
                color="teal"
              />
              <StatsCard
                title="Avg Messages"
                value={analytics.average_messages_per_chat.toFixed(1)}
                icon={BarChart3}
                color="blue"
              />
              <StatsCard
                title="Resolution Rate"
                value={
                  analytics.resolution_rate !== null
                    ? `${analytics.resolution_rate}%`
                    : "N/A"
                }
                icon={CheckCircle}
                color="emerald"
              />
              <StatsCard
                title="Active Sessions"
                value={analytics.active_sessions}
                icon={Activity}
                color="orange"
              />
              <StatsCard
                title="Analyzed"
                value={analytics.analyzed_count}
                subtitle={`of ${analytics.total_chats} total`}
                icon={TrendingUp}
                color="purple"
              />
            </div>
          )}

          {/* Two Column Layout: Sentiment + Topics */}
          {analytics && (analytics.sentiment || analytics.top_topics) && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ChatSentimentCard sentiment={analytics.sentiment} />
              <TopTopicsCard topics={analytics.top_topics} />
            </div>
          )}

          {/* Chat Logs Table */}
          {chats && chats.items.length === 0 ? (
            <div className="bg-white dark:bg-[#1E2530] rounded-xl border border-zinc-200 dark:border-zinc-700 p-12 shadow-sm text-center">
              <MessageCircle className="w-16 h-16 text-zinc-300 dark:text-zinc-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-zinc-900 dark:text-white mb-2">
                No Chats Yet
              </h2>
              <p className="text-zinc-600 dark:text-zinc-400">
                Chat conversations will appear here once customers start
                chatting.
              </p>
            </div>
          ) : chats ? (
            <div className="bg-white dark:bg-[#1E2530] rounded-xl border border-zinc-200 dark:border-zinc-700 shadow-sm overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="bg-zinc-50 dark:bg-[#232A35] border-b border-zinc-200 dark:border-zinc-700">
                    <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">
                      Time
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">
                      Messages
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">
                      Sentiment
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">
                      Topic
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">
                      Resolution
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-100 dark:divide-zinc-700">
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
        </div>
      )}

      {/* Loading overlay for detail */}
      {loadingDetail && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-[#1E2530] rounded-xl p-6 shadow-xl flex items-center gap-3">
            <Loader2 className="w-5 h-5 text-teal-600 animate-spin" />
            <span className="text-zinc-700 dark:text-zinc-300">Loading chat...</span>
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
