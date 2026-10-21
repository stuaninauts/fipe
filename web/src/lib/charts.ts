/**
 * Charts as static SVG, drawn by Observable Plot at build time (docs/adr/0002). No script reaches the
 * browser for these. Plot puts a <style> inside each SVG; the strict CSP would block it, so it is removed
 * here and its rules live in global.css (svg.chart). Colors come from CSS classes, so both themes work.
 */
import * as Plot from '@observablehq/plot';
import { parseHTML } from 'linkedom';

/** Chart widths: the wide one fills the figure on desktop, the narrow one stays legible on a phone. */
export const WIDE = 1040;
export const NARROW = 420;

function plotSvg(options: Plot.PlotOptions, width: number, cls: string): string {
  const { document } = parseHTML('<!doctype html><html><body></body></html>');
  const svg = Plot.plot({ ...options, width, document, className: 'chart' } as Plot.PlotOptions) as unknown as Element;
  svg.setAttribute('class', `chart ${cls}`); // Plot takes a single class name
  return svg.outerHTML.replace(/<style>[\s\S]*?<\/style>/, '');
}

/** Two renderings of the same chart; global.css shows one per screen width (the other is display: none,
 *  so screen readers meet a single chart). */
export function render(options: Plot.PlotOptions): string {
  return plotSvg(options, WIDE, 'chart-wide') + plotSvg(options, NARROW, 'chart-narrow');
}

export interface YearValue {
  year: number;
  value: number;
}

/** One bar per year around zero; focus years in the accent color and labelled. */
export function yearBars(data: YearValue[], o: {
  focus: number[];
  labelled: number[];
  format: (v: number) => string;
  aria: string;
  domain: [number, number];
}): string {
  const isFocus = (d: YearValue) => o.focus.includes(d.year);
  const labelled = data.filter((d) => o.focus.includes(d.year) || o.labelled.includes(d.year));
  return render({
    height: 300,
    marginTop: 28,
    marginBottom: 32,
    marginLeft: 8,
    marginRight: 8,
    ariaLabel: o.aria,
    x: { type: 'band', domain: data.map((d) => d.year), label: null, tickSize: 0, padding: 0.2, tickFormat: (y: number) => (y % 5 === 0 || o.focus.includes(y) ? String(y) : '') },
    y: { domain: o.domain, axis: null },
    marks: [
      Plot.barY(data.filter((d) => !isFocus(d)), { x: 'year', y: 'value', fill: 'currentColor', className: 'bar' }),
      Plot.barY(data.filter(isFocus), { x: 'year', y: 'value', fill: 'currentColor', className: 'bar-focus tone-accent' }),
      ...([[(d: YearValue) => d.value >= 0, -10], [(d: YearValue) => d.value < 0, 12]] as const).map(([keep, dy]) =>
        Plot.text(labelled.filter(keep), {
          x: 'year', y: 'value', dy, text: (d: YearValue) => o.format(d.value), fill: 'currentColor', className: 'bar-label',
        }),
      ),
      Plot.ruleY([0], { stroke: 'currentColor', className: 'baseline' }),
    ],
  });
}

export interface BandPoint {
  x: number;
  y: number;
  lo: number;
  hi: number;
}

/** A median line with its interquartile band; selected points labelled. */
export function bandLine(data: BandPoint[], o: {
  aria: string;
  domain: [number, number];
  xLabel?: string;
  yFormat: (v: number) => string;
  labelled: number[];
  rule?: number;
  xTicks?: number[];
}): string {
  const labelled = data.filter((d) => o.labelled.includes(d.x));
  return render({
    height: 300,
    marginTop: 24,
    marginLeft: 48,
    marginBottom: 40,
    ariaLabel: o.aria,
    x: { label: o.xLabel ?? null, labelAnchor: 'right', tickFormat: (v: number) => String(v), ticks: o.xTicks },
    y: { domain: o.domain, tickFormat: o.yFormat, label: null, grid: false, ticks: 5 },
    marks: [
      Plot.areaY(data, { x: 'x', y1: 'lo', y2: 'hi', fill: 'currentColor', className: 'band' }),
      ...(o.rule !== undefined ? [Plot.ruleY([o.rule], { stroke: 'currentColor', strokeDasharray: '4,4', className: 'rule-mean' })] : []),
      Plot.line(data, { x: 'x', y: 'y', stroke: 'currentColor', strokeWidth: 2, className: 'line' }),
      Plot.dot(labelled, { x: 'x', y: 'y', r: 4, fill: 'currentColor', className: 'line' }),
      Plot.text(labelled, { x: 'x', y: 'y', dy: -12, text: (d: BandPoint) => o.yFormat(d.y), fill: 'currentColor', className: 'label-strong' }),
    ],
  });
}

export interface SeriesPoint {
  series: string;
  label: string;
  x: number;
  y: number;
}

/** Two or more lines, labelled at their last point (no legend box needed). */
export function lines(data: SeriesPoint[], o: {
  aria: string;
  domain: [number, number];
  xLabel?: string;
  yFormat: (v: number) => string;
  classes: Record<string, string>;
}): string {
  const ends = [...new Set(data.map((d) => d.series))].map((s) => {
    const pts = data.filter((d) => d.series === s);
    return pts[pts.length - 1];
  });
  return render({
    height: 300,
    marginTop: 24,
    marginLeft: 48,
    marginRight: 120,
    marginBottom: 40,
    ariaLabel: o.aria,
    x: { label: o.xLabel ?? null, labelAnchor: 'right', tickFormat: (v: number) => String(v) },
    y: { domain: o.domain, tickFormat: o.yFormat, label: null, ticks: 5 },
    marks: [
      ...Object.entries(o.classes).map(([series, cls]) =>
        Plot.line(data.filter((d) => d.series === series), { x: 'x', y: 'y', stroke: 'currentColor', strokeWidth: 2, className: cls }),
      ),
      ...ends.map((d) =>
        Plot.text([d], { x: 'x', y: 'y', dx: 8, textAnchor: 'start', text: 'label', fill: 'currentColor', className: o.classes[d.series] }),
      ),
    ],
  });
}

/** Plain count bars per year (coverage). */
export function countBars(data: YearValue[], o: { aria: string; format: (v: number) => string; labelled: number[] }): string {
  const labelled = data.filter((d) => o.labelled.includes(d.year));
  return render({
    height: 240,
    marginTop: 24,
    marginBottom: 32,
    marginLeft: 8,
    marginRight: 8,
    ariaLabel: o.aria,
    x: { type: 'band', domain: data.map((d) => d.year), label: null, tickSize: 0, padding: 0.2, tickFormat: (y: number) => (y % 5 === 0 ? String(y) : '') },
    y: { axis: null },
    marks: [
      Plot.barY(data, { x: 'year', y: 'value', fill: 'currentColor', className: 'bar' }),
      Plot.text(labelled, { x: 'year', y: 'value', dy: -10, text: (d: YearValue) => o.format(d.value), fill: 'currentColor', className: 'bar-label' }),
      Plot.ruleY([0], { stroke: 'currentColor', className: 'baseline' }),
    ],
  });
}
