import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AppContextProvider } from '@/contexts/AppContext';

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AudioTranscriptionFire - Emergency Response System",
  description: "An integrated emergency response system with audio transcription, address validation, and ML-based incident interpretation",
  keywords: [
    "emergency response",
    "audio transcription",
    "address validation",
    "incident management",
    "dispatch system"
  ],
  authors: [
    {
      name: "AudioTranscriptionFire Team",
    },
  ],
  creator: "AudioTranscriptionFire",
  publisher: "AudioTranscriptionFire",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://audiotranscriptionfire.example.com",
    title: "AudioTranscriptionFire - Emergency Response System",
    description: "An integrated emergency response system with audio transcription, address validation, and ML-based incident interpretation",
    siteName: "AudioTranscriptionFire",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "AudioTranscriptionFire",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "AudioTranscriptionFire - Emergency Response System",
    description: "An integrated emergency response system with audio transcription, address validation, and ML-based incident interpretation",
    images: ["/og-image.png"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
    },
  },
  viewport: {
    width: "device-width",
    initialScale: 1,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <AppContextProvider>
          {children}
        </AppContextProvider>
      </body>
    </html>
  );
}
