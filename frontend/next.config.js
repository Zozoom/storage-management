/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  eslint: { ignoreDuringBuilds: true },
  // Plain `npm run dev`: proxy /api to the local backend (on Vercel the platform routes it).
  async rewrites() {
    if (process.env.NODE_ENV !== "development") return [];
    return [{ source: "/api/:path*", destination: "http://localhost:8000/api/:path*" }];
  },
};

module.exports = nextConfig;
