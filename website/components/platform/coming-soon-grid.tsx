"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchPlatforms } from "@/lib/api/platform-api";

import { ComingSoonCard } from "./coming-soon-card";

export function ComingSoonGrid() {
  const { data: platforms = [] } = useQuery({
    queryKey: ["platforms"],
    queryFn: fetchPlatforms,
    staleTime: Infinity,
  });

  const upcoming = platforms.filter((platform) => !platform.available);
  if (upcoming.length === 0) return null;

  return (
    <section className="w-full">
      <p className="text-muted-foreground mb-3 text-[11px] tracking-[0.14em] uppercase">
        Other platforms
      </p>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {upcoming.map((platform) => (
          <ComingSoonCard key={platform.id} platform={platform} />
        ))}
      </div>
    </section>
  );
}
