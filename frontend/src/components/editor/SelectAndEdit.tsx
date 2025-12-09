/**
 * SelectAndEdit - Visual element selection and AI-powered editing
 *
 * This component provides Lovable-style Select & Edit functionality
 * allowing users to click on preview elements and describe changes.
 *
 * @author Devora Team
 * @version 2.0.0
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import {
  MousePointer2,
  Wand2,
  X,
  Send,
  Loader2,
  Eye,
  EyeOff,
  Undo2,
  Redo2,
  Palette,
  Type,
  Layout,
  Image,
  Code2
} from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Popover, PopoverContent, PopoverTrigger } from '../ui/popover';
import { Tooltip, TooltipContent, TooltipTrigger } from '../ui/tooltip';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { Separator } from '../ui/separator';
import { cn } from '../../lib/utils';
import { toast } from 'sonner';

interface ElementInfo {
  tagName: string;
  className: string;
  id: string;
  textContent: string;
  computedStyles: {
    color: string;
    backgroundColor: string;
    fontSize: string;
    fontFamily: string;
    padding: string;
    margin: string;
    borderRadius: string;
  };
  rect: DOMRect;
  xpath: string;
  selector: string;
}

interface EditSuggestion {
  id: string;
  type: 'style' | 'content' | 'layout' | 'component';
  description: string;
  preview?: string;
}

interface SelectAndEditProps {
  iframeRef: React.RefObject<HTMLIFrameElement>;
  onEditRequest: (element: ElementInfo, instruction: string) => Promise<void>;
  isLoading?: boolean;
  className?: string;
}

interface EditHistory {
  id: string;
  element: ElementInfo;
  instruction: string;
  timestamp: Date;
  applied: boolean;
}

function getXPath(element: Element): string {
  if (element.id) {
    return `//*[@id="${element.id}"]`;
  }

  const parts: string[] = [];
  let current: Element | null = element;

  while (current && current.nodeType === Node.ELEMENT_NODE) {
    let index = 1;
    let sibling: Element | null = current.previousElementSibling;

    while (sibling) {
      if (sibling.tagName === current.tagName) {
        index++;
      }
      sibling = sibling.previousElementSibling;
    }

    const tagName = current.tagName.toLowerCase();
    const part = index > 1 ? `${tagName}[${index}]` : tagName;
    parts.unshift(part);
    current = current.parentElement;
  }

  return '/' + parts.join('/');
}

function getSelector(element: Element): string {
  if (element.id) {
    return `#${element.id}`;
  }

  const path: string[] = [];
  let current: Element | null = element;

  while (current && current !== document.body) {
    let selector = current.tagName.toLowerCase();

    if (current.className && typeof current.className === 'string') {
      const classes = current.className.trim().split(/\s+/).filter(c => c);
      if (classes.length > 0) {
        selector += '.' + classes.slice(0, 2).join('.');
      }
    }

    const parent = current.parentElement;
    if (parent) {
      const siblings = Array.from(parent.children).filter(
        child => child.tagName === current!.tagName
      );
      if (siblings.length > 1) {
        const index = siblings.indexOf(current) + 1;
        selector += `:nth-child(${index})`;
      }
    }

    path.unshift(selector);
    current = current.parentElement;
  }

  return path.join(' > ');
}

function extractElementInfo(element: Element): ElementInfo {
  const computedStyle = window.getComputedStyle(element);
  const rect = element.getBoundingClientRect();

  return {
    tagName: element.tagName.toLowerCase(),
    className: element.className || '',
    id: element.id || '',
    textContent: (element.textContent || '').trim().slice(0, 100),
    computedStyles: {
      color: computedStyle.color,
      backgroundColor: computedStyle.backgroundColor,
      fontSize: computedStyle.fontSize,
      fontFamily: computedStyle.fontFamily,
      padding: computedStyle.padding,
      margin: computedStyle.margin,
      borderRadius: computedStyle.borderRadius
    },
    rect,
    xpath: getXPath(element),
    selector: getSelector(element)
  };
}

function getQuickSuggestions(element: ElementInfo): EditSuggestion[] {
  const suggestions: EditSuggestion[] = [];

  suggestions.push(
    { id: 'change-color', type: 'style', description: 'Change color' },
    { id: 'change-size', type: 'style', description: 'Make it bigger/smaller' }
  );

  switch (element.tagName) {
    case 'button':
      suggestions.push(
        { id: 'change-text', type: 'content', description: 'Change button text' },
        { id: 'add-icon', type: 'component', description: 'Add icon' },
        { id: 'change-variant', type: 'style', description: 'Change button style' }
      );
      break;
    case 'h1':
    case 'h2':
    case 'h3':
    case 'p':
      suggestions.push(
        { id: 'change-text', type: 'content', description: 'Change text' },
        { id: 'change-font', type: 'style', description: 'Change font' }
      );
      break;
    case 'img':
      suggestions.push(
        { id: 'change-image', type: 'content', description: 'Change image' },
        { id: 'add-border', type: 'style', description: 'Add border/shadow' }
      );
      break;
    case 'div':
    case 'section':
      suggestions.push(
        { id: 'change-layout', type: 'layout', description: 'Change layout' },
        { id: 'add-spacing', type: 'style', description: 'Adjust spacing' },
        { id: 'add-background', type: 'style', description: 'Add background' }
      );
      break;
    case 'input':
    case 'textarea':
      suggestions.push(
        { id: 'change-placeholder', type: 'content', description: 'Change placeholder' },
        { id: 'add-validation', type: 'component', description: 'Add validation' }
      );
      break;
    case 'a':
      suggestions.push(
        { id: 'change-link', type: 'content', description: 'Change link' },
        { id: 'change-text', type: 'content', description: 'Change text' }
      );
      break;
  }

  return suggestions;
}

export function SelectAndEdit({
  iframeRef,
  onEditRequest,
  isLoading = false,
  className
}: SelectAndEditProps) {
  const [isActive, setIsActive] = useState(false);
  const [selectedElement, setSelectedElement] = useState<ElementInfo | null>(null);
  const [hoveredElement, setHoveredElement] = useState<ElementInfo | null>(null);
  const [editInstruction, setEditInstruction] = useState('');
  const [editHistory, setEditHistory] = useState<EditHistory[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [showQuickActions, setShowQuickActions] = useState(false);

  const handleIframeMouseMove = useCallback((e: MouseEvent) => {
    if (!isActive || !iframeRef.current) return;

    const target = e.target as Element;
    if (target && target !== document.body && target !== document.documentElement) {
      const info = extractElementInfo(target);
      setHoveredElement(info);
    }
  }, [isActive, iframeRef]);

  const handleIframeClick = useCallback((e: MouseEvent) => {
    if (!isActive || !iframeRef.current) return;

    e.preventDefault();
    e.stopPropagation();

    const target = e.target as Element;
    if (target && target !== document.body && target !== document.documentElement) {
      const info = extractElementInfo(target);
      setSelectedElement(info);
      setShowQuickActions(true);
      toast.success(`Selected: ${info.tagName}${info.className ? '.' + info.className.split(' ')[0] : ''}`);
    }
  }, [isActive, iframeRef]);

  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;

    const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
    if (!iframeDoc) return;

    if (isActive) {
      iframeDoc.addEventListener('mousemove', handleIframeMouseMove);
      iframeDoc.addEventListener('click', handleIframeClick, true);
      iframeDoc.body.style.cursor = 'crosshair';

      const styleId = 'devora-select-edit-styles';
      if (!iframeDoc.getElementById(styleId)) {
        const style = iframeDoc.createElement('style');
        style.id = styleId;
        style.textContent = `
          .devora-highlight {
            outline: 2px dashed #3b82f6 !important;
            outline-offset: 2px !important;
          }
          .devora-selected {
            outline: 3px solid #8b5cf6 !important;
            outline-offset: 2px !important;
          }
        `;
        iframeDoc.head.appendChild(style);
      }
    }

    return () => {
      if (iframeDoc) {
        iframeDoc.removeEventListener('mousemove', handleIframeMouseMove);
        iframeDoc.removeEventListener('click', handleIframeClick, true);
        iframeDoc.body.style.cursor = '';
      }
    };
  }, [isActive, iframeRef, handleIframeMouseMove, handleIframeClick]);

  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;

    const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
    if (!iframeDoc) return;

    iframeDoc.querySelectorAll('.devora-highlight').forEach(el => {
      el.classList.remove('devora-highlight');
    });

    if (hoveredElement && isActive) {
      const el = iframeDoc.querySelector(hoveredElement.selector);
      if (el) {
        el.classList.add('devora-highlight');
      }
    }
  }, [hoveredElement, isActive, iframeRef]);

  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;

    const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
    if (!iframeDoc) return;

    iframeDoc.querySelectorAll('.devora-selected').forEach(el => {
      el.classList.remove('devora-selected');
    });

    if (selectedElement) {
      const el = iframeDoc.querySelector(selectedElement.selector);
      if (el) {
        el.classList.add('devora-selected');
      }
    }
  }, [selectedElement, iframeRef]);

  const handleSubmitEdit = async () => {
    if (!selectedElement || !editInstruction.trim()) {
      toast.error('Please select an element and enter an instruction');
      return;
    }

    try {
      await onEditRequest(selectedElement, editInstruction);

      const historyEntry: EditHistory = {
        id: `edit-${Date.now()}`,
        element: selectedElement,
        instruction: editInstruction,
        timestamp: new Date(),
        applied: true
      };

      setEditHistory(prev => [...prev.slice(0, historyIndex + 1), historyEntry]);
      setHistoryIndex(prev => prev + 1);

      setEditInstruction('');
      setSelectedElement(null);
      setShowQuickActions(false);

      toast.success('Edit applied!');
    } catch (error) {
      toast.error('Failed to apply edit');
    }
  };

  const handleQuickSuggestion = (suggestion: EditSuggestion) => {
    setEditInstruction(suggestion.description);
  };

  const handleUndo = () => {
    if (historyIndex >= 0) {
      setHistoryIndex(prev => prev - 1);
      toast.info('Undone');
    }
  };

  const handleRedo = () => {
    if (historyIndex < editHistory.length - 1) {
      setHistoryIndex(prev => prev + 1);
      toast.info('Redone');
    }
  };

  const quickSuggestions = selectedElement ? getQuickSuggestions(selectedElement) : [];

  return (
    <div className={cn('flex flex-col gap-2', className)}>
      <div className="flex items-center gap-2 p-2 bg-muted/50 rounded-lg">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant={isActive ? 'default' : 'outline'}
              size="sm"
              onClick={() => {
                setIsActive(!isActive);
                if (!isActive) {
                  toast.info('Click on any element in the preview to select it');
                }
              }}
              className="gap-1.5"
            >
              <MousePointer2 className="h-4 w-4" />
              {isActive ? 'Stop Selecting' : 'Select Element'}
            </Button>
          </TooltipTrigger>
          <TooltipContent>Click to enable element selection mode</TooltipContent>
        </Tooltip>

        <Separator orientation="vertical" className="h-6" />

        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="outline" size="icon" onClick={handleUndo} disabled={historyIndex < 0}>
              <Undo2 className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Undo</TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="outline" size="icon" onClick={handleRedo} disabled={historyIndex >= editHistory.length - 1}>
              <Redo2 className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Redo</TooltipContent>
        </Tooltip>

        {editHistory.length > 0 && (
          <Badge variant="secondary" className="ml-2">
            {editHistory.length} edit{editHistory.length > 1 ? 's' : ''}
          </Badge>
        )}
      </div>

      {selectedElement && (
        <div className="p-3 border rounded-lg bg-background space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Code2 className="h-4 w-4 text-muted-foreground" />
              <span className="font-mono text-sm">
                &lt;{selectedElement.tagName}
                {selectedElement.className && (
                  <span className="text-blue-500">
                    .{selectedElement.className.split(' ')[0]}
                  </span>
                )}
                &gt;
              </span>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              onClick={() => {
                setSelectedElement(null);
                setShowQuickActions(false);
              }}
            >
              <X className="h-3 w-3" />
            </Button>
          </div>

          {selectedElement.textContent && (
            <p className="text-sm text-muted-foreground truncate">
              "{selectedElement.textContent}"
            </p>
          )}

          {showQuickActions && (
            <div className="flex flex-wrap gap-1.5">
              {quickSuggestions.map(suggestion => (
                <Button
                  key={suggestion.id}
                  variant="outline"
                  size="sm"
                  className="h-7 text-xs"
                  onClick={() => handleQuickSuggestion(suggestion)}
                >
                  {suggestion.type === 'style' && <Palette className="h-3 w-3 mr-1" />}
                  {suggestion.type === 'content' && <Type className="h-3 w-3 mr-1" />}
                  {suggestion.type === 'layout' && <Layout className="h-3 w-3 mr-1" />}
                  {suggestion.type === 'component' && <Image className="h-3 w-3 mr-1" />}
                  {suggestion.description}
                </Button>
              ))}
            </div>
          )}

          <div className="flex gap-2">
            <Textarea
              placeholder="Describe what you want to change..."
              value={editInstruction}
              onChange={(e) => setEditInstruction(e.target.value)}
              className="min-h-[60px] text-sm resize-none"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                  handleSubmitEdit();
                }
              }}
            />
            <Button
              onClick={handleSubmitEdit}
              disabled={isLoading || !editInstruction.trim()}
              className="self-end"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>
                  <Wand2 className="h-4 w-4 mr-1" />
                  Apply
                </>
              )}
            </Button>
          </div>

          <p className="text-xs text-muted-foreground">Press Ctrl+Enter to apply</p>
        </div>
      )}

      {isActive && hoveredElement && !selectedElement && (
        <div className="p-2 border rounded-lg bg-muted/30 text-sm">
          <span className="font-mono">&lt;{hoveredElement.tagName}&gt;</span>
          {hoveredElement.textContent && (
            <span className="text-muted-foreground ml-2 truncate">
              {hoveredElement.textContent.slice(0, 50)}...
            </span>
          )}
        </div>
      )}

      {editHistory.length > 0 && (
        <Popover>
          <PopoverTrigger asChild>
            <Button variant="outline" size="sm" className="w-fit">
              View Edit History ({editHistory.length})
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-80">
            <ScrollArea className="h-64">
              <div className="space-y-2">
                {editHistory.map((entry, index) => (
                  <div
                    key={entry.id}
                    className={cn(
                      'p-2 rounded border text-sm',
                      index <= historyIndex ? 'bg-background' : 'bg-muted/50 opacity-50'
                    )}
                  >
                    <div className="font-mono text-xs text-muted-foreground">
                      {entry.element.tagName}
                      {entry.element.className && `.${entry.element.className.split(' ')[0]}`}
                    </div>
                    <p className="mt-1">{entry.instruction}</p>
                    <time className="text-xs text-muted-foreground">
                      {entry.timestamp.toLocaleTimeString()}
                    </time>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </PopoverContent>
        </Popover>
      )}
    </div>
  );
}

export default SelectAndEdit;
