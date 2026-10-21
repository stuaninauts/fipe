/** Interface text and routes per language (PT at the root, EN under /en/: docs/adr/0002). */
export type Lang = 'pt' | 'en';
export type Page = 'home' | 'shock' | 'brandNew' | 'depreciation' | 'explore' | 'method' | 'quality';

export const LANGS: Lang[] = ['pt', 'en'];

export function otherLang(lang: Lang): Lang {
  return lang === 'pt' ? 'en' : 'pt';
}

const PATHS: Record<Page, Record<Lang, string>> = {
  home: { pt: '/', en: '/en/' },
  shock: { pt: '/choque-2021-2022/', en: '/en/2021-2022-shock/' },
  brandNew: { pt: '/zero-km/', en: '/en/brand-new/' },
  depreciation: { pt: '/depreciacao/', en: '/en/depreciation/' },
  explore: { pt: '/explorar/', en: '/en/explore/' },
  method: { pt: '/metodo/', en: '/en/method/' },
  quality: { pt: '/qualidade/', en: '/en/data-quality/' },
};

export function path(lang: Lang, page: Page): string {
  return PATHS[page][lang];
}

export const hreflang = (lang: Lang) => (lang === 'pt' ? 'pt-BR' : 'en');

const pt = {
  'site.name': 'Fipe',
  'site.title': 'Quanto um carro perde de valor no Brasil',
  'site.description': 'Duas décadas da tabela FIPE com a inflação descontada: o choque de 2022, o mito do zero km e quanto um carro vale com o tempo.',
  'nav.label': 'Principal',
  'nav.skip': 'Pular para o conteúdo',
  'nav.analyses': 'Análises',
  'nav.explore': 'Explorar',
  'nav.method': 'Método',
  'nav.quality': 'Dados',
  'nav.lang': 'EN',
  'nav.langLabel': 'Read in English',
  'footer.source': 'Fonte: Tabela FIPE (Fundação Instituto de Pesquisas Econômicas) e IPCA (IBGE). O site publica só agregados, nunca o preço de um carro.',
  'footer.code': 'Código',
  'footer.credit': 'Versão original de 2023 em dupla com @gpl27 (INF/UFRGS).',
  'unit.real': 'Valores reais em reais de',
  'table.show': 'Ver os números em tabela',
  'table.n': 'n',
  'chart.year': 'ano',
  'notFound.title': 'Página não encontrada',
  'notFound.body': 'O endereço não existe ou mudou.',
  'notFound.back': 'Voltar ao início',
  'months.short': 'jan,fev,mar,abr,mai,jun,jul,ago,set,out,nov,dez',
} as const;

export type UiKey = keyof typeof pt;

const en: Record<UiKey, string> = {
  'site.name': 'Fipe',
  'site.title': 'How much a car loses value in Brazil',
  'site.description': "Two decades of Brazil's FIPE car price table, adjusted for inflation: the 2022 shock, the brand-new myth and what a car is worth over time.",
  'nav.label': 'Main',
  'nav.skip': 'Skip to content',
  'nav.analyses': 'Analyses',
  'nav.explore': 'Explore',
  'nav.method': 'Method',
  'nav.quality': 'Data',
  'nav.lang': 'PT',
  'nav.langLabel': 'Ler em português',
  'footer.source': 'Source: FIPE price table (Fundação Instituto de Pesquisas Econômicas) and IPCA (IBGE). The site publishes aggregates only, never the price of a single car.',
  'footer.code': 'Code',
  'footer.credit': 'Original 2023 version built with @gpl27 (INF/UFRGS).',
  'unit.real': 'Real values in reais of',
  'table.show': 'See the numbers as a table',
  'table.n': 'n',
  'chart.year': 'year',
  'notFound.title': 'Page not found',
  'notFound.body': 'This address does not exist or has moved.',
  'notFound.back': 'Back to the start',
  'months.short': 'Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec',
};

const UI: Record<Lang, Record<UiKey, string>> = { pt, en };

export function t(lang: Lang, key: UiKey): string {
  return UI[lang][key];
}
