import { spawn } from "node:child_process";
import { existsSync, mkdirSync } from "node:fs";
import { resolve } from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import type { Plugin } from "vite";

const PROJECT_ROOT = resolve(__dirname, "..");
const VENV_PYTHON = resolve(PROJECT_ROOT, ".venv/bin/python");

function ensureDataDirs() {
  for (const d of ["data/chroma", "data/sqlite", "data/traces"]) {
    const p = resolve(PROJECT_ROOT, d);
    if (!existsSync(p)) mkdirSync(p, { recursive: true });
  }
}

function backendPlugin(): Plugin {
  let proc: ReturnType<typeof spawn> | null = null;
  let started = false;

  return {
    name: "spawn-python-backend",
    apply: "serve",
    configureServer() {
      if (started) return;
      started = true;
      ensureDataDirs();

      const pythonBin = existsSync(VENV_PYTHON) ? VENV_PYTHON : "python3";

      proc = spawn(
        pythonBin,
        ["-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
        {
          cwd: PROJECT_ROOT,
          stdio: ["ignore", "pipe", "pipe"],
          env: { ...process.env, PYTHONUNBUFFERED: "1" },
        },
      );

      proc.stdout?.on("data", (d: Buffer) => console.log(`[backend] ${d.toString().trim()}`));
      proc.stderr?.on("data", (d: Buffer) => console.log(`[backend] ${d.toString().trim()}`));
      proc.on("exit", (code) => console.log(`[backend] exited with code ${code}`));
    },
  };
}

export default defineConfig({
  plugins: [react(), backendPlugin()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
      "/health": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
});
