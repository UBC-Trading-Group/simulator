import React, { createContext, useContext, useCallback, useMemo, useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

interface WebSocketContextType {
  latencyMs: number | null;
  isConnected: boolean;
  isReconnecting: boolean;
  prices: Record<string, number>;
  lastUpdated: Date | null;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

// (?) global context so all components can use a centralized WS connection
// for example header can access latency, etc while price ticker can access prices
export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [prices, setPrices] = useState<Record<string, number>>({});
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const wsUrl = useMemo(() => {
    const envUrl = import.meta.env.VITE_WS_URL as string | undefined;
    if (envUrl) return envUrl;
    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = window.location.hostname || 'localhost';
    return `${proto}://${host}:8000/ws/market`;
  }, []);

  const handleMessage = useCallback((data: any) => {
    console.log(data);
    try {
      const priceData = data;
      // update the global context state for prices, maybe can create a type later ?
      for (const [ticker, price] of Object.entries(priceData) as [string, number][]) {
        setPrices(prev => ({
          ...prev,
          [ticker]: price
        }));
      }
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error parsing price data:', error);
    }
  }, []);

  const { latencyMs, isConnected, isReconnecting } = useWebSocket({
    url: wsUrl,
    onMessage: handleMessage,
    pingInterval: 5000,
    maxRetries: 5,
    initialBackoff: 500,
    maxBackoff: 10000,
  });

  return (
    <WebSocketContext.Provider
      value={{
        latencyMs,
        isConnected,
        isReconnecting,
        prices,
        lastUpdated,
      }}
    >
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocketContext = () => {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocketContext must be used within a WebSocketProvider');
  }
  return context;
};
