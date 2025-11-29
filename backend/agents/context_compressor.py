"""Context Compression Module for Intelligent Token Management

This module provides intelligent context compression to manage token limits
when approaching the maximum context window of LLM models.
"""

from typing import Dict, Any, List, Optional, Tuple
import json
import logging
import re

logger = logging.getLogger(__name__)

# Token estimation constants (approximate)
CHARS_PER_TOKEN = 4  # Average characters per token
DEFAULT_MAX_TOKENS = 128000  # GPT-4o context window
SAFE_MARGIN = 0.85  # Use 85% of max tokens to leave room for response


class ContextCompressor:
    """Intelligent context compressor for managing LLM token limits"""
    
    def __init__(self, max_tokens: int = DEFAULT_MAX_TOKENS, safe_margin: float = SAFE_MARGIN):
        self.max_tokens = max_tokens
        self.safe_margin = safe_margin
        self.effective_max = int(max_tokens * safe_margin)
        
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count from text"""
        if not text:
            return 0
        return len(text) // CHARS_PER_TOKEN
    
    def estimate_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Estimate total tokens in a list of messages"""
        total = 0
        for msg in messages:
            total += self.estimate_tokens(msg.get('content', ''))
            total += 4  # Overhead for role, formatting
        return total
    
    def estimate_files_tokens(self, files: List[Dict[str, Any]]) -> int:
        """Estimate total tokens in project files"""
        total = 0
        for file in files:
            total += self.estimate_tokens(file.get('content', ''))
            total += self.estimate_tokens(file.get('name', ''))
            total += 10  # Overhead for structure
        return total
    
    def needs_compression(self, messages: List[Dict], files: List[Dict] = None, 
                          system_prompt: str = "") -> bool:
        """Check if context needs compression"""
        total = self.estimate_tokens(system_prompt)
        total += self.estimate_messages_tokens(messages)
        if files:
            total += self.estimate_files_tokens(files)
        
        return total > self.effective_max
    
    def compress_conversation(self, messages: List[Dict[str, str]], 
                               keep_recent: int = 6) -> List[Dict[str, str]]:
        """Compress conversation history while preserving recent context
        
        Strategy:
        1. Always keep the first message (original context/intent)
        2. Keep the last N messages (recent context)
        3. Summarize middle messages
        """
        if len(messages) <= keep_recent + 1:
            return messages
        
        compressed = []
        
        # Keep first message (original intent)
        if messages:
            compressed.append(messages[0])
        
        # Get middle messages to summarize
        middle_messages = messages[1:-keep_recent] if len(messages) > keep_recent + 1 else []
        
        if middle_messages:
            # Create summary of middle conversation
            summary = self._summarize_messages(middle_messages)
            compressed.append({
                "role": "system",
                "content": f"[Résumé conversation précédente: {summary}]"
            })
        
        # Keep recent messages
        recent = messages[-keep_recent:] if len(messages) >= keep_recent else messages[1:]
        compressed.extend(recent)
        
        logger.info(f"[Compressor] Compressed {len(messages)} messages to {len(compressed)}")
        return compressed
    
    def _summarize_messages(self, messages: List[Dict[str, str]]) -> str:
        """Create a brief summary of messages"""
        summaries = []
        
        for msg in messages:
            content = msg.get('content', '')[:200]  # First 200 chars
            role = msg.get('role', 'unknown')
            
            if role == 'user':
                # Extract key action words
                actions = self._extract_actions(content)
                if actions:
                    summaries.append(f"User: {actions}")
            elif role == 'assistant':
                # Extract what was done
                if 'généré' in content.lower() or 'created' in content.lower():
                    summaries.append("Assistant: Code généré")
                elif 'modifié' in content.lower() or 'updated' in content.lower():
                    summaries.append("Assistant: Code modifié")
                elif 'erreur' in content.lower() or 'error' in content.lower():
                    summaries.append("Assistant: Erreur traitée")
        
        return '; '.join(summaries[:5])  # Max 5 summary items
    
    def _extract_actions(self, text: str) -> str:
        """Extract action keywords from user message"""
        action_words = [
            'créer', 'create', 'ajouter', 'add', 'modifier', 'modify', 'update',
            'supprimer', 'delete', 'corriger', 'fix', 'améliorer', 'improve',
            'implémenter', 'implement', 'changer', 'change'
        ]
        
        text_lower = text.lower()
        found_actions = [word for word in action_words if word in text_lower]
        
        if found_actions:
            # Get first 50 chars with action context
            return text[:50].strip() + '...'
        return text[:30].strip() + '...' if len(text) > 30 else text
    
    def compress_files(self, files: List[Dict[str, Any]], 
                       max_file_tokens: int = 2000) -> List[Dict[str, Any]]:
        """Compress file contents while preserving structure
        
        Strategy:
        1. Keep file names and languages intact
        2. Truncate large files with smart summarization
        3. Preserve important sections (imports, exports, key functions)
        """
        compressed_files = []
        
        for file in files:
            content = file.get('content', '')
            name = file.get('name', '')
            language = file.get('language', 'plaintext')
            
            file_tokens = self.estimate_tokens(content)
            
            if file_tokens <= max_file_tokens:
                compressed_files.append(file)
            else:
                # Compress this file
                compressed_content = self._compress_file_content(
                    content, language, max_file_tokens
                )
                compressed_files.append({
                    'name': name,
                    'content': compressed_content,
                    'language': language,
                    '_compressed': True,
                    '_original_tokens': file_tokens
                })
        
        return compressed_files
    
    def _compress_file_content(self, content: str, language: str, 
                                max_tokens: int) -> str:
        """Intelligently compress file content based on language"""
        lines = content.split('\n')
        
        # Identify important sections
        important_lines = []
        other_lines = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Always keep these
            if self._is_important_line(stripped, language):
                important_lines.append((i, line))
            else:
                other_lines.append((i, line))
        
        # Build compressed content
        result_lines = []
        max_chars = max_tokens * CHARS_PER_TOKEN
        current_chars = 0
        
        # Add important lines first
        for i, line in important_lines:
            if current_chars + len(line) < max_chars * 0.7:  # 70% for important
                result_lines.append((i, line))
                current_chars += len(line)
        
        # Add context from other lines
        remaining_budget = max_chars - current_chars
        for i, line in other_lines[:20]:  # First 20 non-important lines
            if len(line) < remaining_budget:
                result_lines.append((i, line))
                remaining_budget -= len(line)
        
        # Sort by original line number and join
        result_lines.sort(key=lambda x: x[0])
        compressed = '\n'.join([line for _, line in result_lines])
        
        # Add truncation notice
        compressed += f"\n\n// ... [Fichier tronqué - {len(lines)} lignes originales]"
        
        return compressed
    
    def _is_important_line(self, line: str, language: str) -> bool:
        """Determine if a line is important for understanding the code"""
        if not line:
            return False
        
        # Universal important patterns
        important_patterns = [
            r'^import\s',
            r'^from\s.*import',
            r'^export\s',
            r'^class\s',
            r'^def\s',
            r'^function\s',
            r'^const\s.*=.*=>',  # Arrow functions
            r'^async\s+function',
            r'^interface\s',
            r'^type\s',
            r'@.*decorator',
            r'^#.*include',
        ]
        
        # Language-specific patterns
        if language in ['html', 'xml']:
            important_patterns.extend([
                r'^<(!DOCTYPE|html|head|body|script|style)',
                r'^</?(div|section|main|nav|header|footer)\s',
            ])
        elif language == 'css':
            important_patterns.extend([
                r'^\.',  # Class selectors
                r'^#',   # ID selectors  
                r'^@media',
                r'^@keyframes',
            ])
        elif language in ['javascript', 'typescript']:
            important_patterns.extend([
                r'^(var|let|const)\s+\w+\s*=\s*(function|async|\()',
                r'module\.exports',
                r'^export\s+(default|const|function|class)',
            ])
        
        for pattern in important_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        
        return False
    
    def get_compression_stats(self, original_messages: List[Dict], 
                              compressed_messages: List[Dict],
                              original_files: List[Dict] = None,
                              compressed_files: List[Dict] = None) -> Dict[str, Any]:
        """Get statistics about compression"""
        stats = {
            'messages': {
                'original_count': len(original_messages),
                'compressed_count': len(compressed_messages),
                'original_tokens': self.estimate_messages_tokens(original_messages),
                'compressed_tokens': self.estimate_messages_tokens(compressed_messages),
            }
        }
        
        if original_files and compressed_files:
            stats['files'] = {
                'original_count': len(original_files),
                'compressed_count': len(compressed_files),
                'original_tokens': self.estimate_files_tokens(original_files),
                'compressed_tokens': self.estimate_files_tokens(compressed_files),
            }
        
        # Calculate savings
        original_total = stats['messages']['original_tokens']
        compressed_total = stats['messages']['compressed_tokens']
        
        if 'files' in stats:
            original_total += stats['files']['original_tokens']
            compressed_total += stats['files']['compressed_tokens']
        
        stats['total'] = {
            'original_tokens': original_total,
            'compressed_tokens': compressed_total,
            'tokens_saved': original_total - compressed_total,
            'compression_ratio': round(compressed_total / original_total, 2) if original_total > 0 else 1
        }
        
        return stats


