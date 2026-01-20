// import PriceTicker from '../components/PriceTicker';

function HomePage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Welcome to Trading Simulator
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Real-time market data and trading simulation
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="md:col-span-2">
          {/* Main content can go here */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
              Market Overview
            </h2>
            <p className="text-gray-600 dark:text-gray-300">
              Interactive charts and market analysis coming soon...
            </p>
          </div>
        </div>

        {/* <div>
          <PriceTicker />
        </div> */}
      </div>
    </div>
  );
}

export default HomePage;
