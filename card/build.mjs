// Bundles the card into the integration's frontend folder. The card version is
// taken from the integration's manifest.json (single source of truth).
import { readFileSync } from 'node:fs';
import * as esbuild from 'esbuild';

const manifest = JSON.parse(
  readFileSync(new URL('../custom_components/meteoalarm_custom/manifest.json', import.meta.url), 'utf8')
);
const watch = process.argv.includes('--watch');

const options = {
  entryPoints: ['src/meteoalarm-card.ts'],
  bundle: true,
  format: 'esm',
  minify: !watch,
  outfile: '../custom_components/meteoalarm_custom/frontend/meteoalarm-card.js',
  define: { __CARD_VERSION__: JSON.stringify(manifest.version) },
  logLevel: 'info',
};

if (watch) {
  const ctx = await esbuild.context(options);
  await ctx.watch();
} else {
  await esbuild.build(options);
}
