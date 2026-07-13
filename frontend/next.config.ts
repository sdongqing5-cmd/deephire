import type { NextConfig } from "next";
import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin('./i18n.ts');

const nextConfig: NextConfig = {
  // Optimize for development performance
  reactStrictMode: true,

  // Reduce memory usage
  experimental: {
    // Use less memory during compilation
    workerThreads: false,
    cpus: 4,  // Use 4 cores for better performance (balanced)
  },

  // Disable source maps in development to reduce memory
  productionBrowserSourceMaps: false,
};

export default withNextIntl(nextConfig);
