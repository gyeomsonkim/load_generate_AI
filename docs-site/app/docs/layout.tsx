import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import Sidebar from '@/components/docs/Sidebar';
import TableOfContents from '@/components/docs/TableOfContents';

export default function DocsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 max-w-4xl mx-auto px-8 py-12">
          {children}
        </main>
        <TableOfContents />
      </div>
      <Footer />
    </>
  );
}
