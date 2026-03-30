"""Small fallback ticker map used when SEC ticker file is temporarily unreachable."""

FALLBACK_COMPANIES = [
    {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
    {"cik_str": 1045810, "ticker": "NVDA", "title": "NVIDIA CORP"},
    {"cik_str": 1318605, "ticker": "TSLA", "title": "Tesla, Inc."},
    {"cik_str": 789019, "ticker": "MSFT", "title": "MICROSOFT CORP"},
    {"cik_str": 1652044, "ticker": "GOOGL", "title": "Alphabet Inc."},
    {"cik_str": 1018724, "ticker": "AMZN", "title": "AMAZON COM INC"},
    {"cik_str": 1326801, "ticker": "META", "title": "Meta Platforms, Inc."},
]