def compress_context_if_needed(
    messages: List[Dict[str, str]],
    files: List[Dict[str, Any]] = None,
    system_prompt: str = "",
    max_tokens: int = DEFAULT_MAX_TOKENS,
    keep_recent_messages: int = 6,
    max_file_tokens: int = 2000
) -> Tuple[List[Dict[str, str]], List[Dict[str, Any]], Dict[str, Any]]:
    """Convenience function to compress context if needed
    
    Returns:
        Tuple of (compressed_messages, compressed_files, stats)
    """
    compressor = ContextCompressor(max_tokens=max_tokens)
    
    if not compressor.needs_compression(messages, files, system_prompt):
        return messages, files or [], {'compressed': False}
    
    logger.info("[Compressor] Context exceeds limit, compressing...")
    
    compressed_messages = compressor.compress_conversation(
        messages, keep_recent=keep_recent_messages
    )
    
    compressed_files = files
    if files:
        compressed_files = compressor.compress_files(files, max_file_tokens)
    
    stats = compressor.get_compression_stats(
        messages, compressed_messages, files, compressed_files
    )
    stats['compressed'] = True
    
    logger.info(f"[Compressor] Compression complete - saved {stats['total']['tokens_saved']} tokens")
    
    return compressed_messages, compressed_files or [], stats
