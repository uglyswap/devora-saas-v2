export interface NavItem {
  title: string;
  href: string;
  description?: string;
}

export interface NavSection {
  title: string;
  items: NavItem[];
}

export const docsNavigation: NavSection[] = [
  {
    title: "Getting Started",
    items: [
      {
        title: "Introduction",
        href: "/docs/getting-started/introduction",
        description: "Welcome to Devora - Build web apps in minutes with AI"
      },
      {
        title: "Quick Start",
        href: "/docs/getting-started/quick-start",
        description: "Get up and running in 5 minutes"
      },
      {
        title: "Installation",
        href: "/docs/getting-started/installation",
        description: "Set up your development environment"
      }
    ]
  },
  {
    title: "Guides",
    items: [
      {
        title: "Using the Wizard",
        href: "/docs/guides/wizard-usage",
        description: "Step-by-step guide to building with AI"
      },
      {
        title: "AI Chat Assistant",
        href: "/docs/guides/ai-chat",
        description: "Get help while coding with AI"
      },
      {
        title: "Collaboration",
        href: "/docs/guides/collaboration",
        description: "Work together with your team"
      },
      {
        title: "Deployment",
        href: "/docs/guides/deployment",
        description: "Deploy your app to production"
      }
    ]
  },
  {
    title: "Features",
    items: [
      {
        title: "Code Editor",
        href: "/docs/features/editor",
        description: "Powerful Monaco-based code editor"
      },
      {
        title: "Live Preview",
        href: "/docs/features/preview",
        description: "See changes instantly"
      },
      {
        title: "Templates",
        href: "/docs/features/templates",
        description: "Start with pre-built templates"
      }
    ]
  },
  {
    title: "API Reference",
    items: [
      {
        title: "REST API",
        href: "/docs/api-reference/rest-api",
        description: "Complete REST API documentation"
      },
      {
        title: "WebSocket API",
        href: "/docs/api-reference/websocket",
        description: "Real-time collaboration API"
      }
    ]
  }
];

export const flatNavigation = docsNavigation.flatMap(section => section.items);

export function getDocByHref(href: string): NavItem | undefined {
  return flatNavigation.find(item => item.href === href);
}

export function getNextDoc(currentHref: string): NavItem | null {
  const currentIndex = flatNavigation.findIndex(item => item.href === currentHref);
  if (currentIndex === -1 || currentIndex === flatNavigation.length - 1) {
    return null;
  }
  return flatNavigation[currentIndex + 1];
}

export function getPrevDoc(currentHref: string): NavItem | null {
  const currentIndex = flatNavigation.findIndex(item => item.href === currentHref);
  if (currentIndex <= 0) {
    return null;
  }
  return flatNavigation[currentIndex - 1];
}
