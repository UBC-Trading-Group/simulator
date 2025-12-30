import useSWR from "swr";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export interface Instrument {
  id: string;
  full_name: string;
}

const fetcher = (url: string) =>
  fetch(url).then((r) => {
    if (!r.ok) {
      throw new Error(`Instrument fetch failed: ${r.status}`);
    }
    return r.json();
  });

export function useInstruments() {
  const { data, error, isLoading } = useSWR<Instrument[]>(
    `${API_BASE_URL}/portfolio/instruments`,
    fetcher,
    { dedupingInterval: 5000, refreshInterval: 15000 }
  );

  return {
    instruments: data ?? [],
    isLoading,
    isError: error,
  };
}
