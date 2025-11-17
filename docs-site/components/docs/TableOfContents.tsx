'use client';

import { useEffect, useState } from 'react';

interface TocItem {
  id: string;
  title: string;
  level: number;
}

export default function TableOfContents() {
  const [headings, setHeadings] = useState<TocItem[]>([]);
  const [activeId, setActiveId] = useState<string>('');

  useEffect(() => {
    // Extract headings from the page
    const elements = Array.from(document.querySelectorAll('h2, h3'));
    const items: TocItem[] = elements.map((element) => ({
      id: element.id,
      title: element.textContent || '',
      level: parseInt(element.tagName.substring(1)),
    }));
    setHeadings(items);

    // Track active heading
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id);
          }
        });
      },
      { rootMargin: '-100px 0px -80% 0px' }
    );

    elements.forEach((element) => observer.observe(element));

    return () => observer.disconnect();
  }, []);

  if (headings.length === 0) return null;

  return (
    <div className="hidden xl:block w-64 flex-shrink-0">
      <div className="sticky top-20 p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">
          이 페이지에서
        </h3>
        <nav>
          <ul className="space-y-2">
            {headings.map((heading) => (
              <li
                key={heading.id}
                className={`${heading.level === 3 ? 'ml-4' : ''}`}
              >
                <a
                  href={`#${heading.id}`}
                  className={`block text-sm transition-colors hover:text-primary-600 ${
                    activeId === heading.id
                      ? 'text-primary-600 font-medium'
                      : 'text-gray-600'
                  }`}
                >
                  {heading.title}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </div>
  );
}
