/**
 * The public export (web/public/data/, written by fipe/export.py) read at build time.
 * Pages cite these rows; nothing here computes a rate, it only selects rows and formats them
 * (docs/adr/0005). A row that does not exist throws, so a broken reference breaks the build.
 */
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import type { Lang } from '../i18n/ui';

const DATA = join(process.cwd(), 'public', 'data');

function load<T>(name: string): T[] {
  return JSON.parse(readFileSync(join(DATA, `${name}.json`), 'utf8')) as T[];
}

export interface YearlyChange {
  from_year: number;
  to_year: number;
  n: number;
  median_nominal: number;
  median_real: number;
  p25_real: number;
  p75_real: number;
  ipca: number;
  new_n: number;
  new_median_nominal: number;
  mass_n: number;
  mass_median_real: number;
}
export interface Cohort { purchase_year: number; age: number; n: number; median_real: number; p25_real: number; p75_real: number; median_nominal: number }
export interface CohortPooled { age: number; n: number; purchase_years: number; median_real: number; median_nominal: number }
export interface LossByAge { age: number; n: number; years: number; median_real: number; p25_real: number; p75_real: number; median_nominal: number }
export interface FourYear { from_year: number; to_year: number; n: number; median_real: number; median_nominal: number }
export interface HoldsValue { group_type: string; group: string; n: number; purchase_years: number; median_relative: number; p25_relative: number; p75_relative: number; median_real: number }
export interface VersionGap { age: number; groups: number; median_gap: number; p25_gap: number; p75_gap: number; share_top_keeps_less: number }
export interface FuelRelabel { from_year: number; to_year: number; fuel_from: string; fuel_to: string; cars: number }
export interface NewVsUsed { ref_year: number; n: number; median_ratio: number; p25_ratio: number; p75_ratio: number; max_ratio: number }
export interface Retention { scope: 'all' | 'recent'; age: number; n: number; median_ratio: number; p25_ratio: number; p75_ratio: number }
export interface Coverage { ref_year: number; ref_month: number; prices: number; new_car_prices: number; codigos_fipe: number; brands: number }
export interface ExploreRetention { group_type: string; scope: string; group: string; age: number; n: number; median_ratio: number; p25_ratio: number; p75_ratio: number }
export interface ExploreYearly { group_type: string; group: string; to_year: number; n: number; median_real: number }
export interface CleanReport {
  rows_in: number; rows_out: number; invalid_codigo: number; invalid_price: number; invalid_year: number;
  duplicates_dropped: number; duplicate_conflicts: number; fuel_group_collisions: number;
  rows_from_api: number; rows_from_csv_v1: number;
}
export interface FuelLabel { ref_year: number; fuel: string; prices: number }

export const yearly = load<YearlyChange>('yearly_change');
export const cohort = load<Cohort>('cohort');
export const cohortPooled = load<CohortPooled>('cohort_pooled');
export const lossByAge = load<LossByAge>('loss_by_age');
export const fourYear = load<FourYear>('four_year_change');
export const holdsValue = load<HoldsValue>('holds_value');
export const versionGap = load<VersionGap>('version_gap');
export const fuelRelabels = load<FuelRelabel>('fuel_relabels');
export const newVsUsed = load<NewVsUsed>('new_vs_used');
export const retention = load<Retention>('retention_by_age');
export const coverage = load<Coverage>('coverage');
export const exploreRetention = load<ExploreRetention>('explore_retention');
export const exploreYearly = load<ExploreYearly>('explore_yearly');
export const cleanReport = load<CleanReport>('clean_report')[0];
export const fuelLabels = load<FuelLabel>('fuel_labels');
export const manifest = JSON.parse(readFileSync(join(DATA, 'manifest.json'), 'utf8')) as {
  attribution: string;
  price_base: string;
  tables: Record<string, { description: string; rows: number; columns: string[] }>;
};

/** Exactly one row matching `where`, or the build fails. */
export function one<T extends object>(rows: T[], where: Partial<T>): T {
  const found = rows.filter((r) => Object.entries(where).every(([k, v]) => (r as Record<string, unknown>)[k] === v));
  if (found.length !== 1) throw new Error(`data: expected one row for ${JSON.stringify(where)}, got ${found.length}`);
  return found[0];
}

export const first = <T>(rows: T[]): T => rows[0];
export const last = <T>(rows: T[]): T => rows[rows.length - 1];

const LOCALE: Record<Lang, string> = { pt: 'pt-BR', en: 'en-US' };

export function int(v: number, lang: Lang): string {
  return new Intl.NumberFormat(LOCALE[lang], { maximumFractionDigits: 0 }).format(v);
}

/** 0.0903 -> "+9,0%" (changes carry their sign). */
export function change(v: number, lang: Lang, digits = 1): string {
  return new Intl.NumberFormat(LOCALE[lang], { style: 'percent', minimumFractionDigits: digits, maximumFractionDigits: digits, signDisplay: 'exceptZero' }).format(v);
}

/** 0.5902 -> "59%" (shares, no sign). */
export function share(v: number, lang: Lang, digits = 0): string {
  return new Intl.NumberFormat(LOCALE[lang], { style: 'percent', minimumFractionDigits: digits, maximumFractionDigits: digits }).format(v);
}

/** 0.88, 0.91 -> "88–91%" (a range of shares with one percent sign). */
export function shareRange(lo: number, hi: number, lang: Lang, digits = 0): string {
  const n = new Intl.NumberFormat(LOCALE[lang], { minimumFractionDigits: digits, maximumFractionDigits: digits });
  return `${n.format(lo * 100)}–${share(hi, lang, digits)}`;
}

/** -0.069 -> "6,9%": a loss written after a verb that already says "loses" (no double sign). */
export function loss(v: number, lang: Lang, digits = 0): string {
  return share(Math.abs(v), lang, digits);
}

/** -0.0991, -0.1076 -> "10% a 11%": a range of losses, smallest first, without signs. */
export function lossRange(a: number, b: number, lang: Lang): string {
  const [lo, hi] = [Math.abs(a), Math.abs(b)].sort((x, y) => x - y);
  return `${share(lo, lang)} ${lang === 'pt' ? 'a' : 'to'} ${share(hi, lang)}`;
}

/** 1.0862 -> "+9%": a relative value (1 = same as comparable cars) shown as how far above or below. */
export function relative(v: number, lang: Lang): string {
  return change(v - 1, lang, 0);
}

/** "2026-09" -> "set/2026" or "Sep 2026". */
export function month(ym: string, lang: Lang, names: string): string {
  const [y, m] = ym.split('-').map(Number);
  const label = names.split(',')[m - 1];
  return lang === 'pt' ? `${label}/${y}` : `${label} ${y}`;
}
