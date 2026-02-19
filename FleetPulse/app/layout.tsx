import './globals.css';
import type { Metadata } from 'next';
import { Bodoni_Moda, Carme } from 'next/font/google';
import { ThemeProvider } from '@/components/theme-provider';

const bodoniModa = Bodoni_Moda({
  subsets: ['latin'],
  variable: '--font-heading',
  display: 'swap',
});

const carme = Carme({
  subsets: ['latin'],
  weight: '400',
  variable: '--font-body',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'FleetPulse - Professional Fleet Management',
  description: 'Enterprise fleet management platform by Cloud Telematics',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${bodoniModa.variable} ${carme.variable}`} suppressHydrationWarning>
      <body className="font-body antialiased">
        <ThemeProvider attribute="class" defaultTheme="light" enableSystem={false}>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
