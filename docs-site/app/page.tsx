import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import Hero from '@/components/home/Hero';
import Features from '@/components/home/Features';
import QuickStart from '@/components/home/QuickStart';
import APIPreview from '@/components/home/APIPreview';
import CTA from '@/components/home/CTA';

export default function HomePage() {
  return (
    <>
      <Header />
      <main className="min-h-screen">
        <Hero />
        <Features />
        <QuickStart />
        <APIPreview />
        <CTA />
      </main>
      <Footer />
    </>
  );
}
