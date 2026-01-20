import useSWR from "swr";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export interface NewsItem {
  id: number;
  headline: string;
  description: string;
  magnitude_top?: number;
  magnitude_bottom?: number;
  magnitude?: number;
  decay_halflife_s?: number;
  ts_release_ms: number;
  effect?: number;
  factors?: string[];
  age_seconds?: number;
}

export interface NewsStatus {
  sim_time_ms: number;
  sim_time_seconds: number;
  active_news_count: number;
  active_news_ids: number[];
}

const fetcher = (url: string, token?: string) =>
  fetch(url, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  }).then((r) => {
    if (!r.ok) {
      throw new Error(`News fetch failed: ${r.status}`);
    }
    return r.json();
  });

// Hook to get all news from database
export function useNews() {
  const { data, error, isLoading } = useSWR<{ news: NewsItem[] }>(
    `${API_BASE_URL}/news/all`,
    fetcher,
    {
      refreshInterval: 5000,
      dedupingInterval: 2000,
    }
  );

  return {
    news: data?.news ?? [],
    isLoading,
    isError: error,
  };
}

// Hook to get active news with details (requires auth)
export function useActiveNews() {
  const token = localStorage.getItem("token");
  
  const { data, error, isLoading } = useSWR<{
    active_news_count: number;
    active_news_ids: number[];
    news_details?: NewsItem[];
    sim_time_ms?: number;
  }>(
    token ? `${API_BASE_URL}/admin/debug/drift` : null,
    (url) => fetcher(url, token || undefined),
    {
      refreshInterval: 5000,
      dedupingInterval: 2000,
    }
  );

  return {
    activeNews: data?.news_details ?? [],
    simTimeSeconds: data?.sim_time_ms ? data.sim_time_ms / 1000 : 0,
    activeCount: data?.active_news_count ?? 0,
    isLoading,
    isError: error,
  };
}

// Hook to get news status (public)
export function useNewsStatus() {
  const { data, error, isLoading } = useSWR<NewsStatus>(
    `${API_BASE_URL}/news/status`,
    fetcher,
    {
      refreshInterval: 3000,
      dedupingInterval: 1000,
    }
  );

  return {
    status: data,
    isLoading,
    isError: error,
  };
}
