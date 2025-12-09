import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { docsNavigation, NavSection } from '../config/navigation';

interface DocsSidebarProps {
  className?: string;
}

export const DocsSidebar: React.FC<DocsSidebarProps> = ({ className = '' }) => {
  const location = useLocation();
  const [openSections, setOpenSections] = React.useState<string[]>(
    docsNavigation.map(section => section.title)
  );

  const toggleSection = (sectionTitle: string) => {
    setOpenSections(prev =>
      prev.includes(sectionTitle)
        ? prev.filter(title => title !== sectionTitle)
        : [...prev, sectionTitle]
    );
  };

  const isActive = (href: string) => location.pathname === href;

  return (
    <aside className={`docs-sidebar ${className}`}>
      <nav className="space-y-1">
        {docsNavigation.map((section: NavSection) => {
          const isOpen = openSections.includes(section.title);

          return (
            <div key={section.title} className="mb-4">
              <button
                onClick={() => toggleSection(section.title)}
                className="flex items-center justify-between w-full px-3 py-2 text-sm font-semibold text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
              >
                <span>{section.title}</span>
                {isOpen ? (
                  <ChevronDown className="w-4 h-4 text-gray-500" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-gray-500" />
                )}
              </button>

              {isOpen && (
                <ul className="mt-1 space-y-1 ml-2">
                  {section.items.map(item => (
                    <li key={item.href}>
                      <Link
                        to={item.href}
                        className={`
                          block px-3 py-2 text-sm rounded-md transition-colors
                          ${
                            isActive(item.href)
                              ? 'bg-indigo-50 text-indigo-600 font-medium'
                              : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                          }
                        `}
                      >
                        {item.title}
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          );
        })}
      </nav>
    </aside>
  );
};

export default DocsSidebar;
