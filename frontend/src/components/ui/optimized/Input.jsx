import React, { memo, forwardRef, useState } from 'react';
import { Eye, EyeOff, AlertCircle, CheckCircle } from 'lucide-react';
import { cn } from '../../../lib/utils';

/**
 * Input - Optimized input component with variants
 *
 * Features:
 * - Password visibility toggle
 * - Error and success states
 * - Left and right icons
 * - Helper text
 * - Character counter
 *
 * Performance optimizations:
 * - React.memo to prevent re-renders
 * - forwardRef for ref forwarding
 *
 * @version 2.0.0 - Optimized by Frontend Squad
 */
const Input = memo(forwardRef(function Input(
  {
    className,
    type = 'text',
    label,
    error,
    success,
    helperText,
    leftIcon,
    rightIcon,
    maxLength,
    showCharCount = false,
    disabled = false,
    ...props
  },
  ref
) {
  const [showPassword, setShowPassword] = useState(false);
  const [charCount, setCharCount] = useState(props.value?.length || 0);

  const isPassword = type === 'password';
  const inputType = isPassword && showPassword ? 'text' : type;

  const handleChange = (e) => {
    setCharCount(e.target.value.length);
    props.onChange?.(e);
  };

  return (
    <div className="w-full space-y-2">
      {/* Label */}
      {label && (
        <label className="text-sm font-medium text-foreground">
          {label}
          {props.required && <span className="text-destructive ml-1">*</span>}
        </label>
      )}

      {/* Input Container */}
      <div className="relative">
        {/* Left Icon */}
        {leftIcon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
            {leftIcon}
          </div>
        )}

        {/* Input */}
        <input
          ref={ref}
          type={inputType}
          maxLength={maxLength}
          disabled={disabled}
          className={cn(
            'flex h-10 w-full rounded-lg border bg-background px-3 py-2 text-sm',
            'transition-colors duration-200',
            'placeholder:text-muted-foreground',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
            'disabled:cursor-not-allowed disabled:opacity-50',
            leftIcon && 'pl-10',
            (rightIcon || isPassword || showCharCount) && 'pr-10',
            error && 'border-destructive focus-visible:ring-destructive',
            success && 'border-success focus-visible:ring-success',
            !error && !success && 'border-input focus-visible:ring-primary',
            className
          )}
          onChange={handleChange}
          {...props}
        />

        {/* Right Icons Container */}
        <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
          {/* Error Icon */}
          {error && (
            <AlertCircle className="w-4 h-4 text-destructive" />
          )}

          {/* Success Icon */}
          {success && !error && (
            <CheckCircle className="w-4 h-4 text-success" />
          )}

          {/* Custom Right Icon */}
          {rightIcon && !error && !success && (
            <div className="text-muted-foreground">{rightIcon}</div>
          )}

          {/* Password Toggle */}
          {isPassword && (
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="text-muted-foreground hover:text-foreground transition-colors"
              tabIndex={-1}
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? (
                <EyeOff className="w-4 h-4" />
              ) : (
                <Eye className="w-4 h-4" />
              )}
            </button>
          )}
        </div>
      </div>

      {/* Helper Text & Character Count */}
      <div className="flex items-center justify-between text-xs">
        {/* Helper Text or Error Message */}
        {(helperText || error) && (
          <span className={cn(
            'text-muted-foreground',
            error && 'text-destructive'
          )}>
            {error || helperText}
          </span>
        )}

        {/* Character Counter */}
        {showCharCount && maxLength && (
          <span className={cn(
            'text-muted-foreground ml-auto',
            charCount >= maxLength && 'text-destructive'
          )}>
            {charCount}/{maxLength}
          </span>
        )}
      </div>
    </div>
  );
}));

Input.displayName = 'Input';

export { Input };
