"""Symbol registry for the trading recommendations app.

Each instrument maps a friendly Arabic name to the symbol Yahoo Finance uses,
plus display metadata (category + number of decimals for price formatting).

Adding a new instrument is just a new entry in INSTRUMENTS.
"""

INSTRUMENTS = [
    # --- الذهب والفوركس ---
    {"id": "XAUUSD", "yahoo": "GC=F",     "name_ar": "الذهب",          "name_en": "Gold (XAU/USD)",   "category": "metals",  "decimals": 2},
    {"id": "XAGUSD", "yahoo": "SI=F",     "name_ar": "الفضة",          "name_en": "Silver (XAG/USD)", "category": "metals",  "decimals": 2},
    {"id": "EURUSD", "yahoo": "EURUSD=X", "name_ar": "يورو / دولار",   "name_en": "EUR/USD",          "category": "forex",   "decimals": 5},
    {"id": "GBPUSD", "yahoo": "GBPUSD=X", "name_ar": "باوند / دولار",  "name_en": "GBP/USD",          "category": "forex",   "decimals": 5},
    {"id": "USDJPY", "yahoo": "USDJPY=X", "name_ar": "دولار / ين",     "name_en": "USD/JPY",          "category": "forex",   "decimals": 3},

    # --- الكريبتو ---
    {"id": "BTCUSD", "yahoo": "BTC-USD",  "name_ar": "بيتكوين",        "name_en": "Bitcoin",          "category": "crypto",  "decimals": 2},
    {"id": "ETHUSD", "yahoo": "ETH-USD",  "name_ar": "إيثيريوم",       "name_en": "Ethereum",         "category": "crypto",  "decimals": 2},
    {"id": "SOLUSD", "yahoo": "SOL-USD",  "name_ar": "سولانا",         "name_en": "Solana",           "category": "crypto",  "decimals": 2},

    # --- المؤشرات ---
    {"id": "US30",   "yahoo": "^DJI",     "name_ar": "داو جونز",       "name_en": "Dow Jones (US30)", "category": "indices", "decimals": 2},
    {"id": "NAS100", "yahoo": "^NDX",     "name_ar": "ناسداك 100",     "name_en": "Nasdaq 100",       "category": "indices", "decimals": 2},
    {"id": "SPX500", "yahoo": "^GSPC",    "name_ar": "إس آند بي 500",  "name_en": "S&P 500",          "category": "indices", "decimals": 2},
]

CATEGORIES = {
    "metals":  "المعادن",
    "forex":   "الفوركس",
    "crypto":  "الكريبتو",
    "indices": "المؤشرات",
}

_BY_ID = {inst["id"]: inst for inst in INSTRUMENTS}


def get(symbol_id):
    """Return the instrument dict for an id, or None."""
    return _BY_ID.get(symbol_id)


def all_instruments():
    return list(INSTRUMENTS)
