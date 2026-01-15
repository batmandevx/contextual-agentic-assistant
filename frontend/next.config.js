/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  images: {
    unoptimized: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://r6vbn1vjpl.execute-api.us-east-1.amazonaws.com', // Update to Production URL!    
  },
}

module.exports = nextConfig
