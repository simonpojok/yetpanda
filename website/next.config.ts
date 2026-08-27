import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    // images.domains is deprecated in Next 16; remotePatterns is the
    // replacement. Serving thumbnails through next/image removes any need
    // for a backend image proxy.
    remotePatterns: [
      { protocol: "https", hostname: "i.ytimg.com" },
      { protocol: "https", hostname: "i9.ytimg.com" },
      { protocol: "https", hostname: "yt3.ggpht.com" },
    ],
  },
};

export default nextConfig;
