import useSWR from "swr";
import { getApiBaseUrl } from "../config/api";

export interface Order {
  ticker: string;
  price: number;
  quantity: number;
  user_id: string;
  order_id: string;
}

export interface OrderbookResponse {
  ticker: string;
  bids: Order[];
  asks: Order[];
}

const fetcher = (url: string) =>
  fetch(url).then((r) => {
    if (!r.ok) {
      throw new Error(`Orderbook fetch failed: ${r.status}`);
    }
    return r.json();
  });

export function useOrderbook(ticker: string) {
  const normalizedTicker = (ticker || "").trim().toUpperCase();
  const shouldFetch = normalizedTicker !== "";

  const { data, error, isLoading } = useSWR<OrderbookResponse>(
    shouldFetch ? `${getApiBaseUrl()}/orderbook/${encodeURIComponent(normalizedTicker)}` : null,
    fetcher,
    {
      refreshInterval: 700,
      dedupingInterval: 300,
    }
  );

  return {
    bids: data?.bids ?? [],
    asks: data?.asks ?? [],
    ticker: data?.ticker ?? normalizedTicker,
    isLoading,
    isError: error,
  };
}
