"""Known company profiles used to normalize high-frequency company queries."""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class CompanyProfile:
    """Normalized company metadata used by curated and fallback sources."""

    ticker: str
    company_name: str
    aliases: tuple[str, ...]
    ir_url: str
    results_url: str | None = None


COMPANY_PROFILES: tuple[CompanyProfile, ...] = (
    CompanyProfile(
        ticker="TSLA",
        company_name="Tesla, Inc.",
        aliases=("tesla", "tsla"),
        ir_url="https://ir.tesla.com/",
        results_url="https://ir.tesla.com/press?page=1",
    ),
    CompanyProfile(
        ticker="AAPL",
        company_name="Apple Inc.",
        aliases=("apple", "aapl", "apple inc"),
        ir_url="https://investor.apple.com/",
        results_url="https://investor.apple.com/investor-relations/default.aspx",
    ),
    CompanyProfile(
        ticker="NVDA",
        company_name="NVIDIA Corporation",
        aliases=("nvidia", "nvda", "nvidia corporation"),
        ir_url="https://investor.nvidia.com/",
        results_url="https://investor.nvidia.com/financial-info/default.aspx",
    ),
    CompanyProfile(
        ticker="MSFT",
        company_name="Microsoft Corporation",
        aliases=("microsoft", "msft", "microsoft corporation"),
        ir_url="https://www.microsoft.com/en-us/Investor/",
        results_url="https://www.microsoft.com/en-us/Investor/earnings/default.aspx",
    ),
    CompanyProfile(
        ticker="AMZN",
        company_name="Amazon.com, Inc.",
        aliases=("amazon", "amzn", "amazoncom", "amazon.com"),
        ir_url="https://www.aboutamazon.com/investor-relations",
        results_url="https://www.aboutamazon.com/news/company-news",
    ),
    CompanyProfile(
        ticker="META",
        company_name="Meta Platforms, Inc.",
        aliases=("meta", "meta platforms", "facebook", "fb", "meta platforms inc"),
        ir_url="https://investor.atmeta.com/",
        results_url="https://investor.atmeta.com/investor-news/default.aspx",
    ),
    CompanyProfile(
        ticker="GOOGL",
        company_name="Alphabet Inc.",
        aliases=("alphabet", "google", "googl", "goog", "alphabet inc"),
        ir_url="https://abc.xyz/investor/",
        results_url="https://abc.xyz/investor/#quarterly-earnings",
    ),
    CompanyProfile(
        ticker="AMD",
        company_name="Advanced Micro Devices, Inc.",
        aliases=("amd", "advanced micro devices", "advanced micro devices inc"),
        ir_url="https://ir.amd.com/",
        results_url="https://ir.amd.com/news-events/press-releases",
    ),
    CompanyProfile(
        ticker="NFLX",
        company_name="Netflix, Inc.",
        aliases=("netflix", "nflx", "netflix inc"),
        ir_url="https://ir.netflix.net/",
        results_url="https://ir.netflix.net/financials/quarterly-earnings/default.aspx",
    ),
    CompanyProfile(
        ticker="PLTR",
        company_name="Palantir Technologies Inc.",
        aliases=("palantir", "pltr", "palantir technologies"),
        ir_url="https://investors.palantir.com/",
        results_url="https://investors.palantir.com/news-events",
    ),
    CompanyProfile(
        ticker="JPM",
        company_name="JPMorgan Chase & Co.",
        aliases=("jpm", "jpmorgan", "jpmorgan chase", "jpmorgan chase & co"),
        ir_url="https://www.jpmorganchase.com/ir",
        results_url="https://www.jpmorganchase.com/ir/news",
    ),
    CompanyProfile(
        ticker="BAC",
        company_name="Bank of America Corporation",
        aliases=("bac", "bank of america", "bank of america corporation"),
        ir_url="https://investor.bankofamerica.com/",
        results_url="https://investor.bankofamerica.com/quarterly-earnings",
    ),
    CompanyProfile(
        ticker="GS",
        company_name="The Goldman Sachs Group, Inc.",
        aliases=("gs", "goldman sachs", "goldman sachs group"),
        ir_url="https://www.goldmansachs.com/investor-relations/",
        results_url="https://www.goldmansachs.com/investor-relations/financials/current",
    ),
    CompanyProfile(
        ticker="XOM",
        company_name="Exxon Mobil Corporation",
        aliases=("xom", "exxon", "exxon mobil", "exxon mobil corporation"),
        ir_url="https://corporate.exxonmobil.com/investors",
        results_url="https://corporate.exxonmobil.com/news/results-and-presentations",
    ),
    CompanyProfile(
        ticker="CVX",
        company_name="Chevron Corporation",
        aliases=("cvx", "chevron", "chevron corporation"),
        ir_url="https://www.chevron.com/investors",
        results_url="https://www.chevron.com/investors/earnings",
    ),
    CompanyProfile(
        ticker="DIS",
        company_name="The Walt Disney Company",
        aliases=("dis", "disney", "walt disney", "the walt disney company"),
        ir_url="https://thewaltdisneycompany.com/investor-relations/",
        results_url="https://thewaltdisneycompany.com/app/uploads/earnings/",
    ),
    CompanyProfile(
        ticker="INTC",
        company_name="Intel Corporation",
        aliases=("intel", "intc", "intel corporation"),
        ir_url="https://www.intc.com/",
        results_url="https://www.intc.com/financial-info/financial-results/default.aspx",
    ),
    CompanyProfile(
        ticker="ORCL",
        company_name="Oracle Corporation",
        aliases=("oracle", "orcl", "oracle corporation"),
        ir_url="https://www.oracle.com/investor/",
        results_url="https://www.oracle.com/investor/financial-information/quarterly-results/",
    ),
    CompanyProfile(
        ticker="CRM",
        company_name="Salesforce, Inc.",
        aliases=("salesforce", "crm", "salesforce inc"),
        ir_url="https://investor.salesforce.com/",
        results_url="https://investor.salesforce.com/financials/default.aspx",
    ),
    CompanyProfile(
        ticker="ADBE",
        company_name="Adobe Inc.",
        aliases=("adobe", "adbe", "adobe inc"),
        ir_url="https://www.adobe.com/investor-relations.html",
        results_url="https://www.adobe.com/investor-relations/financial-documents.html",
    ),
    CompanyProfile(
        ticker="QCOM",
        company_name="QUALCOMM Incorporated",
        aliases=("qualcomm", "qcom", "qualcomm incorporated"),
        ir_url="https://investor.qualcomm.com/",
        results_url="https://investor.qualcomm.com/financial-information/default.aspx",
    ),
    CompanyProfile(
        ticker="AVGO",
        company_name="Broadcom Inc.",
        aliases=("broadcom", "avgo", "broadcom inc"),
        ir_url="https://investors.broadcom.com/",
        results_url="https://investors.broadcom.com/financial-information/quarterly-results",
    ),
    CompanyProfile(
        ticker="MU",
        company_name="Micron Technology, Inc.",
        aliases=("micron", "mu", "micron technology"),
        ir_url="https://investors.micron.com/",
        results_url="https://investors.micron.com/quarterly-results",
    ),
    CompanyProfile(
        ticker="PYPL",
        company_name="PayPal Holdings, Inc.",
        aliases=("paypal", "pypl", "paypal holdings"),
        ir_url="https://investor.pypl.com/",
        results_url="https://investor.pypl.com/financials/default.aspx",
    ),
    CompanyProfile(
        ticker="UBER",
        company_name="Uber Technologies, Inc.",
        aliases=("uber", "uber technologies", "uber technologies inc"),
        ir_url="https://investor.uber.com/",
        results_url="https://investor.uber.com/financial-information/default.aspx",
    ),
    CompanyProfile(
        ticker="SHOP",
        company_name="Shopify Inc.",
        aliases=("shopify", "shop", "shopify inc"),
        ir_url="https://investors.shopify.com/",
        results_url="https://investors.shopify.com/financial-reports/default.aspx",
    ),
    CompanyProfile(
        ticker="SNOW",
        company_name="Snowflake Inc.",
        aliases=("snowflake", "snow", "snowflake inc"),
        ir_url="https://investors.snowflake.com/",
        results_url="https://investors.snowflake.com/financial-info/default.aspx",
    ),
    CompanyProfile(
        ticker="COIN",
        company_name="Coinbase Global, Inc.",
        aliases=("coinbase", "coin", "coinbase global"),
        ir_url="https://investor.coinbase.com/",
        results_url="https://investor.coinbase.com/financials/default.aspx",
    ),
    CompanyProfile(
        ticker="BABA",
        company_name="Alibaba Group Holding Limited",
        aliases=("alibaba", "baba", "alibaba group"),
        ir_url="https://www.alibabagroup.com/en-US/ir-home",
        results_url="https://www.alibabagroup.com/en-US/ir-financial-results",
    ),
    CompanyProfile(
        ticker="PDD",
        company_name="PDD Holdings Inc.",
        aliases=("pdd", "pdd holdings", "pinduoduo"),
        ir_url="https://investor.pddholdings.com/",
        results_url="https://investor.pddholdings.com/financial-information/quarterly-results",
    ),
    CompanyProfile(
        ticker="TSM",
        company_name="Taiwan Semiconductor Manufacturing Company Limited",
        aliases=("tsm", "tsmc", "taiwan semiconductor", "taiwan semiconductor manufacturing"),
        ir_url="https://investor.tsmc.com/english",
        results_url="https://investor.tsmc.com/english/financial-calendar",
    ),
    CompanyProfile(
        ticker="ASML",
        company_name="ASML Holding N.V.",
        aliases=("asml", "asml holding"),
        ir_url="https://www.asml.com/en/investors",
        results_url="https://www.asml.com/en/investors/financial-results",
    ),
    CompanyProfile(
        ticker="NKE",
        company_name="NIKE, Inc.",
        aliases=("nike", "nke", "nike inc"),
        ir_url="https://investors.nike.com/",
        results_url="https://investors.nike.com/investors/news-events-and-reports/default.aspx",
    ),
    CompanyProfile(
        ticker="SBUX",
        company_name="Starbucks Corporation",
        aliases=("starbucks", "sbux", "starbucks corporation"),
        ir_url="https://investor.starbucks.com/",
        results_url="https://investor.starbucks.com/press-releases/default.aspx",
    ),
    CompanyProfile(
        ticker="WMT",
        company_name="Walmart Inc.",
        aliases=("walmart", "wmt", "walmart inc"),
        ir_url="https://stock.walmart.com/",
        results_url="https://stock.walmart.com/financials/default.aspx",
    ),
    CompanyProfile(
        ticker="COST",
        company_name="Costco Wholesale Corporation",
        aliases=("costco", "cost", "costco wholesale"),
        ir_url="https://investor.costco.com/",
        results_url="https://investor.costco.com/financial-information/default.aspx",
    ),
)


def normalize_company_query(value: str) -> str:
    """Normalize free-form company/ticker input for alias matching."""
    lowered = value.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def resolve_company_profile(query: str) -> CompanyProfile | None:
    """Resolve a user query to a known company profile when possible."""
    normalized = normalize_company_query(query)
    if not normalized:
        return None

    for profile in COMPANY_PROFILES:
        aliases = {normalize_company_query(alias) for alias in profile.aliases}
        aliases.add(normalize_company_query(profile.company_name))
        aliases.add(normalize_company_query(profile.ticker))
        if normalized in aliases:
            return profile

    for profile in COMPANY_PROFILES:
        aliases = {normalize_company_query(alias) for alias in profile.aliases}
        aliases.add(normalize_company_query(profile.company_name))
        if any(normalized in alias or alias in normalized for alias in aliases):
            return profile
    return None
