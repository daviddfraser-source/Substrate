/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverActions: true,
    typedRouter: true
  },
  output: "standalone",
  typescript: {
    ignoreBuildErrors: false
  }
};

module.exports = nextConfig;
