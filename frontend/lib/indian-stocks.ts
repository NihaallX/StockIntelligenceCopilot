/**
 * Popular Indian stocks for autocomplete
 * Frontend-only list, no database needed
 * Users can still type ANY stock - this just helps with suggestions
 */

export interface StockSuggestion {
  ticker: string;
  name: string;
  exchange: 'NSE' | 'BSE';
}

export const POPULAR_INDIAN_STOCKS: StockSuggestion[] = [
  // Top Market Cap - Large Cap
  { ticker: 'RELIANCE.NS', name: 'Reliance Industries', exchange: 'NSE' },
  { ticker: 'TCS.NS', name: 'Tata Consultancy Services', exchange: 'NSE' },
  { ticker: 'HDFCBANK.NS', name: 'HDFC Bank', exchange: 'NSE' },
  { ticker: 'INFY.NS', name: 'Infosys', exchange: 'NSE' },
  { ticker: 'ICICIBANK.NS', name: 'ICICI Bank', exchange: 'NSE' },
  { ticker: 'HINDUNILVR.NS', name: 'Hindustan Unilever', exchange: 'NSE' },
  { ticker: 'BHARTIARTL.NS', name: 'Bharti Airtel', exchange: 'NSE' },
  { ticker: 'SBIN.NS', name: 'State Bank of India', exchange: 'NSE' },
  { ticker: 'KOTAKBANK.NS', name: 'Kotak Mahindra Bank', exchange: 'NSE' },
  { ticker: 'LT.NS', name: 'Larsen & Toubro', exchange: 'NSE' },
  { ticker: 'ITC.NS', name: 'ITC', exchange: 'NSE' },
  { ticker: 'AXISBANK.NS', name: 'Axis Bank', exchange: 'NSE' },
  { ticker: 'BAJFINANCE.NS', name: 'Bajaj Finance', exchange: 'NSE' },
  { ticker: 'ASIANPAINT.NS', name: 'Asian Paints', exchange: 'NSE' },
  { ticker: 'MARUTI.NS', name: 'Maruti Suzuki', exchange: 'NSE' },
  { ticker: 'TITAN.NS', name: 'Titan Company', exchange: 'NSE' },
  { ticker: 'SUNPHARMA.NS', name: 'Sun Pharma', exchange: 'NSE' },
  { ticker: 'ULTRACEMCO.NS', name: 'UltraTech Cement', exchange: 'NSE' },
  { ticker: 'NESTLEIND.NS', name: 'Nestle India', exchange: 'NSE' },
  { ticker: 'ADANIENT.NS', name: 'Adani Enterprises', exchange: 'NSE' },
  
  // IT Sector
  { ticker: 'WIPRO.NS', name: 'Wipro', exchange: 'NSE' },
  { ticker: 'HCLTECH.NS', name: 'HCL Technologies', exchange: 'NSE' },
  { ticker: 'TECHM.NS', name: 'Tech Mahindra', exchange: 'NSE' },
  { ticker: 'LTIM.NS', name: 'LTIMindtree', exchange: 'NSE' },
  { ticker: 'PERSISTENT.NS', name: 'Persistent Systems', exchange: 'NSE' },
  { ticker: 'COFORGE.NS', name: 'Coforge', exchange: 'NSE' },
  { ticker: 'MPHASIS.NS', name: 'Mphasis', exchange: 'NSE' },
  { ticker: 'OFSS.NS', name: 'Oracle Financial Services', exchange: 'NSE' },
  { ticker: 'LTTS.NS', name: 'L&T Technology Services', exchange: 'NSE' },
  
  // Banking & Financial Services
  { ticker: 'INDUSINDBK.NS', name: 'IndusInd Bank', exchange: 'NSE' },
  { ticker: 'BAJAJFINSV.NS', name: 'Bajaj Finserv', exchange: 'NSE' },
  { ticker: 'HDFCLIFE.NS', name: 'HDFC Life Insurance', exchange: 'NSE' },
  { ticker: 'SBILIFE.NS', name: 'SBI Life Insurance', exchange: 'NSE' },
  { ticker: 'ICICIGI.NS', name: 'ICICI Lombard', exchange: 'NSE' },
  { ticker: 'ICICIPRULI.NS', name: 'ICICI Prudential Life', exchange: 'NSE' },
  { ticker: 'BAJAJHLDNG.NS', name: 'Bajaj Holdings', exchange: 'NSE' },
  { ticker: 'PNB.NS', name: 'Punjab National Bank', exchange: 'NSE' },
  { ticker: 'BANKBARODA.NS', name: 'Bank of Baroda', exchange: 'NSE' },
  { ticker: 'FEDERALBNK.NS', name: 'Federal Bank', exchange: 'NSE' },
  { ticker: 'IDFCFIRSTB.NS', name: 'IDFC First Bank', exchange: 'NSE' },
  { ticker: 'AUBANK.NS', name: 'AU Small Finance Bank', exchange: 'NSE' },
  { ticker: 'BANDHANBNK.NS', name: 'Bandhan Bank', exchange: 'NSE' },
  
  // Auto & Auto Components
  { ticker: 'TATAMOTORS.NS', name: 'Tata Motors', exchange: 'NSE' },
  { ticker: 'M&M.NS', name: 'Mahindra & Mahindra', exchange: 'NSE' },
  { ticker: 'BAJAJ-AUTO.NS', name: 'Bajaj Auto', exchange: 'NSE' },
  { ticker: 'HEROMOTOCO.NS', name: 'Hero MotoCorp', exchange: 'NSE' },
  { ticker: 'EICHERMOT.NS', name: 'Eicher Motors', exchange: 'NSE' },
  { ticker: 'TVSMOTOR.NS', name: 'TVS Motor', exchange: 'NSE' },
  { ticker: 'BOSCHLTD.NS', name: 'Bosch', exchange: 'NSE' },
  { ticker: 'MOTHERSON.NS', name: 'Samvardhana Motherson', exchange: 'NSE' },
  { ticker: 'APOLLOTYRE.NS', name: 'Apollo Tyres', exchange: 'NSE' },
  { ticker: 'MRF.NS', name: 'MRF', exchange: 'NSE' },
  { ticker: 'ESCORTS.NS', name: 'Escorts Kubota', exchange: 'NSE' },
  
  // Pharma & Healthcare
  { ticker: 'DRREDDY.NS', name: 'Dr Reddy\'s Labs', exchange: 'NSE' },
  { ticker: 'CIPLA.NS', name: 'Cipla', exchange: 'NSE' },
  { ticker: 'DIVISLAB.NS', name: 'Divi\'s Laboratories', exchange: 'NSE' },
  { ticker: 'APOLLOHOSP.NS', name: 'Apollo Hospitals', exchange: 'NSE' },
  { ticker: 'BIOCON.NS', name: 'Biocon', exchange: 'NSE' },
  { ticker: 'AUROPHARMA.NS', name: 'Aurobindo Pharma', exchange: 'NSE' },
  { ticker: 'ALKEM.NS', name: 'Alkem Laboratories', exchange: 'NSE' },
  { ticker: 'TORNTPHARM.NS', name: 'Torrent Pharma', exchange: 'NSE' },
  { ticker: 'LUPIN.NS', name: 'Lupin', exchange: 'NSE' },
  { ticker: 'ZYDUSLIFE.NS', name: 'Zydus Lifesciences', exchange: 'NSE' },
  
  // FMCG & Consumer
  { ticker: 'BRITANNIA.NS', name: 'Britannia Industries', exchange: 'NSE' },
  { ticker: 'DABUR.NS', name: 'Dabur India', exchange: 'NSE' },
  { ticker: 'MARICO.NS', name: 'Marico', exchange: 'NSE' },
  { ticker: 'GODREJCP.NS', name: 'Godrej Consumer', exchange: 'NSE' },
  { ticker: 'COLPAL.NS', name: 'Colgate Palmolive', exchange: 'NSE' },
  { ticker: 'TATACONSUM.NS', name: 'Tata Consumer Products', exchange: 'NSE' },
  { ticker: 'VARUN.NS', name: 'Varun Beverages', exchange: 'NSE' },
  { ticker: 'PGHH.NS', name: 'Procter & Gamble Hygiene', exchange: 'NSE' },
  { ticker: 'EMAMILTD.NS', name: 'Emami', exchange: 'NSE' },
  { ticker: 'RADICO.NS', name: 'Radico Khaitan', exchange: 'NSE' },
  
  // Energy & Power
  { ticker: 'ONGC.NS', name: 'ONGC', exchange: 'NSE' },
  { ticker: 'NTPC.NS', name: 'NTPC', exchange: 'NSE' },
  { ticker: 'POWERGRID.NS', name: 'Power Grid Corporation', exchange: 'NSE' },
  { ticker: 'BPCL.NS', name: 'Bharat Petroleum', exchange: 'NSE' },
  { ticker: 'IOC.NS', name: 'Indian Oil Corporation', exchange: 'NSE' },
  { ticker: 'GAIL.NS', name: 'GAIL India', exchange: 'NSE' },
  { ticker: 'ADANIGREEN.NS', name: 'Adani Green Energy', exchange: 'NSE' },
  { ticker: 'ADANIPOWER.NS', name: 'Adani Power', exchange: 'NSE' },
  { ticker: 'TATAPOWER.NS', name: 'Tata Power', exchange: 'NSE' },
  { ticker: 'TORNTPOWER.NS', name: 'Torrent Power', exchange: 'NSE' },
  
  // Metals & Mining
  { ticker: 'TATASTEEL.NS', name: 'Tata Steel', exchange: 'NSE' },
  { ticker: 'HINDALCO.NS', name: 'Hindalco Industries', exchange: 'NSE' },
  { ticker: 'COALINDIA.NS', name: 'Coal India', exchange: 'NSE' },
  { ticker: 'JSWSTEEL.NS', name: 'JSW Steel', exchange: 'NSE' },
  { ticker: 'VEDL.NS', name: 'Vedanta', exchange: 'NSE' },
  { ticker: 'HINDZINC.NS', name: 'Hindustan Zinc', exchange: 'NSE' },
  { ticker: 'NMDC.NS', name: 'NMDC', exchange: 'NSE' },
  { ticker: 'SAIL.NS', name: 'SAIL', exchange: 'NSE' },
  { ticker: 'JINDALSTEL.NS', name: 'Jindal Steel & Power', exchange: 'NSE' },
  
  // Cement
  { ticker: 'GRASIM.NS', name: 'Grasim Industries', exchange: 'NSE' },
  { ticker: 'SHREECEM.NS', name: 'Shree Cement', exchange: 'NSE' },
  { ticker: 'AMBUJACEM.NS', name: 'Ambuja Cements', exchange: 'NSE' },
  { ticker: 'ACC.NS', name: 'ACC', exchange: 'NSE' },
  { ticker: 'DALMIACEM.NS', name: 'Dalmia Bharat', exchange: 'NSE' },
  
  // Infrastructure & Construction
  { ticker: 'ADANIPORTS.NS', name: 'Adani Ports & SEZ', exchange: 'NSE' },
  { ticker: 'DLF.NS', name: 'DLF', exchange: 'NSE' },
  { ticker: 'GODREJPROP.NS', name: 'Godrej Properties', exchange: 'NSE' },
  { ticker: 'OBEROIRLTY.NS', name: 'Oberoi Realty', exchange: 'NSE' },
  { ticker: 'PRESTIGE.NS', name: 'Prestige Estates', exchange: 'NSE' },
  { ticker: 'BRIGADE.NS', name: 'Brigade Enterprises', exchange: 'NSE' },
  { ticker: 'IPCALAB.NS', name: 'IPCA Laboratories', exchange: 'NSE' },
  
  // Telecom & Media
  { ticker: 'ZEEL.NS', name: 'Zee Entertainment', exchange: 'NSE' },
  { ticker: 'PVRINOX.NS', name: 'PVR INOX', exchange: 'NSE' },
  { ticker: 'DISHTV.NS', name: 'Dish TV', exchange: 'NSE' },
  
  // Retail & E-commerce
  { ticker: 'TRENT.NS', name: 'Trent', exchange: 'NSE' },
  { ticker: 'DMART.NS', name: 'Avenue Supermarts (DMart)', exchange: 'NSE' },
  { ticker: 'ABFRL.NS', name: 'Aditya Birla Fashion', exchange: 'NSE' },
  { ticker: 'SHOPERSTOP.NS', name: 'Shoppers Stop', exchange: 'NSE' },
  
  // Chemicals & Fertilizers
  { ticker: 'UPL.NS', name: 'UPL', exchange: 'NSE' },
  { ticker: 'SRF.NS', name: 'SRF', exchange: 'NSE' },
  { ticker: 'PIDILITIND.NS', name: 'Pidilite Industries', exchange: 'NSE' },
  { ticker: 'AARTI.NS', name: 'Aarti Industries', exchange: 'NSE' },
  { ticker: 'DEEPAKNTR.NS', name: 'Deepak Nitrite', exchange: 'NSE' },
  { ticker: 'CHAMBLFERT.NS', name: 'Chambal Fertilizers', exchange: 'NSE' },
  
  // Engineering & Capital Goods
  { ticker: 'ABB.NS', name: 'ABB India', exchange: 'NSE' },
  { ticker: 'SIEMENS.NS', name: 'Siemens', exchange: 'NSE' },
  { ticker: 'HAVELLS.NS', name: 'Havells India', exchange: 'NSE' },
  { ticker: 'VOLTAS.NS', name: 'Voltas', exchange: 'NSE' },
  { ticker: 'CUMMINSIND.NS', name: 'Cummins India', exchange: 'NSE' },
  { ticker: 'THERMAX.NS', name: 'Thermax', exchange: 'NSE' },
  { ticker: 'CROMPTON.NS', name: 'Crompton Greaves', exchange: 'NSE' },
  
  // Hotels & Tourism
  { ticker: 'INDHOTEL.NS', name: 'Indian Hotels', exchange: 'NSE' },
  { ticker: 'TAJGVK.NS', name: 'Taj GVK Hotels', exchange: 'NSE' },
  { ticker: 'LEMONTREE.NS', name: 'Lemon Tree Hotels', exchange: 'NSE' },
  
  // Mid-cap IT & Services
  { ticker: 'ZOMATO.NS', name: 'Zomato', exchange: 'NSE' },
  { ticker: 'NYKAA.NS', name: 'Nykaa (FSN E-Commerce)', exchange: 'NSE' },
  { ticker: 'PAYTM.NS', name: 'Paytm (One97 Communications)', exchange: 'NSE' },
  { ticker: 'POLICYBZR.NS', name: 'PolicyBazaar (PB Fintech)', exchange: 'NSE' },
  
  // Mid-cap Diversified
  { ticker: 'ADANIENSOL.NS', name: 'Adani Energy Solutions', exchange: 'NSE' },
  { ticker: 'ADANITRANS.NS', name: 'Adani Transmission', exchange: 'NSE' },
  { ticker: 'ADANIWILMAR.NS', name: 'Adani Wilmar', exchange: 'NSE' },
  { ticker: 'VEDL.NS', name: 'Vedanta', exchange: 'NSE' },
  { ticker: 'HINDZINC.NS', name: 'Hindustan Zinc', exchange: 'NSE' },
  
  // PSU Banks
  { ticker: 'CANBK.NS', name: 'Canara Bank', exchange: 'NSE' },
  { ticker: 'UNIONBANK.NS', name: 'Union Bank of India', exchange: 'NSE' },
  { ticker: 'INDIABANK.NS', name: 'Indian Bank', exchange: 'NSE' },
  
  // BSE Popular (Alternative Exchange)
  { ticker: 'RELIANCE.BO', name: 'Reliance Industries', exchange: 'BSE' },
  { ticker: 'TCS.BO', name: 'TCS', exchange: 'BSE' },
  { ticker: 'HDFCBANK.BO', name: 'HDFC Bank', exchange: 'BSE' },
  { ticker: 'INFY.BO', name: 'Infosys', exchange: 'BSE' },
  { ticker: 'ICICIBANK.BO', name: 'ICICI Bank', exchange: 'BSE' },
];

/**
 * Search stocks by name or ticker
 */
export function searchStocks(query: string): StockSuggestion[] {
  if (!query || query.length < 2) return [];
  
  const searchTerm = query.toLowerCase();
  
  return POPULAR_INDIAN_STOCKS.filter(stock => {
    // Match company name
    if (stock.name.toLowerCase().includes(searchTerm)) return true;
    
    // Match full ticker (e.g., "RELIANCE.NS")
    if (stock.ticker.toLowerCase().includes(searchTerm)) return true;
    
    // Match ticker WITHOUT suffix (e.g., "RELIANCE" matches "RELIANCE.NS")
    const tickerWithoutSuffix = stock.ticker.replace(/\.(NS|BO)$/i, '').toLowerCase();
    if (tickerWithoutSuffix.includes(searchTerm)) return true;
    
    return false;
  }).slice(0, 8); // Show max 8 results
}
