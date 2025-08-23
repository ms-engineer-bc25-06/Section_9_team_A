/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
    // ESLintエラーを完全に無視
    ignorePath: '.eslintignore',
  },
}

module.exports = nextConfig
