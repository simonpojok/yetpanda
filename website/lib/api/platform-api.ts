import { endpoints } from "./endpoints";
import { request } from "./http-client";
import type { Platform } from "@/lib/domain/platform";

export async function fetchPlatforms(): Promise<Platform[]> {
  const data = await request<{ platforms: Platform[] }>(endpoints.platforms);
  return data.platforms;
}
