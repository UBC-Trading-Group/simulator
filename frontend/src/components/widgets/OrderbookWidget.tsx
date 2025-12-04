import { useOrderbook } from "../../hooks/useOrderbook";

export default function OrderBook() {
  const { bids, asks } = useOrderbook("NOVA");

  return (
    <div>
      <div className="h-full bg-white dark:bg-dark-2 flex flex-col p-6">
        {/* Search and Filters */}
        <div className="flex items-center gap-3 mb-4 shrink-0">
          <div className="flex-1 relative">
            <svg className="w-5 h-5 text-gray-400 dark:text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input 
              type="text" 
              placeholder="Search Order Book"
              className="w-full pl-10 pr-4 py-2.5 bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-700 dark:text-gray-300 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-text-2 focus:border-transparent"
            />
          </div>
          <button className="px-4 py-2.5 bg-tg-brightred hover:opacity-90 text-white rounded-lg font-medium text-sm flex items-center gap-2 transition-colors">
            <span>×</span>
            <span>TRAX</span>
          </button>
          <button className="px-4 py-2.5 bg-tg-brightred hover:opacity-90 text-white rounded-lg font-medium text-sm flex items-center gap-2 transition-colors">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
            <span>Filters</span>
          </button>
        </div>

        {/* Order Book Table */}
        <div className="bg-white dark:bg-dark-2 rounded-lg shadow-sm dark:shadow-none border border-gray-200 dark:border-ui  flex flex-col flex-1">
          {/* Fixed Header */}
          <div className="bg-linear-to-r from-tg-brightred to-brand grid grid-cols-2 shrink-0">
            {/* BID Header */}
            <div className="px-6 py-4">
              <h2 className="text-white text-2xl font-bold mb-3">BID</h2>
              <div className="grid grid-cols-3 gap-4 text-white font-semibold text-sm">
                <div>Name</div>
                <div className="text-center">Quantity</div>
                <div className="text-right">Price</div>
              </div>
            </div>

            {/* ASK Header */}
            <div className="px-6 py-4">
              <h2 className="text-white text-2xl font-bold mb-3">ASK</h2>
              <div className="grid grid-cols-3 gap-4 text-white font-semibold text-sm">
                <div>Name</div>
                <div className="text-center">Quantity</div>
                <div className="text-right">Price</div>
              </div>
            </div>
          </div>

          {/* Scrollable Order Rows */}
          <div className="grid grid-cols-2 overflow-y-auto flex-1">
            {/* BID Side */}
            <div className="bg-white dark:bg-dark-2">
              {bids.map((order, index) => (
                <div 
                  key={`bid-${index}`}
                  className="px-6 py-4 border-b border-gray-100 dark:border-ui hover:backdrop-brightness-75 dark:hover:backdrop-brightness-125 transition-colors"
                >
                  <div className="grid grid-cols-3 gap-4 items-center">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gray-100 dark:bg-gray-800 rounded flex items-center justify-center shrink-0">
                        <span className="text-xs font-bold text-gray-700 dark:text-gray-300">{order.ticker}</span>
                      </div>
                      <div className="min-w-0">
                        <div className="text-gray-900 dark:text-white font-semibold text-sm">{order.ticker}</div>
                        {/* <div className="text-gray-400 text-xs truncate">{order.company}</div> */}
                      </div>
                    </div>
                    <div className="text-gray-600 dark:text-white text-center font-medium text-sm">
                      {order.quantity}
                    </div>
                    <div className="text-green-600 text-right font-semibold">
                      ${order.price.toFixed(2)}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* ASK Side */}
            <div className="bg-white dark:bg-dark-2 border-l border-gray-200 dark:border-ui">
              {asks.map((order, index) => (
                <div 
                  key={`ask-${index}`}
                  className="px-6 py-4 border-b border-gray-100 dark:border-ui hover:backdrop-brightness-75 dark:hover:backdrop-brightness-125  transition-colors"
                >
                  <div className="grid grid-cols-3 gap-4 items-center">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gray-100 dark:bg-gray-800 rounded flex items-center justify-center shrink-0">
                        <span className="text-xs font-bold text-gray-700 dark:text-gray-300">{order.ticker}</span>
                      </div>
                      <div className="min-w-0">
                        <div className="text-gray-900 dark:text-white font-semibold text-sm">{order.ticker}</div>
                        {/* <div className="text-gray-400 text-xs truncate">{order.company}</div> */}
                      </div>
                    </div>
                    <div className="text-gray-600 dark:text-white text-center font-medium text-sm">
                      {order.quantity}
                    </div>
                    <div className="text-red-500 text-right font-semibold">
                      ${order.price.toFixed(2)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
