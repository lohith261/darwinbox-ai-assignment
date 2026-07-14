import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { apiMiddleware } from "./frontend-web/api-middleware.ts";

const __dirname = dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  root: resolve(__dirname, "frontend-web"),
  build: {
    outDir: resolve(__dirname, "dist"),
    emptyOutDir: true,
  },
  plugins: [
    react(),
    {
      name: "api-middleware",
      apply: "serve",
      configureServer(server) {
        server.middlewares.use(apiMiddleware());
      },
    },
  ],
  server: {
    port: 5173,
    host: true,
  },
});
