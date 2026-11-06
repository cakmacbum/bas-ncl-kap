/// <reference types="vitest" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// API'yi proxy'le: /api → FastAPI (localhost:8000)
export default defineConfig({
  plugins: [react()],
  test: { environment: "node", include: ["src/**/*.test.ts"], exclude: ["e2e/**", "node_modules/**", "dist/**"] },
  // D06: OCCT worker ES modül olarak paketlenir; WASM `?url` ile ayrı asset (ön paketlemeye girmez).
  worker: { format: "es" },
  optimizeDeps: { exclude: ["replicad-opencascadejs"] },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
