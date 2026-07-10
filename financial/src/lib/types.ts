export type MarketReturnRow = {
  ticker: string;
  market: string;
  name: string;
  start?: number;
  end?: number;
  ret_1y: number;
};

export type MarketScanReceipt = {
  scan_type: string;
  period: string;
  universe_size: number;
  priced: number;
  filters: { min_start_price: number; max_return_cap: number };
  top_50_sane: MarketReturnRow[];
  created_at: string;
};

export type ReturnTicker = {
  ticker: string;
  return_pct: number;
  start_usd?: number;
  end_usd?: number;
  note?: string;
};

export type ReturnScanReceipt = {
  scan_type: string;
  period: string;
  sources: string[];
  runs: {
    raw_sec_scan?: {
      status: string;
      tickers_priced: number;
      raw_highest: ReturnTicker;
      raw_runner_up: ReturnTicker;
    };
    sanity_sec_scan_full?: {
      status: string;
      tickers_priced: number;
      highest: ReturnTicker;
    };
    exchange_sample?: {
      priced: number;
      highest: ReturnTicker;
    };
  };
  prior_validated_basket?: {
    highest: ReturnTicker;
  };
  created_at: string;
};

export type PennyCandidate = {
  ticker: string;
  name: string;
  px: number;
  score: number;
  ret_1y: number;
  ret_3m: number;
  upside_pct: number | null;
  sector?: string | null;
  exchange?: string;
};

export type PennyForwardReceipt = {
  scan_type: string;
  as_of: string;
  survivor_count: number;
  top_k: number;
  top: PennyCandidate[];
  method: string;
  elapsed_sec?: number | null;
  artv_reference?: { ticker: string; note?: string } | null;
  algorithm?: string | null;
};

export type MoneyballPick = {
  ticker: string;
  name: string;
  price_now: number;
  proj_target: number | null;
  moneyball_score: number;
  upside_multiple: number | null;
  x100_feasible: boolean;
  cent_zone: boolean;
  stake_usd: number;
  value_at_target_usd: number | null;
  stake_needed_for_goal_usd: number | null;
  ret_1y: number | null;
  ret_3m: number | null;
  mcap_m: number | null;
  exchange: string;
  rec: string;
  vol: number | null;
  components: Record<string, number>;
};

export type MoneyballReceipt = {
  scan_type: string;
  algorithm: string;
  as_of: string | null;
  config: {
    stake_usd: number;
    target_dollar_goal: number;
    cent_zone_max: number;
  };
  summary: {
    scored: number;
    cent_zone_count: number;
    x100_feasible_count: number;
    best_cent_zone: MoneyballPick | null;
    best_x100: MoneyballPick | null;
  };
  moneyball_thesis: string;
  top: MoneyballPick[];
  method: string;
  matured_reference?: { ticker?: string; note?: string };
  created_at: string;
};

export type DollarToMillionPlaybook = {
  scan_type: string;
  as_of: string;
  goal_usd: number;
  llm_first: boolean;
  verdict: string;
  paths: {
    memecoin_launch: {
      feasible_for_1_to_1m: boolean;
      expected_hit_rate: string;
      documented_examples: {
        name: string;
        in_usd: number;
        out_usd: number;
        multiple: number;
        horizon: string;
        source: string;
      }[];
      monitor_checklist: string[];
    };
    sec_penny_stocks: {
      feasible_for_1_to_1m: boolean;
      best_asymmetric_add: Record<string, unknown> | null;
      stock_paths_from_moneyball: {
        ticker: string;
        name: string;
        price_now: number;
        proj_target: number;
        upside_multiple: number;
        stake_needed_for_1m_usd: number | null;
        moneyball_score: number;
        cent_zone: boolean;
      }[];
      note: string;
    };
  };
  commands: string[];
  created_at: string;
};

export type FreightMode = {
  mode: string;
  thousand_tons: number;
  million_ton_miles?: number;
  pct_of_tons: number;
};

export type FreightMovementReceipt = {
  scan_type: string;
  year: string;
  what_this_is: string;
  what_this_is_not: string[];
  totals: {
    billion_tons_equiv: number;
    thousand_tons: number;
    million_ton_miles: number;
  };
  by_mode: FreightMode[];
  top_corridors: { corridor: string; thousand_tons: number }[];
  top_commodities?: { commodity: string; thousand_tons: number }[];
  created_at?: string;
};

export type UnifiedCommodity = {
  sctg: string;
  commodity: string;
  economy_score: number;
  faf5_thousand_tons?: number | null;
  faf5_pct?: number | null;
  cfs_million_tons?: number | null;
  cfs_billion_usd?: number | null;
  cfs_pct?: number | null;
  primary_mode?: string | null;
};

export type CommodityEconomyReceipt = {
  scan_type: string;
  algorithm: string;
  as_of: string;
  what_this_is: string;
  what_this_is_not: string[];
  physical_economy_totals: {
    faf5_billion_tons?: number | null;
    cfs_million_tons?: number | null;
    cfs_billion_usd_shipment_value?: number | null;
    usgs_deposit_sites?: number | null;
    crude_imports_kbbl_latest?: number | null;
  };
  unified_commodity_slate: UnifiedCommodity[];
  energy_snapshot: {
    crude_imports_by_origin: {
      region: string;
      thousand_barrels: number;
      latest_month?: string;
    }[];
  };
  layers: {
    cfs_2022?: {
      by_sector: { sector: string; label: string; billion_usd: number; million_tons: number }[];
    };
    usgs_minerals?: {
      top_commodities: { commodity: string; deposit_sites: number; type: string }[];
    };
  };
  gaps: string[];
  created_at: string;
};
