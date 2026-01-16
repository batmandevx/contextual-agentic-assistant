/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  images: {
    unoptimized: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://agentic-assistant-alb-171236663.us-east-1.elb.amazonaws.com',
  },
}

module.exports = nextConfig
