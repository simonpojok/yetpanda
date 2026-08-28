import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // The prod image copies .next/standalone, which only exists in this
  // mode. Without it the production build would come out unusable.
  output: "standalone",
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
