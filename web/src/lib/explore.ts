/**
 * Explore page logic shared by the build (first render, no JS needed) and the browser island
 * (src/scripts/explore.ts). It only selects and formats rows of the export; nothing is computed
 * beyond picking the groups the reader chose (docs/adr/0005). No Node imports here.
 */
import type * as PlotNs from '@observablehq/plot';

export type View = 'retention' | 'yearly';
export type By = 'brand' | 'fuel_group' | 'price_band';
export type Scope = 'all' | 'recent';

export interface State {
  view: View;
  by: By;
  groups: string[];
  scope: Scope;
}

export interface RetentionRow { group_type: string; scope: string; group: string; age: number; n: number; median_ratio: number }
export interface YearlyRow { group_type: string; group: string; to_year: number; n: number; median_real: number }

export const MAX_GROUPS = 5;
/** Points resting on fewer prices than this are left out of the lines and greyed in the table. */
export const MIN_N = 30;

export const BRAND_LABELS: Record<string, string> = {
  'VW - VolksWagen': 'Volkswagen',
  'GM - Chevrolet': 'Chevrolet',
  'Kia Motors': 'Kia',
  SSANGYONG: 'SsangYong',
};

export interface Labels {
  fuel: Record<string, string>;
  band: Record<string, string>;
  age: string;
  year: string;
  retention: string;
  yearly: string;
}

export function groupLabel(state: Pick<State, 'by'>, group: string, labels: Labels): string {
  if (state.by === 'fuel_group') return labels.fuel[group] ?? group;
  if (state.by === 'price_band') return labels.band[group] ?? group;
  return BRAND_LABELS[group] ?? group;
}

/** Groups available for a breakdown, in the order the export lists them. */
export function availableGroups(rows: { group_type: string; group: string; n: number }[], by: By): string[] {
  const groups = [...new Set(rows.filter((r) => r.group_type === by).map((r) => r.group))];
  if (by !== 'brand') return groups.sort();
  // Brands with the most comparisons first, so the default picks are the best-supported ones.
  const total = new Map<string, number>();
  for (const r of rows) if (r.group_type === by) total.set(r.group, (total.get(r.group) ?? 0) + r.n);
  return groups.sort((a, b) => (total.get(b) ?? 0) - (total.get(a) ?? 0));
}

export function defaultGroups(rows: { group_type: string; group: string; n: number }[], by: By): string[] {
  return availableGroups(rows, by).slice(0, by === 'brand' ? 4 : MAX_GROUPS);
}

export interface Point {
  group: string;
  label: string;
  x: number;
  y: number;
  n: number;
  small: boolean;
}

export function points(state: State, retention: RetentionRow[], yearly: YearlyRow[], labels: Labels): Point[] {
  const chosen = new Set(state.groups);
  if (state.view === 'retention') {
    return retention
      .filter((r) => r.group_type === state.by && r.scope === state.scope && chosen.has(r.group))
      .map((r) => ({ group: r.group, label: groupLabel(state, r.group, labels), x: r.age, y: r.median_ratio, n: r.n, small: r.n < MIN_N }));
  }
  return yearly
    .filter((r) => r.group_type === state.by && chosen.has(r.group))
    .map((r) => ({ group: r.group, label: groupLabel(state, r.group, labels), x: r.to_year, y: r.median_real, n: r.n, small: r.n < MIN_N }));
}

/** Plot options for the chosen state; the caller renders them (linkedom at build, the DOM in the browser). */
export function chartOptions(Plot: typeof PlotNs, state: State, pts: Point[], fmt: (v: number) => string, labels: Labels, width = 1040): PlotNs.PlotOptions {
  const order = state.groups;
  const cls = (g: string) => `series-${(order.indexOf(g) % MAX_GROUPS) + 1}`;
  const shown = pts.filter((p) => !p.small);
  const retention = state.view === 'retention';
  const ends = dodge(
    order.map((g) => shown.filter((p) => p.group === g).at(-1)).filter((p): p is Point => p !== undefined),
    retention ? 0.045 : spread(shown) * 0.06,
  );
  const narrow = width < 640;
  return {
    width,
    height: narrow ? 360 : 400,
    marginTop: 24,
    marginLeft: 52,
    marginRight: narrow ? 104 : 132,
    marginBottom: 40,
    ariaLabel: retention ? labels.retention : labels.yearly,
    x: { label: retention ? labels.age : labels.year, labelAnchor: 'right', tickFormat: (v: number) => String(v) },
    y: retention
      ? { domain: [0, 1], tickFormat: fmt, label: null, ticks: 5 }
      : { tickFormat: fmt, label: null, ticks: 6, nice: true },
    marks: [
      ...(retention ? [] : [Plot.ruleY([0], { stroke: 'currentColor', className: 'baseline' })]),
      ...order.map((g) =>
        Plot.line(shown.filter((p) => p.group === g), { x: 'x', y: 'y', stroke: 'currentColor', strokeWidth: 2, className: cls(g) }),
      ),
      ...order.map((g) =>
        Plot.dot(shown.filter((p) => p.group === g), { x: 'x', y: 'y', r: 2.5, fill: 'currentColor', className: cls(g) }),
      ),
      ...ends.map((p) =>
        Plot.text([p], { x: 'x', y: 'labelY', dx: 8, textAnchor: 'start', text: 'label', fill: 'currentColor', className: cls(p.group) }),
      ),
      Plot.tip(shown, Plot.pointer({ x: 'x', y: 'y', title: (p: Point) => `${p.label}\n${p.x}: ${fmt(p.y)} (n=${p.n})` })),
    ],
  };
}

function spread(pts: Point[]): number {
  const ys = pts.map((p) => p.y);
  return ys.length ? Math.max(...ys) - Math.min(...ys) || 1 : 1;
}

/** End labels pushed apart vertically so they never overlap (`labelY`, in data units). */
function dodge(ends: Point[], gap: number): (Point & { labelY: number })[] {
  const sorted = [...ends].sort((a, b) => a.y - b.y).map((p) => ({ ...p, labelY: p.y }));
  for (let i = 1; i < sorted.length; i++) {
    if (sorted[i].labelY - sorted[i - 1].labelY < gap) sorted[i].labelY = sorted[i - 1].labelY + gap;
  }
  return sorted;
}

export function stateToQuery(s: State): string {
  const q = new URLSearchParams({ v: s.view, by: s.by, g: s.groups.join('|') });
  if (s.view === 'retention') q.set('s', s.scope);
  return `?${q.toString()}`;
}

export function stateFromQuery(search: string, fallback: State, groupsFor: (by: By) => string[]): State {
  const q = new URLSearchParams(search);
  const view: View = q.get('v') === 'yearly' ? 'yearly' : q.get('v') === 'retention' ? 'retention' : fallback.view;
  const byRaw = q.get('by');
  const by: By = byRaw === 'brand' || byRaw === 'fuel_group' || byRaw === 'price_band' ? byRaw : fallback.by;
  const valid = new Set(groupsFor(by));
  const wanted = (q.get('g') ?? '').split('|').filter((g) => valid.has(g)).slice(0, MAX_GROUPS);
  const scope: Scope = q.get('s') === 'recent' ? 'recent' : 'all';
  return { view, by, scope, groups: wanted.length ? wanted : by === fallback.by ? fallback.groups : [...valid].slice(0, by === 'brand' ? 4 : MAX_GROUPS) };
}
