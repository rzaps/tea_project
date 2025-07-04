import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig(({ mode }) => ({
  plugins: [
    react({
      jsxRuntime: "automatic",
    }),
  ],
  base: mode === "production" ? "https://tea-project-static.onrender.com/" : "/",
  build: {
    outDir: "../staticfiles",
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: path.resolve(__dirname, "src/main.tsx"),
      output: {
        format: 'es',
        entryFileNames: "assets/[name].[hash].js",
        chunkFileNames: "assets/[name].[hash].js",
        assetFileNames: "assets/[name].[hash].[ext]",
      },
    },
  },
  server: {
    host: "localhost",
    port: 5173,
    strictPort: true,
    cors: true,
    origin: "http://localhost:5173",
  },
}));
