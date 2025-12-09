/**
 * Devora i18n Configuration
 *
 * Internationalization setup using react-i18next
 * Supports: English (en), French (fr), Spanish (es)
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import HttpBackend from 'i18next-http-backend';

// Import translation files
import enTranslations from '../locales/en.json';
import frTranslations from '../locales/fr.json';
import esTranslations from '../locales/es.json';

/**
 * Supported languages configuration
 */
export const SUPPORTED_LANGUAGES = [
  {
    code: 'en',
    name: 'English',
    nativeName: 'English',
    flag: '🇺🇸',
    dir: 'ltr'
  },
  {
    code: 'fr',
    name: 'French',
    nativeName: 'Français',
    flag: '🇫🇷',
    dir: 'ltr'
  },
  {
    code: 'es',
    name: 'Spanish',
    nativeName: 'Español',
    flag: '🇪🇸',
    dir: 'ltr'
  }
];

/**
 * Language detection configuration
 */
const detectionOptions = {
  // Order of language detection methods
  order: [
    'querystring',    // ?lng=en
    'cookie',         // Cookie value
    'localStorage',   // localStorage value
    'navigator',      // Browser language
    'htmlTag'        // <html lang="en">
  ],

  // Keys to lookup language
  lookupQuerystring: 'lng',
  lookupCookie: 'i18next',
  lookupLocalStorage: 'i18nextLng',

  // Cache user language on
  caches: ['localStorage', 'cookie'],

  // Optional expire and domain for cookie
  cookieMinutes: 10080, // 7 days
  cookieDomain: window.location.hostname
};

/**
 * i18next configuration
 */
i18n
  // Load translation using http backend
  .use(HttpBackend)

  // Detect user language
  .use(LanguageDetector)

  // Pass the i18n instance to react-i18next
  .use(initReactI18next)

  // Initialize i18next
  .init({
    // Resources (translations)
    resources: {
      en: {
        translation: enTranslations
      },
      fr: {
        translation: frTranslations
      },
      es: {
        translation: esTranslations
      }
    },

    // Default language
    fallbackLng: 'en',

    // Supported languages
    supportedLngs: SUPPORTED_LANGUAGES.map(lang => lang.code),

    // Language detection
    detection: detectionOptions,

    // Debug mode (set to false in production)
    debug: process.env.NODE_ENV === 'development',

    // Interpolation options
    interpolation: {
      escapeValue: false, // React already escapes values
      formatSeparator: ',',

      // Custom format function
      format: (value, format, lng) => {
        if (format === 'uppercase') return value.toUpperCase();
        if (format === 'lowercase') return value.toLowerCase();
        if (format === 'capitalize') {
          return value.charAt(0).toUpperCase() + value.slice(1);
        }
        if (format === 'number') {
          return new Intl.NumberFormat(lng).format(value);
        }
        if (format === 'currency') {
          return new Intl.NumberFormat(lng, {
            style: 'currency',
            currency: 'USD'
          }).format(value);
        }
        if (format === 'date') {
          return new Intl.DateTimeFormat(lng).format(new Date(value));
        }
        if (format === 'datetime') {
          return new Intl.DateTimeFormat(lng, {
            dateStyle: 'medium',
            timeStyle: 'short'
          }).format(new Date(value));
        }
        return value;
      }
    },

    // React-specific options
    react: {
      // Wait for all translations to load before rendering
      useSuspense: true,

      // Bind i18n events to component lifecycle
      bindI18n: 'languageChanged loaded',
      bindI18nStore: 'added removed',

      // Default namespace
      defaultNS: 'translation'
    },

    // Load options
    load: 'languageOnly', // Load only 'en' not 'en-US'

    // Namespace configuration
    ns: ['translation'],
    defaultNS: 'translation',

    // Key separator
    keySeparator: '.',

    // Allow empty values
    returnEmptyString: false,

    // Return null for missing keys
    returnNull: false,

    // Save missing translations
    saveMissing: process.env.NODE_ENV === 'development',
    missingKeyHandler: (lng, ns, key, fallbackValue) => {
      if (process.env.NODE_ENV === 'development') {
        console.warn(`Missing translation: ${key} for language: ${lng}`);
      }
    }
  });

/**
 * Update HTML lang attribute when language changes
 */
i18n.on('languageChanged', (lng) => {
  const language = SUPPORTED_LANGUAGES.find(l => l.code === lng);
  if (language) {
    document.documentElement.lang = lng;
    document.documentElement.dir = language.dir;
  }
});

/**
 * Helper function to get current language info
 */
export const getCurrentLanguage = () => {
  const currentLng = i18n.language || 'en';
  return SUPPORTED_LANGUAGES.find(lang => lang.code === currentLng) || SUPPORTED_LANGUAGES[0];
};

/**
 * Helper function to change language
 */
export const changeLanguage = (languageCode) => {
  return i18n.changeLanguage(languageCode);
};

/**
 * Helper function to format number
 */
export const formatNumber = (value, options = {}) => {
  return new Intl.NumberFormat(i18n.language, options).format(value);
};

/**
 * Helper function to format currency
 */
export const formatCurrency = (value, currency = 'USD', options = {}) => {
  return new Intl.NumberFormat(i18n.language, {
    style: 'currency',
    currency,
    ...options
  }).format(value);
};

/**
 * Helper function to format date
 */
export const formatDate = (value, options = {}) => {
  return new Intl.DateTimeFormat(i18n.language, options).format(new Date(value));
};

/**
 * Helper function to format relative time
 */
export const formatRelativeTime = (value, unit = 'day') => {
  const rtf = new Intl.RelativeTimeFormat(i18n.language, { numeric: 'auto' });
  return rtf.format(value, unit);
};

export default i18n;
