export function StatItem({ label, value }: { label: string; value: string }) {
  return (
    <span className="flex items-baseline gap-1.5">
      <span className="text-muted-foreground text-[11px] tracking-wide uppercase">
        {label}
      </span>
      <span className="tabular text-[13px]">{value}</span>
    </span>
  );
}
