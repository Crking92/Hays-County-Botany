import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  // Relative paths let the same build work at a GitHub project URL,
  // a custom domain, or a local preview server.
  base: "./",
  plugins: [react()],
  build: {
    outDir: "dist",
    sourcemap: true,
  },
});
