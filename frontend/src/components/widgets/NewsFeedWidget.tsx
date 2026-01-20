import { useEffect, useState } from "react";

interface NewsItem {
  id: number;
  headline: string;
  description: string;
  magnitude: number;
  effect: number;
  factors: string[];
  age_seconds: number;
}

interface NewsStatus {
  sim_time_seconds: number;
  active_news_count: number;
  news_details?: NewsItem[];
}

function NewsFeedWidget() {
  const [newsStatus, setNewsStatus] = useState<NewsStatus | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchNews = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return;

      // Fetch news status from admin endpoint (has more details)
      const response = await fetch("http://localhost:8000/api/v1/admin/debug/drift", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setNewsStatus({
          sim_time_seconds: data.sim_time_ms ? data.sim_time_ms / 1000 : 0,
          active_news_count: data.active_news_count || 0,
          news_details: data.news_details || [],
        });
      }
      setLoading(false);
    } catch (error) {
      console.error("Error fetching news:", error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNews();
    const interval = setInterval(fetchNews, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}m ${secs}s`;
  };

  const getImpactColor = (effect: number) => {
    if (effect > 0.01) return "text-green-600";
    if (effect > 0.005) return "text-green-500";
    if (effect < -0.01) return "text-red-600";
    if (effect < -0.005) return "text-red-500";
    return "text-yellow-600";
  };

  const getImpactLabel = (effect: number) => {
    const pct = (effect * 100).toFixed(2);
    return effect >= 0 ? `+${pct}%` : `${pct}%`;
  };

  return (
    <div className="p-4 h-full flex flex-col">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-lg font-semibold">News Feed</h3>
        {newsStatus && (
          <span className="text-sm text-gray-500">
            Sim Time: {formatTime(newsStatus.sim_time_seconds)}
          </span>
        )}
      </div>

      {loading ? (
        <p className="text-gray-500">Loading news...</p>
      ) : newsStatus && newsStatus.active_news_count > 0 ? (
        <div className="flex-1 overflow-y-auto space-y-3">
          {newsStatus.news_details?.map((news) => (
            <div
              key={news.id}
              className="border-l-4 border-blue-500 pl-3 py-2 bg-gray-50 rounded"
            >
              <h4 className="font-semibold text-sm leading-tight mb-1">
                {news.headline}
              </h4>
              <p className="text-xs text-gray-600">{news.description}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="flex items-center justify-center h-full text-gray-500">
          <p>No active news. Waiting for market events...</p>
        </div>
      )}

      {newsStatus && newsStatus.active_news_count > 0 && (
        <div className="mt-3 pt-3 border-t text-xs text-gray-600">
          {newsStatus.active_news_count} active news event{newsStatus.active_news_count !== 1 ? "s" : ""} affecting the market
        </div>
      )}
    </div>
  );
}

export default NewsFeedWidget;


