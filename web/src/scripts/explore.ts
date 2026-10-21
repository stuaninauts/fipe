/**
 * Explore island: reads the export from /data/ and redraws the chart and table when the reader changes
 * the controls. State lives in the URL. Plot builds each SVG detached from the page; its <style> is removed
 * before insertion, so the strict CSP never sees an inline style (rules live in global.css, svg.chart).
 */
import * as Plot from '@observablehq/plot';
import {
  availableGroups, chartOptions, groupLabel, points, stateFromQuery, stateToQuery,
  type By, type Labels, type Point, type RetentionRow, type State, type YearlyRow,
} from '../lib/explore';

interface Config {
  lang: 'pt' | 'en';
  labels: Labels;
  initial: State;
  maxGroups: number;
  minN: number;
  text: Record<'groupsHint' | 'tooMany' | 'empty' | 'age' | 'year' | 'loading' | 'error' | 'bandNew' | 'bandUsed', string>;
}

const root = document.getElementById('explore');
if (root) void init(root);

async function init(root: HTMLElement) {
  const config = JSON.parse(root.dataset.config ?? '{}') as Config;
  const groupsBy = JSON.parse(root.dataset.groups ?? '{}') as Record<By, string[]>;
  const form = root.querySelector<HTMLFormElement>('form.controls')!;
  const chartEl = root.querySelector<HTMLElement>('[data-chart]')!;
  const tableEl = root.querySelector<HTMLElement>('[data-table]')!;
  const listEl = root.querySelector<HTMLElement>('[data-groups-list]')!;
  const statusEl = root.querySelector<HTMLElement>('[data-status]')!;
  const captionEl = root.querySelector<HTMLElement>('[data-caption]')!;
  root.querySelector<HTMLElement>('[data-hint]')!.textContent = config.text.groupsHint;

  const locale = config.lang === 'pt' ? 'pt-BR' : 'en-US';
  const share = new Intl.NumberFormat(locale, { style: 'percent', maximumFractionDigits: 0 });
  const change = new Intl.NumberFormat(locale, { style: 'percent', maximumFractionDigits: 0, signDisplay: 'exceptZero' });
  const int = new Intl.NumberFormat(locale);
  const captions: Record<State['view'], string> = {
    retention: captionEl.textContent ?? '',
    yearly: config.lang === 'pt'
      ? `Variação real mediana do preço do mesmo carro usado, de janeiro a janeiro (ano de chegada no eixo). Pontos com menos de ${config.minN} preços ficam fora das linhas.`
      : `Median real change in the price of the same used car, January to January (year of arrival on the axis). Points resting on fewer than ${config.minN} prices are left out of the lines.`,
  };

  let retention: RetentionRow[];
  let yearly: YearlyRow[];
  try {
    statusEl.textContent = config.text.loading;
    [retention, yearly] = await Promise.all([
      fetch('/data/explore_retention.json').then((r) => r.json() as Promise<RetentionRow[]>),
      fetch('/data/explore_yearly.json').then((r) => r.json() as Promise<YearlyRow[]>),
    ]);
    statusEl.textContent = '';
  } catch {
    statusEl.textContent = config.text.error;
    return;
  }

  const groupsFor = (by: By) => groupsBy[by] ?? availableGroups(retention, by);
  let state = stateFromQuery(location.search, config.initial, groupsFor);
  form.hidden = false;

  function syncForm() {
    form.querySelectorAll<HTMLInputElement>('input[name="view"]').forEach((i) => (i.checked = i.value === state.view));
    form.querySelectorAll<HTMLInputElement>('input[name="scope"]').forEach((i) => (i.checked = i.value === state.scope));
    const select = form.querySelector<HTMLSelectElement>('select[name="by"]')!;
    select.value = state.by;
    // The two views use different price bands; the option says which one.
    select.querySelector<HTMLOptionElement>('option[value="price_band"]')!.textContent =
      state.view === 'retention' ? config.text.bandNew : config.text.bandUsed;
    form.querySelector<HTMLElement>('fieldset.scope')!.hidden = state.view !== 'retention';
    listEl.replaceChildren(
      ...groupsFor(state.by).map((g) => {
        const label = document.createElement('label');
        const input = document.createElement('input');
        input.type = 'checkbox';
        input.name = 'group';
        input.value = g;
        input.checked = state.groups.includes(g);
        label.append(input, ` ${groupLabel(state, g, config.labels)}`);
        return label;
      }),
    );
  }

  function draw() {
    const fmt = (v: number) => (state.view === 'retention' ? share.format(v) : change.format(v));
    const pts = points(state, retention, yearly, config.labels);
    captionEl.textContent = captions[state.view];
    if (!state.groups.length) {
      statusEl.textContent = config.text.empty;
      chartEl.replaceChildren();
      tableEl.replaceChildren();
      return;
    }
    const width = Math.max(320, Math.min(1040, chartEl.clientWidth || 1040));
    const svg = Plot.plot({ ...chartOptions(Plot, state, pts, fmt, config.labels, width), className: 'chart' });
    svg.querySelector('style')?.remove();
    chartEl.replaceChildren(svg);
    tableEl.replaceChildren(table(pts, fmt));
  }

  function table(pts: Point[], fmt: (v: number) => string): HTMLTableElement {
    const t = document.createElement('table');
    t.className = 'num';
    const head = t.createTHead().insertRow();
    const first = document.createElement('th');
    first.textContent = state.view === 'retention' ? config.text.age : config.text.year;
    head.append(first);
    for (const g of state.groups) {
      const th = document.createElement('th');
      th.textContent = groupLabel(state, g, config.labels);
      head.append(th);
    }
    const body = t.createTBody();
    for (const x of [...new Set(pts.map((p) => p.x))].sort((a, b) => a - b)) {
      const row = body.insertRow();
      row.insertCell().textContent = String(x);
      for (const g of state.groups) {
        const p = pts.find((q) => q.group === g && q.x === x);
        const cell = row.insertCell();
        cell.textContent = p ? `${fmt(p.y)} (n=${int.format(p.n)})` : '–';
        if (p?.small) cell.className = 'small-n';
      }
    }
    return t;
  }

  function update(next: State) {
    state = next;
    history.replaceState(null, '', stateToQuery(state));
    syncForm();
    draw();
  }

  form.addEventListener('change', (e) => {
    const target = e.target as HTMLInputElement | HTMLSelectElement;
    statusEl.textContent = '';
    if (target.name === 'view') update({ ...state, view: target.value as State['view'] });
    else if (target.name === 'scope') update({ ...state, scope: target.value as State['scope'] });
    else if (target.name === 'by') {
      const by = target.value as By;
      update({ ...state, by, groups: groupsFor(by).slice(0, by === 'brand' ? 4 : config.maxGroups) });
    } else if (target.name === 'group') {
      const input = target as HTMLInputElement;
      const groups = input.checked ? [...state.groups, input.value] : state.groups.filter((g) => g !== input.value);
      if (groups.length > config.maxGroups) {
        input.checked = false;
        statusEl.textContent = config.text.tooMany;
        return;
      }
      update({ ...state, groups });
    }
  });
  form.addEventListener('submit', (e) => e.preventDefault());
  let resizeTimer: number | undefined;
  let lastWidth = chartEl.clientWidth;
  window.addEventListener('resize', () => {
    window.clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(() => {
      if (Math.abs(chartEl.clientWidth - lastWidth) < 40) return;
      lastWidth = chartEl.clientWidth;
      draw();
    }, 150);
  });

  syncForm();
  draw();
}
