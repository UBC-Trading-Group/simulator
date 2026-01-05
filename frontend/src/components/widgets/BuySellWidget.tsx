import React, { useState, useMemo, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useWebSocketContext } from '../../contexts/WebSocketContext';
import { getApiBaseUrl } from '../../config/api';
import { focusStyles, palette, widgetStyles } from './buySellStyles';
import {
  formatPrice,
  isValidPrice,
  isValidQuantity,
} from './tradeHelpers';
import type {
  OrderBookSnapshot,
  PortfolioPosition,
} from './tradeHelpers';

const BuySellWidget: React.FC = () => {
  const { token, isAuthenticated } = useAuth();
  const { prices } = useWebSocketContext();

  const [selectedTicker, setSelectedTicker] = useState<string>('');
  const [quantity, setQuantity] = useState<string>('12');
  const [limitPrice, setLimitPrice] = useState<string>('0');
  const [hasUserEditedLimit, setHasUserEditedLimit] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [positions, setPositions] = useState<PortfolioPosition[]>([]);
  const [orderBook, setOrderBook] = useState<OrderBookSnapshot | null>(null);
  const [isLoadingBook, setIsLoadingBook] = useState(false);
  const [bookError, setBookError] = useState<string | null>(null);

  // Fetch portfolio to prime available tickers list
  useEffect(() => {
    if (!isAuthenticated || !token) {
      setPositions([]);
      return;
    }

    let isCancelled = false;

    const fetchPortfolio = async () => {
      try {
        const response = await fetch(`${getApiBaseUrl()}/portfolio/`, {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
        if (!response.ok) {
          return;
        }
        const data = await response.json();
        if (!isCancelled && Array.isArray(data?.positions)) {
          setPositions(data.positions);
        }
      } catch (err) {
        // Silent fail; widget still works off websocket data
        if (!isCancelled) {
          console.error('Failed to load portfolio', err);
        }
      }
    };

    fetchPortfolio();
    const interval = setInterval(fetchPortfolio, 5000);
    return () => {
      isCancelled = true;
      clearInterval(interval);
    };
  }, [isAuthenticated, token]);

  // Get available tickers from WebSocket prices + portfolio positions
  const availableTickers = useMemo(() => {
    const tickers = new Set<string>();
    Object.keys(prices).forEach((t) => tickers.add(t));
    positions.forEach((pos) => tickers.add(pos.symbol));
    return Array.from(tickers).sort();
  }, [prices, positions]);

  // Get current price for selected ticker from WebSocket
  const currentPrice = useMemo(() => {
    if (!selectedTicker) return null;
    const livePrice = prices[selectedTicker];
    if (typeof livePrice === 'number') return livePrice;

    if (orderBook && orderBook.symbol === selectedTicker) {
      const fromBook =
        orderBook.mid_price ??
        orderBook.best_ask?.price ??
        orderBook.best_bid?.price ??
        null;
      return typeof fromBook === 'number' ? fromBook : null;
    }
    return null;
  }, [selectedTicker, prices, orderBook]);

  useEffect(() => {
    if (availableTickers.length > 0 && !selectedTicker) {
      setSelectedTicker(availableTickers[0]);
    }
  }, [availableTickers, selectedTicker]);

  // Require authentication to render trading controls
  if (!isAuthenticated) {
    return (
      <div
        style={{
          width: '100%',
          maxWidth: 420,
          border: '1px solid #E7E9F1',
          background: 'var(--color-white)',
          boxShadow: '0 25px 45px rgba(30, 33, 50, 0.08)',
          padding: '28px 28px 32px',
          borderRadius: 18,
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 16 }}>
          <h2 style={{ margin: 0, fontSize: 20, fontWeight: 700, color: '#1B212D' }}>
            Place Market Order
          </h2>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              borderRadius: 999,
              padding: '8px 14px',
              background: '#F4F6FB',
              color: '#2E354A',
              fontSize: 13,
              fontWeight: 600,
              letterSpacing: 0.5,
              textTransform: 'uppercase',
            }}
          >
            Login required
          </div>
        </div>
        <div style={{ marginTop: 16, fontSize: 14, color: '#98A1B4' }}>
          Please log in to view prices and place orders.
        </div>
      </div>
    );
  }

  // Load order book snapshot for the selected ticker
  useEffect(() => {
    if (!selectedTicker || !isAuthenticated || !token) {
      setOrderBook(null);
      return;
    }

    let isCancelled = false;

    const fetchOrderBook = async () => {
      setIsLoadingBook(true);
      setBookError(null);
      try {
        const response = await fetch(
          `${getApiBaseUrl()}/trading/orderbook/${selectedTicker}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          }
        );

        if (!response.ok) {
          const detail = await response.json().catch(() => ({}));
          throw new Error(detail.detail || 'Unable to load order book');
        }

        const data = (await response.json()) as OrderBookSnapshot;
        if (!isCancelled) {
          setOrderBook(data);
        }
      } catch (err) {
        if (!isCancelled) {
          setBookError(
            err instanceof Error ? err.message : 'Unable to load order book'
          );
          setOrderBook(null);
        }
      } finally {
        if (!isCancelled) {
          setIsLoadingBook(false);
        }
      }
    };

    fetchOrderBook();
    const interval = setInterval(fetchOrderBook, 3000);
    return () => {
      isCancelled = true;
      clearInterval(interval);
    };
  }, [selectedTicker, isAuthenticated, token]);

  // Prime limit price with the latest market price unless the user edits it
  useEffect(() => {
    setHasUserEditedLimit(false);
  }, [selectedTicker]);

  useEffect(() => {
    if (hasUserEditedLimit) return;
    if (currentPrice === null) return;
    setLimitPrice(currentPrice.toFixed(2));
  }, [currentPrice, hasUserEditedLimit, selectedTicker]);

  const submitMarketOrder = async (orderType: 'buy' | 'sell') => {
    if (!isAuthenticated || !token) {
      setError('Please log in to place orders');
      return;
    }

    if (!selectedTicker || !isValidQuantity(quantity)) {
      setError('Please select a ticker and enter a valid quantity');
      return;
    }

    if (currentPrice === null) {
      setError('Unable to get current market price. Please try again.');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`${getApiBaseUrl()}/trading/orders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          symbol: selectedTicker,
          quantity: parseInt(quantity, 10),
          side: orderType,
          order_type: 'market',
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to place order');
      }

      const data = await response.json();
      setSuccess(
        `Market order placed: ${orderType.toUpperCase()} ${quantity} ${selectedTicker} @ $${data.price?.toFixed(2) || formatPrice(currentPrice)}`
      );
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to place order'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const submitLimitOrder = async () => {
    if (!isAuthenticated || !token) {
      setError('Please log in to place orders');
      return;
    }

    if (
      !selectedTicker ||
      !isValidQuantity(quantity) ||
      !isValidPrice(limitPrice)
    ) {
      setError('Please fill in all fields with valid values');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`${getApiBaseUrl()}/trading/orders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          symbol: selectedTicker,
          quantity: parseInt(quantity, 10),
          side: 'buy',
          order_type: 'limit',
          price: parseFloat(limitPrice),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to place limit order');
      }

      const data = await response.json();
      setSuccess(
        `Limit order placed: ${quantity} ${selectedTicker} @ $${data.price?.toFixed(2) || limitPrice}`
      );
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to place limit order'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={widgetStyles.card}>
      {/* Header / status line */}
      <div style={widgetStyles.headerRow}>
        <h2 style={widgetStyles.title}>Place Market Order</h2>
        {currentPrice !== null && selectedTicker && (
          <div style={widgetStyles.statusPill}>
            <span>{selectedTicker}</span>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: palette.marketBuy, display: 'inline-block' }} />
            <span>${formatPrice(currentPrice)}</span>
          </div>
        )}
      </div>

      {/* Alerts */}
      {(error || success) && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {error && <div style={widgetStyles.alert(true)}>{error}</div>}
          {success && <div style={widgetStyles.alert(false)}>{success}</div>}
        </div>
      )}

      {/* Market order */}
      <section style={widgetStyles.section}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <h3 style={widgetStyles.sectionTitle}>Ticker</h3>
          <div style={widgetStyles.selectWrapper}>
            <select
              value={selectedTicker}
              onChange={(e) => setSelectedTicker(e.target.value)}
              style={{
                ...widgetStyles.input,
                appearance: 'none',
                cursor: 'pointer',
              }}
              disabled={isSubmitting || availableTickers.length === 0}
            >
              {availableTickers.length === 0 ? (
                <option value="">No tickers available</option>
              ) : (
                availableTickers.map((ticker) => (
                  <option key={ticker} value={ticker}>
                    {ticker}
                  </option>
                ))
              )}
            </select>
            <span style={widgetStyles.selectCaret}>▾</span>
          </div>
        </div>

        <div style={widgetStyles.fieldGroup}>
          <span style={widgetStyles.label}>Quantity</span>
          <input
            type="number"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            min="1"
            step="1"
            style={widgetStyles.input}
            onFocus={(e) => Object.assign(e.currentTarget.style, focusStyles)}
            onBlur={(e) => Object.assign(e.currentTarget.style, widgetStyles.input)}
            disabled={isSubmitting}
          />
        </div>

        <div style={widgetStyles.fieldGroup}>
          <span style={widgetStyles.label}>Market Price</span>
          <div style={{ fontSize: 13, color: palette.secondaryText, marginBottom: 6 }}>
            {isLoadingBook && <span>Syncing order book...</span>}
            {!isLoadingBook && bookError && (
              <span style={{ color: palette.marketSell }}>{bookError}</span>
            )}
            {!isLoadingBook && !bookError && orderBook && (
              <span>
                Mid ${formatPrice(orderBook.mid_price ?? null)} • Bid{' '}
                {orderBook.best_bid
                  ? `$${formatPrice(orderBook.best_bid.price)} x ${orderBook.best_bid.quantity}`
                  : '—'}{' '}
                • Ask{' '}
                {orderBook.best_ask
                  ? `$${formatPrice(orderBook.best_ask.price)} x ${orderBook.best_ask.quantity}`
                  : '—'}
              </span>
            )}
          </div>
          <div style={widgetStyles.priceActions}>
            <button
              onClick={() => submitMarketOrder('buy')}
              disabled={
                currentPrice === null ||
                !isValidQuantity(quantity) ||
                isSubmitting ||
                !isAuthenticated
              }
              style={{
                ...widgetStyles.pillButton('buy'),
                opacity:
                  currentPrice === null ||
                  !isValidQuantity(quantity) ||
                  isSubmitting ||
                  !isAuthenticated
                    ? 0.6
                    : 1,
              }}
            >
              BUY @ ${formatPrice(currentPrice)}
            </button>
            <button
              onClick={() => submitMarketOrder('sell')}
              disabled={
                currentPrice === null ||
                !isValidQuantity(quantity) ||
                isSubmitting ||
                !isAuthenticated
              }
              style={{
                ...widgetStyles.pillButton('sell'),
                opacity:
                  currentPrice === null ||
                  !isValidQuantity(quantity) ||
                  isSubmitting ||
                  !isAuthenticated
                    ? 0.6
                    : 1,
              }}
            >
              SELL @ ${formatPrice(currentPrice)}
            </button>
          </div>
        </div>
      </section>

      <div style={widgetStyles.divider} />

      {/* Limit order */}
      <section style={widgetStyles.section}>
        <h3 style={widgetStyles.sectionTitle}>Place Limit Order</h3>

        <div style={widgetStyles.fieldGroup}>
          <span style={widgetStyles.label}>Quantity</span>
          <input
            type="number"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            min="1"
            step="1"
            style={widgetStyles.input}
            onFocus={(e) => Object.assign(e.currentTarget.style, focusStyles)}
            onBlur={(e) => Object.assign(e.currentTarget.style, widgetStyles.input)}
            disabled={isSubmitting}
          />
        </div>

        <div style={widgetStyles.fieldGroup}>
          <span style={widgetStyles.label}>Price</span>
          <div style={{ position: 'relative' }}>
            <span
              style={{
                position: 'absolute',
                left: 16,
                top: '50%',
                transform: 'translateY(-50%)',
                fontWeight: 600,
                color: palette.secondaryText,
              }}
            >
              $
            </span>
            <input
              type="number"
              value={limitPrice}
              onChange={(e) => {
                setLimitPrice(e.target.value);
                setHasUserEditedLimit(true);
              }}
              min="0"
              step="0.01"
              style={{ ...widgetStyles.input, paddingLeft: 34 }}
              onFocus={(e) => Object.assign(e.currentTarget.style, { ...focusStyles, paddingLeft: '34px' })}
              onBlur={(e) => Object.assign(e.currentTarget.style, { ...widgetStyles.input, paddingLeft: '34px' })}
              disabled={isSubmitting}
              placeholder="0.00"
            />
          </div>
        </div>

        <button
          onClick={submitLimitOrder}
          disabled={
            !isValidQuantity(quantity) ||
            !isValidPrice(limitPrice) ||
            isSubmitting ||
            !isAuthenticated
          }
          style={{
            ...widgetStyles.limitButton,
            opacity:
              !isValidQuantity(quantity) ||
              !isValidPrice(limitPrice) ||
              isSubmitting ||
              !isAuthenticated
                ? 0.6
                : 1,
          }}
        >
          {isSubmitting ? 'Placing Order...' : 'Place Limit Order'}
        </button>
      </section>
    </div>
  );
};

export default BuySellWidget;
