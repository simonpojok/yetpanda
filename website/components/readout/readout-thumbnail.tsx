import Image from "next/image";

export function ReadoutThumbnail({
  src,
  alt,
  size = "md",
}: {
  src: string;
  alt: string;
  size?: "sm" | "md";
}) {
  const dimensions = size === "sm" ? "h-10 w-[71px]" : "h-[68px] w-[121px]";

  if (!src) {
    return <div className={`${dimensions} shrink-0 rounded-[4px] bg-muted`} />;
  }

  return (
    <div className={`${dimensions} relative shrink-0 overflow-hidden rounded-[4px] bg-muted`}>
      <Image src={src} alt={alt} fill sizes="121px" className="object-cover" />
    </div>
  );
}
