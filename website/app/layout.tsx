import type { Metadata } from "next";
import { Archivo, Instrument_Sans, JetBrains_Mono } from "next/font/google";

import { AppProviders } from "@/providers/app-providers";

import "./globals.css";

// Display: mechanical and signage-like, which suits a transfer console.
const archivo = Archivo({
  variable: "--font-archivo",
  subsets: ["latin"],
  weight: ["500", "600", "700"],
});

// UI: legible at small sizes, less ubiquitous than Inter.
const instrumentSans = Instrument_Sans({
  variable: "--font-sans",
  subsets: ["latin"],
});

// Data: durations, sizes, bitrates, percentages.
const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin"],
  weight: ["400", "500"],
});

export const metadata: Metadata = {
  title: "YetPanda - Download video and audio from YouTube",
  description:
    "Paste a YouTube link and get an MP4 or MP3. Whole playlists too, at the quality you choose.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${archivo.variable} ${instrumentSans.variable} ${jetbrainsMono.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col">
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
