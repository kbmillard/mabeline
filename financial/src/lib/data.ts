import type {
  CommodityEconomyReceipt,
  DollarToMillionPlaybook,
  FreightMovementReceipt,
  MarketScanReceipt,
  MoneyballReceipt,
  PennyForwardReceipt,
  ReturnScanReceipt,
} from "./types";

import returnScan from "@/data/return_scan_receipt_v1.json";
import pennyForward from "@/data/penny_forward_screen_v1.json";
import moneyball from "@/data/moneyball_aggregate_v1.json";
import millionPlaybook from "@/data/dollar_to_million_playbook_v1.json";
import freightMovement from "@/data/freight_movement_receipt_v1.json";
import commodityEconomy from "@/data/commodity_economy_v1.json";
import marketScan from "@/data/market_scan_returns_v1.json";
import iranOil from "@/data/thg_iran_oil_v1.json";

export function getMarketScan(): MarketScanReceipt {
  return marketScan as MarketScanReceipt;
}

export function getIranOil() {
  return iranOil;
}

export function getReturnScan(): ReturnScanReceipt {
  return returnScan as ReturnScanReceipt;
}

export function getPennyForward(): PennyForwardReceipt {
  return pennyForward as PennyForwardReceipt;
}

export function getMoneyball(): MoneyballReceipt {
  return moneyball as MoneyballReceipt;
}

export function getMillionPlaybook(): DollarToMillionPlaybook {
  return millionPlaybook as DollarToMillionPlaybook;
}

export function getFreightMovement(): FreightMovementReceipt {
  return freightMovement as FreightMovementReceipt;
}

export function getCommodityEconomy(): CommodityEconomyReceipt {
  return commodityEconomy as CommodityEconomyReceipt;
}

export function fmtPct(n: number | null | undefined, digits = 1): string {
  if (n == null || Number.isNaN(n)) return "—";
  const sign = n > 0 ? "+" : "";
  return `${sign}${n.toFixed(digits)}%`;
}

export function fmtUsd(n: number | null | undefined): string {
  if (n == null || Number.isNaN(n)) return "—";
  if (n < 0.01) return `$${n.toFixed(4)}`;
  if (n < 1) return `$${n.toFixed(3)}`;
  return `$${n.toFixed(2)}`;
}

export function fmtNum(n: number | null | undefined, digits = 1): string {
  if (n == null || Number.isNaN(n)) return "—";
  return n.toLocaleString(undefined, { maximumFractionDigits: digits });
}
