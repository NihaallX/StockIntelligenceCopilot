"use client";

import { useEffect, useState, useRef } from "react";
import { useAuth } from "@/lib/auth-context";
import { getPortfolioPositions, addPortfolioPosition, deletePortfolioPosition, validateTicker, getHistoricalPrice, PortfolioPosition } from "@/lib/api";
import { motion } from "framer-motion";
import { Plus, TrendingUp, TrendingDown, Info, Trash2, Loader2, Calendar, Sparkles } from "lucide-react";
import { searchStocks, StockSuggestion } from "@/lib/indian-stocks";
import { FieldLabel } from "@/components/ui/tooltip";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";

export default function PortfolioPage() {
  const { tokens } = useAuth();
  const [positions, setPositions] = useState<PortfolioPosition[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSlowLoading, setIsSlowLoading] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [addPositionError, setAddPositionError] = useState("");
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<{ id: string; ticker: string } | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [isFetchingPrice, setIsFetchingPrice] = useState(false);

  // Autocomplete state
  const [suggestions, setSuggestions] = useState<StockSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const tickerInputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  const [formData, setFormData] = useState({
    ticker: "",
    quantity: "",
    entryPrice: "",
    entryDate: new Date().toISOString().split("T")[0],
    notes: "",
  });

  useEffect(() => {
    loadPositions();
  }, [tokens]);

  // Click outside to close suggestions
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node) &&
        tickerInputRef.current &&
        !tickerInputRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const loadPositions = () => {
    if (tokens?.access_token) {
      setIsSlowLoading(false);
      const slowTimer = setTimeout(() => setIsSlowLoading(true), 3000);
      
      getPortfolioPositions(tokens.access_token)
        .then(setPositions)
        .catch(console.error)
        .finally(() => {
          clearTimeout(slowTimer);
          setIsLoading(false);
          setIsSlowLoading(false);
        });
    }
  };

  const handleAddPosition = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tokens?.access_token) return;

    setAddPositionError("");
    setIsValidating(true);
    
    try {
      // Validate ticker first
      const ticker = formData.ticker.toUpperCase();
      const validation = await validateTicker(tokens.access_token, ticker);
      
      if (!validation.valid) {
        setAddPositionError(validation.message);
        setIsValidating(false);
        return;
      }
      
      await addPortfolioPosition(
        tokens.access_token,
        ticker,
        parseFloat(formData.quantity),
        parseFloat(formData.entryPrice),
        formData.entryDate,
        formData.notes || undefined
      );
      setShowAddForm(false);
      setFormData({
        ticker: "",
        quantity: "",
        entryPrice: "",
        entryDate: new Date().toISOString().split("T")[0],
        notes: "",
      });
      loadPositions();
    } catch (error: any) {
      // Use categorized error messages
      if (error.getUserMessage) {
        setAddPositionError(error.getUserMessage());
      } else {
        setAddPositionError(error.message || "Failed to add position");
      }
      
      // Handle auth errors
      if (error.category === 'auth') {
        setTimeout(() => window.location.href = '/login', 2000);
      }
    } finally {
      setIsValidating(false);
    }
  };

  const handleFetchHistoricalPrice = async () => {
    if (!tokens?.access_token || !formData.ticker || !formData.entryDate) {
      setAddPositionError("Please enter ticker and date first");
      return;
    }

    setIsFetchingPrice(true);
    setAddPositionError("");

    try {
      const ticker = formData.ticker.toUpperCase();
      const result = await getHistoricalPrice(tokens.access_token, ticker, formData.entryDate);
      
      // Fill in the entry price
      setFormData({ ...formData, entryPrice: result.price.toFixed(2) });
      
      // Show success message briefly
      setAddPositionError(`✓ Fetched price for ${formData.entryDate}: ₹${result.price.toFixed(2)}`);
      setTimeout(() => setAddPositionError(""), 3000);
      
    } catch (error: any) {
      setAddPositionError(error.message || "Failed to fetch historical price");
    } finally {
      setIsFetchingPrice(false);
    }
  };

  const handleTickerInputChange = (value: string) => {
    setFormData({ ...formData, ticker: value.toUpperCase() });
    
    if (value.length >= 2) {
      const results = searchStocks(value);
      setSuggestions(results);
      setShowSuggestions(results.length > 0);
      setSelectedIndex(-1);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };

  const selectSuggestion = (suggestion: StockSuggestion) => {
    setFormData({ ...formData, ticker: suggestion.ticker });
    setShowSuggestions(false);
    setSuggestions([]);
    setSelectedIndex(-1);
  };

  const handleTickerKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestions || suggestions.length === 0) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev < suggestions.length - 1 ? prev + 1 : prev));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : -1));
    } else if (e.key === "Enter" && selectedIndex >= 0) {
      e.preventDefault();
      selectSuggestion(suggestions[selectedIndex]);
    } else if (e.key === "Escape") {
      setShowSuggestions(false);
      setSelectedIndex(-1);
    }
  };

  const handleDeletePosition = async (positionId: string, ticker: string) => {
    if (!tokens?.access_token) return;
    
    setConfirmDelete({ id: positionId, ticker });
  };

  const confirmDeletePosition = async () => {
    if (!confirmDelete || !tokens?.access_token) return;
    
    setDeletingId(confirmDelete.id);
    setConfirmDelete(null);
    
    try {
      await deletePortfolioPosition(tokens.access_token, confirmDelete.id);
      loadPositions();
    } catch (error: any) {
      console.error("Failed to delete position:", error);
      alert(error.message || "Failed to delete position");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <ConfirmDialog
        isOpen={!!confirmDelete}
        title="Delete Position"
        message={`Delete ${confirmDelete?.ticker} position? This cannot be undone.`}
        confirmLabel="Delete"
        cancelLabel="Cancel"
        onConfirm={confirmDeletePosition}
        onCancel={() => setConfirmDelete(null)}
        variant="danger"
      />
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold mb-2">Portfolio</h1>
          <p className="text-muted-foreground">Manage your investment positions</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => window.location.href = '/dashboard/portfolio/suggestions'}
            disabled={positions.length === 0}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
            title={positions.length === 0 ? "Add positions first" : "Get AI suggestions"}
          >
            <Sparkles className="w-4 h-4" />
            <span className="hidden sm:inline">AI Suggestions</span>
          </button>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity"
          >
            <Plus className="w-4 h-4" />
            Add Position
          </button>
        </div>
      </div>

      {/* Add Position Form */}
      {showAddForm && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          className="bg-card border border-border rounded-xl p-6"
        >
          <h3 className="text-lg font-semibold mb-2">Add New Position</h3>
          
          {/* Global Help Banner */}
          <div className="mb-4 p-3 bg-muted/50 rounded-lg flex items-start gap-2 text-sm text-muted-foreground">
            <Info className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <p>This is for tracking and analysis only. No trades are placed from here.</p>
          </div>
          
          <form onSubmit={handleAddPosition} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="relative">
              <FieldLabel 
                label="Ticker" 
                tooltip="The stock symbol used by the exchange, like RELIANCE.NS or TCS.NS. It represents shares you already own."
                required
              />
              <input
                ref={tickerInputRef}
                type="text"
                value={formData.ticker}
                onChange={(e) => handleTickerInputChange(e.target.value)}
                onKeyDown={handleTickerKeyDown}
                className="w-full px-4 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background"
                placeholder="RELIANCE.NS"
                required
              />
              
              {/* Autocomplete Dropdown */}
              {showSuggestions && suggestions.length > 0 && (
                <div
                  ref={suggestionsRef}
                  className="absolute z-50 w-full mt-2 bg-card border border-border rounded-lg shadow-lg max-h-64 overflow-y-auto"
                >
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={suggestion.ticker}
                      type="button"
                      onClick={() => selectSuggestion(suggestion)}
                      className={`w-full px-4 py-3 text-left hover:bg-accent transition-colors flex items-center justify-between ${
                        index === selectedIndex ? "bg-accent" : ""
                      }`}
                    >
                      <div className="flex-1">
                        <div className="font-semibold text-sm">{suggestion.name}</div>
                        <div className="text-xs text-muted-foreground">{suggestion.ticker}</div>
                      </div>
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded ${
                          suggestion.exchange === "NSE"
                            ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300"
                            : "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300"
                        }`}
                      >
                        {suggestion.exchange}
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>
            <div>
              <FieldLabel 
                label="Quantity" 
                tooltip="The number of shares of this stock you own."
                required
              />
              <input
                type="number"
                step="0.01"
                value={formData.quantity}
                onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                className="w-full px-4 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background"
                placeholder="10"
                required
              />
            </div>
            <div>
              <FieldLabel 
                label="Entry Price" 
                tooltip="The price you paid per share when you bought this stock. Used to calculate profit and loss."
                required
              />
              <input
                type="number"
                step="0.01"
                value={formData.entryPrice}
                onChange={(e) => setFormData({ ...formData, entryPrice: e.target.value })}
                className="w-full px-4 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background"
                placeholder="150.00"
                required
              />
            </div>
            <div>
              <FieldLabel 
                label="Entry Date" 
                tooltip="The date you bought this stock. An approximate date is okay."
                required
              />
              <div className="flex gap-2">
                <input
                  type="date"
                  value={formData.entryDate}
                  onChange={(e) => setFormData({ ...formData, entryDate: e.target.value })}
                  className="flex-1 px-4 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background"
                  required
                />
                <button
                  type="button"
                  onClick={handleFetchHistoricalPrice}
                  disabled={isFetchingPrice || !formData.ticker || !formData.entryDate}
                  className="px-4 py-2 bg-muted hover:bg-accent text-foreground rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 whitespace-nowrap"
                  title="Fetch the historical price for the entered date"
                >
                  {isFetchingPrice ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Calendar className="w-4 h-4" />
                  )}
                  <span className="hidden sm:inline">Fetch Price</span>
                </button>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                💡 Don't remember the price? Enter ticker and date, then click "Fetch Price"
              </p>
            </div>
            <div className="md:col-span-2">
              <FieldLabel 
                label="Notes" 
                tooltip="Optional notes for your reference, like why you bought this stock. Not used for analysis."
              />
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                className="w-full px-4 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background"
                placeholder="Position notes..."
                rows={3}
              />
            </div>
            <div className="md:col-span-2 flex gap-4">
              <button
                type="submit"
                disabled={isValidating}
                className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isValidating && <Loader2 className="w-4 h-4 animate-spin" />}
                {isValidating ? "Validating..." : "Add Position"}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowAddForm(false);
                  setAddPositionError("");
                }}
                className="px-6 py-2 border border-border rounded-lg hover:bg-accent transition-colors"
              >
                Cancel
              </button>
            </div>
            
            {addPositionError && (
              <div className="md:col-span-2 mt-2 p-3 bg-amber-50 dark:bg-amber-900/10 border border-amber-300 dark:border-amber-700 rounded-lg">
                <p className="text-sm text-muted-foreground">{addPositionError}</p>
              </div>
            )}
          </form>
        </motion.div>
      )}
      
      {isSlowLoading && (
        <div className="p-3 bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800 rounded-lg text-sm">
          <p className="text-muted-foreground">
            ⏱️ Loading portfolio data is taking longer than usual. Please wait...
          </p>
        </div>
      )}

      {/* Positions Table */}
      <div className="bg-card border border-border rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-semibold">Ticker</th>
                <th className="px-6 py-4 text-right text-sm font-semibold">Quantity</th>
                <th className="px-6 py-4 text-right text-sm font-semibold">Entry Price</th>
                <th className="px-6 py-4 text-right text-sm font-semibold">Cost Basis</th>
                <th className="px-6 py-4 text-right text-sm font-semibold">Current Price</th>
                <th className="px-6 py-4 text-right text-sm font-semibold">P&L</th>
                <th className="px-6 py-4 text-right text-sm font-semibold">P&L %</th>
                <th className="px-6 py-4 text-right text-sm font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-muted-foreground">
                    Loading positions...
                  </td>
                </tr>
              ) : positions.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-muted-foreground">
                    No positions yet. Add your first position to get started.
                  </td>
                </tr>
              ) : (
                positions.map((position) => {
                  const pnl = position.unrealized_pnl ? parseFloat(position.unrealized_pnl) : null;
                  const pnlPercent = position.unrealized_pnl_percent;
                  const isPositive = pnl !== null && pnl >= 0;

                  return (
                    <motion.tr
                      key={position.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="border-t border-border hover:bg-muted/30 transition-colors"
                    >
                      <td className="px-6 py-4">
                        <span className="font-semibold">{position.ticker}</span>
                      </td>
                      <td className="px-6 py-4 text-right">{position.quantity}</td>
                      <td className="px-6 py-4 text-right">
                        ₹{parseFloat(position.entry_price).toFixed(2)}
                      </td>
                      <td className="px-6 py-4 text-right">
                        ₹{parseFloat(position.cost_basis).toLocaleString('en-IN')}
                      </td>
                      <td className="px-6 py-4 text-right">
                        {position.current_price
                          ? `₹${parseFloat(position.current_price).toFixed(2)}`
                          : "-"}
                      </td>
                      <td className="px-6 py-4 text-right">
                        {pnl !== null ? (
                          <span className={isPositive ? "text-green-500" : "text-red-500"}>
                            {isPositive ? "+" : ""}₹{pnl.toLocaleString('en-IN')}
                          </span>
                        ) : (
                          "-"
                        )}
                      </td>
                      <td className="px-6 py-4 text-right">
                        {pnlPercent ? (
                          <div className="flex items-center justify-end gap-1">
                            {isPositive ? (
                              <TrendingUp className="w-4 h-4 text-green-500" />
                            ) : (
                              <TrendingDown className="w-4 h-4 text-red-500" />
                            )}
                            <span className={isPositive ? "text-green-500" : "text-red-500"}>
                              {isPositive ? "+" : ""}
                              {pnlPercent}%
                            </span>
                          </div>
                        ) : (
                          "-"
                        )}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => handleDeletePosition(position.id, position.ticker)}
                          disabled={deletingId === position.id}
                          className="inline-flex items-center justify-center w-8 h-8 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          title="Delete position"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </motion.tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
