import './globals.css';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

export const metadata = {
  title: 'FindMyJob',
  description: 'Get job matches based on your resume skills',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-black text-orange-400 font-sans">
        <Navbar />
        <main className="pt-20">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
