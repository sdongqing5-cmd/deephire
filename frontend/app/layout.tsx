import type { Metadata } from "next";
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { cookies } from 'next/headers';
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";
import { FrontendLogProvider } from "@/components/frontend-log-provider";

export const metadata: Metadata = {
  title: "DeepHire",
  description: "AI-powered recruitment platform",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const cookieStore = await cookies();
  const locale = cookieStore.get('locale')?.value || 'en';
  const messages = await getMessages({ locale });

  return (
    <html
      lang={locale}
      className="h-full antialiased"
    >
      <body className="min-h-full flex flex-col">
        <NextIntlClientProvider locale={locale} messages={messages}>
          <FrontendLogProvider />
          {children}
          <Toaster />
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
