import useSWR from "swr";

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

const fetcher = (url: string) => fetch(url).then((r) => r.json());

export function useOrderbook(ticker: string) {
  const { data, error, isLoading } = useSWR<OrderbookResponse>(
    `http://localhost:8000/api/v1/orderbook/${ticker}`,
    fetcher,
    {
      refreshInterval: 700,
      dedupingInterval: 300,
    }
  );

  return {
    bids: data?.bids ?? [],
    asks: data?.asks ?? [],
    ticker: data?.ticker,
    isLoading,
    isError: error,
  };
}
