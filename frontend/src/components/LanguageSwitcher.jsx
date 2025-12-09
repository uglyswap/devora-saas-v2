/**
 * Language Switcher Component
 *
 * Allows users to change the application language
 * Implements WCAG 2.1 AA accessibility standards
 */

import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { SUPPORTED_LANGUAGES, changeLanguage, getCurrentLanguage } from '../i18n/config';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import { Button } from './ui/button';
import { Globe } from 'lucide-react';

/**
 * LanguageSwitcher Component
 *
 * @param {Object} props - Component props
 * @param {string} props.variant - Button variant (default, outline, ghost)
 * @param {string} props.size - Button size (default, sm, lg)
 * @param {boolean} props.showLabel - Show language label
 * @param {boolean} props.showFlag - Show flag emoji
 * @param {string} props.className - Additional CSS classes
 */
export function LanguageSwitcher({
  variant = 'outline',
  size = 'default',
  showLabel = true,
  showFlag = true,
  className = ''
}) {
  const { i18n } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const currentLanguage = getCurrentLanguage();

  const handleLanguageChange = async (languageCode) => {
    try {
      await changeLanguage(languageCode);
      setIsOpen(false);

      // Announce language change to screen readers
      const announcement = `Language changed to ${
        SUPPORTED_LANGUAGES.find(l => l.code === languageCode)?.name
      }`;
      announceToScreenReader(announcement);
    } catch (error) {
      console.error('Error changing language:', error);
    }
  };

  const announceToScreenReader = (message) => {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    document.body.appendChild(announcement);

    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  };

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button
          variant={variant}
          size={size}
          className={className}
          aria-label={`Current language: ${currentLanguage.nativeName}. Click to change language`}
          aria-expanded={isOpen}
          aria-haspopup="menu"
        >
          <Globe className="h-4 w-4" aria-hidden="true" />
          {showFlag && (
            <span className="ml-2" aria-hidden="true">
              {currentLanguage.flag}
            </span>
          )}
          {showLabel && (
            <span className="ml-2">{currentLanguage.nativeName}</span>
          )}
        </Button>
      </DropdownMenuTrigger>

      <DropdownMenuContent
        align="end"
        role="menu"
        aria-label="Language selection"
      >
        {SUPPORTED_LANGUAGES.map((language) => (
          <DropdownMenuItem
            key={language.code}
            onClick={() => handleLanguageChange(language.code)}
            role="menuitem"
            aria-current={i18n.language === language.code ? 'true' : 'false'}
            className={`
              cursor-pointer
              ${i18n.language === language.code ? 'bg-accent font-semibold' : ''}
            `}
          >
            <span className="mr-2" aria-hidden="true">
              {language.flag}
            </span>
            <span>{language.nativeName}</span>
            {i18n.language === language.code && (
              <span className="ml-auto text-xs" aria-label="Currently selected">
                ✓
              </span>
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

/**
 * Compact Language Switcher (Icon Only)
 */
export function LanguageSwitcherCompact(props) {
  return (
    <LanguageSwitcher
      {...props}
      showLabel={false}
      showFlag={false}
    />
  );
}

/**
 * Language Switcher with Flags
 */
export function LanguageSwitcherWithFlags(props) {
  return (
    <LanguageSwitcher
      {...props}
      showLabel={true}
      showFlag={true}
    />
  );
}

/**
 * Inline Language Selector (Radio Group)
 * Alternative implementation for settings pages
 */
export function InlineLanguageSelector({ className = '' }) {
  const { i18n } = useTranslation();

  const handleChange = async (languageCode) => {
    try {
      await changeLanguage(languageCode);
    } catch (error) {
      console.error('Error changing language:', error);
    }
  };

  return (
    <div
      role="radiogroup"
      aria-label="Language selection"
      className={`flex flex-col gap-2 ${className}`}
    >
      {SUPPORTED_LANGUAGES.map((language) => (
        <label
          key={language.code}
          className={`
            flex items-center gap-3 p-3 rounded-lg border cursor-pointer
            transition-colors hover:bg-accent/50
            ${i18n.language === language.code ? 'border-primary bg-accent' : 'border-border'}
          `}
        >
          <input
            type="radio"
            name="language"
            value={language.code}
            checked={i18n.language === language.code}
            onChange={(e) => handleChange(e.target.value)}
            className="sr-only"
            role="radio"
            aria-checked={i18n.language === language.code}
          />
          <div
            className={`
              w-4 h-4 rounded-full border-2 flex items-center justify-center
              ${i18n.language === language.code ? 'border-primary' : 'border-muted-foreground'}
            `}
            aria-hidden="true"
          >
            {i18n.language === language.code && (
              <div className="w-2 h-2 rounded-full bg-primary" />
            )}
          </div>
          <span className="text-2xl" aria-hidden="true">
            {language.flag}
          </span>
          <div className="flex-1">
            <div className="font-medium">{language.nativeName}</div>
            <div className="text-sm text-muted-foreground">{language.name}</div>
          </div>
          {i18n.language === language.code && (
            <span className="text-primary font-semibold text-sm">
              ✓ Selected
            </span>
          )}
        </label>
      ))}
    </div>
  );
}

export default LanguageSwitcher;
