import Navbar from '@/components/navbar/Navbar';
import './globals.css';

export const metadata = {
  title: 'ATS Resume Agent',
  description: 'Optimize your resume for any job description',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-gray-50 min-h-screen pt-16" suppressHydrationWarning>
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
