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
    CompanyProfile(
        ticker="TMO",
        company_name="Thermo Fisher Scientific Inc.",
        aliases=("thermo fisher", "tmo", "thermo fisher scientific"),
        ir_url="https://ir.thermofisher.com/",
        results_url="https://ir.thermofisher.com/financials/default.aspx",
    ),
    CompanyProfile(
        ticker="LLY",
        company_name="Eli Lilly and Company",
        aliases=("eli lilly", "lly", "lilly", "eli lilly and company"),
        ir_url="https://investor.lilly.com/",
        results_url="https://investor.lilly.com/financial-information/default.aspx",
    ),
    CompanyProfile(
        ticker="JNJ",
        company_name="Johnson & Johnson",
        aliases=("jnj", "johnson and johnson", "johnson & johnson"),
        ir_url="https://investor.jnj.com/",
        results_url="https://investor.jnj.com/financials/quarterly-results",
    ),
    CompanyProfile(
        ticker="UNH",
        company_name="UnitedHealth Group Incorporated",
        aliases=("unitedhealth", "unh", "unitedhealth group"),
        ir_url="https://www.unitedhealthgroup.com/investors.html",
        results_url="https://www.unitedhealthgroup.com/investors/financial-reports.html",
    ),
    CompanyProfile(
        ticker="ABBV",
        company_name="AbbVie Inc.",
        aliases=("abbvie", "abbv", "abbvie inc"),
        ir_url="https://investors.abbvie.com/",
        results_url="https://investors.abbvie.com/financial-results/default.aspx",
    ),
    CompanyProfile(
        ticker="MRK",
        company_name="Merck & Co., Inc.",
        aliases=("merck", "mrk", "merck and co", "merck & co"),
        ir_url="https://investors.merck.com/",
        results_url="https://investors.merck.com/financials-and-reports/default.aspx",
    ),
    CompanyProfile(
        ticker="PFE",
        company_name="Pfizer Inc.",
        aliases=("pfizer", "pfe", "pfizer inc"),
        ir_url="https://investors.pfizer.com/",
        results_url="https://investors.pfizer.com/financials/quarterly-results/default.aspx",
    ),
    CompanyProfile(
        ticker="KO",
        company_name="The Coca-Cola Company",
        aliases=("coca cola", "ko", "coke", "the coca cola company"),
        ir_url="https://investors.coca-colacompany.com/",
        results_url="https://investors.coca-colacompany.com/financial-information/quarterly-earnings/default.aspx",
    ),
    CompanyProfile(
        ticker="PEP",
        company_name="PepsiCo, Inc.",
        aliases=("pepsico", "pep", "pepsi", "pepsico inc"),
        ir_url="https://investors.pepsico.com/",
        results_url="https://investors.pepsico.com/investors/financial-information/default.aspx",
    ),
    CompanyProfile(
        ticker="MCD",
        company_name="McDonald's Corporation",
        aliases=("mcdonalds", "mcd", "mcdonald's", "mcdonald s"),
        ir_url="https://corporate.mcdonalds.com/corpmcd/investors.html",
        results_url="https://corporate.mcdonalds.com/corpmcd/investors/financial-information.html",
    ),
    CompanyProfile(
        ticker="HD",
        company_name="The Home Depot, Inc.",
        aliases=("home depot", "hd", "the home depot"),
        ir_url="https://ir.homedepot.com/",
        results_url="https://ir.homedepot.com/financial-reports/default.aspx",
    ),
    CompanyProfile(
        ticker="LOW",
        company_name="Lowe's Companies, Inc.",
        aliases=("lowes", "low", "lowe s", "lowe's"),
        ir_url="https://investor.lowes.com/",
        results_url="https://investor.lowes.com/financial-information/default.aspx",
    ),
    CompanyProfile(
        ticker="CAT",
        company_name="Caterpillar Inc.",
        aliases=("caterpillar", "cat", "caterpillar inc"),
        ir_url="https://investors.caterpillar.com/",
        results_url="https://investors.caterpillar.com/financials/default.aspx",
    ),
    CompanyProfile(
        ticker="GE",
        company_name="GE Aerospace",
        aliases=("ge", "general electric", "ge aerospace"),
        ir_url="https://www.geaerospace.com/investor-relations",
        results_url="https://www.geaerospace.com/investor-relations/financial-information",
    ),
    CompanyProfile(
        ticker="RTX",
        company_name="RTX Corporation",
        aliases=("rtx", "raytheon", "rtx corporation"),
        ir_url="https://investors.rtx.com/",
        results_url="https://investors.rtx.com/financial-information/default.aspx",
    ),
    CompanyProfile(
        ticker="HON",
        company_name="Honeywell International Inc.",
        aliases=("honeywell", "hon", "honeywell international"),
        ir_url="https://investor.honeywell.com/",
        results_url="https://investor.honeywell.com/financial/default.aspx",
    ),
    CompanyProfile(
        ticker="IBM",
        company_name="International Business Machines Corporation",
        aliases=("ibm", "international business machines"),
        ir_url="https://www.ibm.com/investor/",
        results_url="https://www.ibm.com/investor/att/pdf/IBM_Annual_Report.pdf",
    ),
    CompanyProfile(
        ticker="AMAT",
        company_name="Applied Materials, Inc.",
        aliases=("amat", "applied materials", "applied materials inc"),
        ir_url="https://ir.appliedmaterials.com/",
        results_url="https://ir.appliedmaterials.com/financial-information/default.aspx",
    ),
    CompanyProfile(
        ticker="LRCX",
        company_name="Lam Research Corporation",
        aliases=("lam research", "lrcx", "lam research corporation"),
        ir_url="https://investor.lamresearch.com/",
        results_url="https://investor.lamresearch.com/financials/default.aspx",
    ),
    CompanyProfile(
        ticker="TXN",
        company_name="Texas Instruments Incorporated",
        aliases=("texas instruments", "txn", "ti"),
        ir_url="https://investor.ti.com/",
        results_url="https://investor.ti.com/financial-information/default.aspx",
    ),
    CompanyProfile(
        ticker="BKNG",
        company_name="Booking Holdings Inc.",
        aliases=("booking", "bkng", "booking holdings", "booking.com"),
        ir_url="https://ir.bookingholdings.com/",
        results_url="https://ir.bookingholdings.com/financial-information/default.aspx",
    ),
    CompanyProfile(
        ticker="ABNB",
        company_name="Airbnb, Inc.",
        aliases=("airbnb", "abnb", "airbnb inc"),
        ir_url="https://investors.airbnb.com/",
        results_url="https://investors.airbnb.com/financials/default.aspx",
    ),
    CompanyProfile(
        ticker="MAR",
        company_name="Marriott International, Inc.",
        aliases=("marriott", "mar", "marriott international"),
        ir_url="https://marriott.gcs-web.com/",
        results_url="https://marriott.gcs-web.com/financial-information/default.aspx",
    ),
    CompanyProfile(
        ticker="V",
        company_name="Visa Inc.",
        aliases=("visa", "v", "visa inc"),
        ir_url="https://investor.visa.com/",
        results_url="https://investor.visa.com/financial-info/default.aspx",
    ),
    CompanyProfile(
        ticker="MA",
        company_name="Mastercard Incorporated",
        aliases=("mastercard", "ma", "mastercard incorporated"),
        ir_url="https://investor.mastercard.com/",
        results_url="https://investor.mastercard.com/financials/default.aspx",
    ),
    CompanyProfile(
        ticker="AXP",
        company_name="American Express Company",
        aliases=("american express", "axp", "amex"),
        ir_url="https://ir.americanexpress.com/",
        results_url="https://ir.americanexpress.com/financial-information/default.aspx",
    ),
    CompanyProfile(
        ticker="BLK",
        company_name="BlackRock, Inc.",
        aliases=("blackrock", "blk", "blackrock inc"),
        ir_url="https://ir.blackrock.com/",
        results_url="https://ir.blackrock.com/financials/default.aspx",
    ),
    CompanyProfile(
        ticker="MS",
        company_name="Morgan Stanley",
        aliases=("morgan stanley", "ms"),
        ir_url="https://www.morganstanley.com/about-us-ir",
        results_url="https://www.morganstanley.com/about-us-ir/earnings-releases",
    ),
    CompanyProfile(
        ticker="C",
        company_name="Citigroup Inc.",
        aliases=("citigroup", "citi", "c", "citigroup inc"),
        ir_url="https://www.citigroup.com/citi/investor/",
        results_url="https://www.citigroup.com/citi/investor/quarterly/2025.htm",
    ),
    CompanyProfile(
        ticker="WFC",
        company_name="Wells Fargo & Company",
        aliases=("wells fargo", "wfc", "wells fargo company"),
        ir_url="https://www.wellsfargo.com/about/investor-relations/",
        results_url="https://www.wellsfargo.com/about/investor-relations/quarterly-earnings/",
    ),
    CompanyProfile(
        ticker="SCHW",
        company_name="The Charles Schwab Corporation",
        aliases=("charles schwab", "schw", "schwab"),
        ir_url="https://www.aboutschwab.com/investor-relations",
        results_url="https://www.aboutschwab.com/investor-relations/quarterly-reports",
    ),
    CompanyProfile(
        ticker="SPGI",
        company_name="S&P Global Inc.",
        aliases=("spgi", "s&p global", "s and p global"),
        ir_url="https://investor.spglobal.com/",
        results_url="https://investor.spglobal.com/financials/default.aspx",
    ),
    CompanyProfile(
        ticker="INTU",
        company_name="Intuit Inc.",
        aliases=("intuit", "intu", "intuit inc"),
        ir_url="https://investors.intuit.com/",
        results_url="https://investors.intuit.com/financials/default.aspx",
    ),
    CompanyProfile(
        ticker="ADP",
        company_name="Automatic Data Processing, Inc.",
        aliases=("adp", "automatic data processing"),
        ir_url="https://investors.adp.com/",
        results_url="https://investors.adp.com/financial-information/default.aspx",
    ),
    CompanyProfile(
        ticker="DE",
        company_name="Deere & Company",
        aliases=("deere", "john deere", "de", "deere and company"),
        ir_url="https://investor.deere.com/",
        results_url="https://investor.deere.com/financials/default.aspx",
    ),
    CompanyProfile(
        ticker="BA",
        company_name="The Boeing Company",
        aliases=("boeing", "ba", "the boeing company"),
        ir_url="https://investors.boeing.com/",
        results_url="https://investors.boeing.com/investors/financial-results/default.aspx",
    ),
    CompanyProfile(
        ticker="COP",
        company_name="ConocoPhillips",
        aliases=("conocophillips", "cop"),
        ir_url="https://www.conocophillips.com/investor-relations/",
        results_url="https://www.conocophillips.com/investor-relations/quarterly-results/",
    ),
    CompanyProfile(
        ticker="SLB",
        company_name="SLB",
        aliases=("slb", "schlumberger"),
        ir_url="https://investorcenter.slb.com/",
        results_url="https://investorcenter.slb.com/financials/default.aspx",
    ),
)


def normalize_company_query(value: str) -> str:
    """Normalize free-form company/ticker input for alias matching."""
    lowered = value.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def _profile_search_terms(profile: CompanyProfile) -> set[str]:
    """Build the normalized exact-match term set for one company profile."""
    terms = {normalize_company_query(profile.ticker), normalize_company_query(profile.company_name)}
    terms.update(normalize_company_query(alias) for alias in profile.aliases)
    return {term for term in terms if term}


def resolve_company_profile(query: str) -> CompanyProfile | None:
    """Resolve a user query to a known company profile when possible."""
    normalized = normalize_company_query(query)
    if not normalized:
        return None

    for profile in COMPANY_PROFILES:
        if normalized in _profile_search_terms(profile):
            return profile

    # Very short queries such as "MS" should never fall through to loose substring matching,
    # otherwise symbols like MS get incorrectly resolved to Microsoft instead of Morgan Stanley.
    if len(normalized) <= 2:
        return None

    for profile in COMPANY_PROFILES:
        search_terms = _profile_search_terms(profile)
        if any(len(term) >= 3 and (normalized in term or term in normalized) for term in search_terms):
            return profile
    return None
