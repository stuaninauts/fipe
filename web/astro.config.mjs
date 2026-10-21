// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// PT na raiz e EN em /en/, com URLs no idioma da página (docs/adr/0002).
export default defineConfig({
  site: 'https://fipe.stuaninauts.com',
  trailingSlash: 'ignore',
  // Sem Markdown com realce de código: o Shiki colocaria estilos inline que a CSP bloqueia.
  markdown: { syntaxHighlight: false },
  i18n: {
    defaultLocale: 'pt',
    locales: ['pt', 'en'],
    routing: { prefixDefaultLocale: false },
  },
  integrations: [sitemap({ filter: (page) => !page.endsWith('/404/') })],
  // CSP estrita (docs/adr/0002): script-src e style-src saem com hashes no build; nada inline sem hash.
  // Os SVGs do Plot chegam sem o <style> próprio (src/lib/charts.ts e src/scripts/explore.ts).
  // A única origem externa é o beacon do Web Analytics da Cloudflare, injetado pela borda; as métricas
  // voltam para o próprio domínio (/cdn-cgi/rum), e o Explorar busca o export em /data/, então
  // connect-src fica 'self'.
  security: {
    csp: {
      scriptDirective: { resources: ["'self'", 'https://static.cloudflareinsights.com'] },
      directives: [
        "default-src 'self'",
        "img-src 'self' data:",
        "font-src 'self'",
        "connect-src 'self'",
        "object-src 'none'",
        "base-uri 'self'",
        "form-action 'self'",
      ],
    },
  },
});
