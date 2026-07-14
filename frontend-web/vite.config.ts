import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { apiMiddleware } from "./api-middleware.ts";

export default defineConfig({
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
