import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface Position {
  symbol: string;
  full_name: string;
  sector: string;
  quantity: number;
  price: number;
  total_position: number;
  pnl: number;
  pnl_percentage: number;
}

interface PortfolioData {
  user_id: number;
  username: string;
  total_value: number;
  cash: number;
  positions: Position[];
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

function PortfolioWidget() {
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const { token, isAuthenticated } = useAuth();

  useEffect(() => {
    if (!isAuthenticated || !token) {
      setLoading(false);
      return;
    }

    const fetchPortfolio = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/portfolio/`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch portfolio');
        }

        const data = await response.json();
        setPortfolio(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchPortfolio();
    
    // Refresh every 5 seconds
    const interval = setInterval(fetchPortfolio, 5000);
    return () => clearInterval(interval);
  }, [token, isAuthenticated]);

  if (!isAuthenticated) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Portfolio</h3>
        <p className="text-gray-600 dark:text-gray-300">Please log in to view your portfolio.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Portfolio</h3>
        <p className="text-gray-600 dark:text-gray-300">Loading portfolio...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Portfolio</h3>
        <p className="text-red-600 dark:text-red-400">Error: {error}</p>
      </div>
    );
  }

  if (!portfolio || portfolio.positions.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Portfolio</h3>
        <p className="text-gray-600 dark:text-gray-300">No positions yet. Start trading to build your portfolio!</p>
      </div>
    );
  }

  const filteredPositions = portfolio.positions.filter(position =>
    position.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
    position.full_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
      <div className="p-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Portfolio</h3>
        
        {/* Search Bar */}
        <div className="mb-4">
          <input
            type="text"
            placeholder="Search Transactions"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Portfolio Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700">
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-300">Stock</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-300">Sector</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-300">Quantity</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-300">Price</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-300">Total Position</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-300">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredPositions.map((position) => (
                <tr key={position.symbol} className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="py-4 px-4">
                    <div>
                      <div className="font-semibold text-gray-900 dark:text-white">{position.symbol}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">{position.full_name}</div>
                    </div>
                  </td>
                  <td className="py-4 px-4 text-gray-700 dark:text-gray-300">{position.sector}</td>
                  <td className="py-4 px-4 text-right text-gray-900 dark:text-white">{position.quantity}</td>
                  <td className="py-4 px-4 text-right text-gray-900 dark:text-white">${position.price.toFixed(2)}</td>
                  <td className="py-4 px-4 text-right">
                    <div className="font-semibold text-gray-900 dark:text-white">${position.total_position.toFixed(2)}</div>
                    <div className={`text-sm ${position.pnl >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                      {position.pnl >= 0 ? '▲' : '▼'} ${Math.abs(position.pnl).toFixed(2)}
                    </div>
                  </td>
                  <td className="py-4 px-4 text-right">
                    <button className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded transition-colors">
                      Close All
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default PortfolioWidget;


