export interface OrderBookSnapshot {
  symbol: string;
  mid_price: number | null;
  best_bid: { price: number; quantity: number } | null;
  best_ask: { price: number; quantity: number } | null;
}

export interface PortfolioPosition {
  symbol: string;
  full_name: string;
  sector: string;
  quantity: number;
  price: number;
  total_position: number;
  pnl: number;
  pnl_percentage: number;
}

export function formatPrice(price: number | null): string {
  if (price === null || Number.isNaN(price)) return '—';
  return price.toFixed(2);
}

export function isValidPrice(price: string): boolean {
  const num = parseFloat(price);
  return !isNaN(num) && num > 0;
}

export function isValidQuantity(quantity: string): boolean {
  const num = parseInt(quantity, 10);
  return !isNaN(num) && num > 0 && Number.isInteger(num);
}

