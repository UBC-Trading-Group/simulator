import useSWR from "swr";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export interface NewsItem {
  id: number;
  headline: string;
  description: string;
  magnitude_top?: number;
  magnitude_bottom?: number;
  decay_halflife_s?: number;
  ts_release_ms: number;
}

const fetcher = (url: string) =>
  fetch(url).then((r) => {
    if (!r.ok) {
      throw new Error(`News fetch failed: ${r.status}`);
    }
    return r.json();
  });

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
