import { defineConfig } from 'astro/config';

// En GitHub Actions se toma el usuario del repositorio; en local queda sin "site".
const usuario = process.env.GITHUB_REPOSITORY_OWNER;
const repo = process.env.GITHUB_REPOSITORY?.split('/')[1] ?? 'flora-siete-de-abril';

export default defineConfig({
  site: usuario ? `https://${usuario}.github.io` : undefined,
  base: usuario ? `/${repo}` : '/',
  trailingSlash: 'always',
});
