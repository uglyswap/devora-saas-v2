/**
 * Documentation Feature - Main Export
 * Export centralisé pour le module documentation interactive
 */

// Components
export { CodeBlock } from './components/CodeBlock';
export { Callout } from './components/Callout';
export { ApiEndpoint } from './components/ApiEndpoint';
export { InteractivePlayground } from './components/InteractivePlayground';
export { DocsSidebar } from './components/DocsSidebar';
export { DocsLayout } from './components/DocsLayout';

// Config
export {
  docsNavigation,
  flatNavigation,
  getDocByHref,
  getNextDoc,
  getPrevDoc,
  type NavItem,
  type NavSection
} from './config/navigation';
