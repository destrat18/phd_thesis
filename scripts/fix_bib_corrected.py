#!/usr/bin/env python3
"""
Bibliography Management Tool for Merging Papers into Thesis

Purpose:
  - Detect duplicate BibTeX entries (by author, year, title, DOI, ISBN, URL)
  - Standardize citation key naming to format: lastnameYYYYshortword (e.g., albert2009termination)
  - Remove duplicate entries and update all .tex files with new keys
  - Preserve BibTeX file formatting and comments

Safety Features:
  - Creates automatic backup before making changes
  - Dry-run mode to preview changes before applying
  - Only modifies keys within \cite{} and related commands
"""

import re
import os
import sys
import unicodedata
import argparse
from collections import defaultdict
from urllib.parse import urlparse

# Default configuration paths
BIB_PATH = 'refs.bib'
BACKUP_PATH = BIB_PATH + '.bak'
BASE_DIR = '.'

# ============================================================================
# REGEX PATTERNS - CORRECTED
# ============================================================================

# Pattern to match BibTeX entry headers: @type{key,
# FIXED: Added proper named group syntax (?P<name>...)
entry_re = re.compile(
    r'@(?P<type>\w+)\s*\{\s*(?P<key>[^,]+),',
    re.IGNORECASE
)

# Pattern to extract field values from BibTeX entries
# Matches: fieldname = {value} or "value" or plain value
# FIXED: Named groups now have proper syntax
field_re = re.compile(
    r'(?P<field_name>\w+)\s*=\s*(?P<field_value>\{(?:[^{}]|\{[^}]*\})*\}|"[^"]*"|[^,\n]+)',
    re.IGNORECASE
)

# Common English stopwords for generating short key names
COMMON_STOPWORDS = {'the', 'and', 'of', 'for', 'on', 'in', 'a', 'an', 'to', 
                    'with', 'by', 'via', 'using', 'from', 'at', 'or', 'is'}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def asciiify(s):
    """
    Convert string to ASCII-only, removing accents and special characters.
    
    Args:
        s: Input string
        
    Returns:
        ASCII-normalized lowercase string
        
    Example:
        asciiify("Müller") -> "muller"
    """
    if not s:
        return ''
    # Normalize Unicode (NFKD = compatibility decomposition)
    s = unicodedata.normalize('NFKD', s)
    # Encode to ASCII, dropping non-ASCII characters
    s = s.encode('ascii', 'ignore').decode('ascii')
    return s


def first_author_lastname(author_field):
    """
    Extract the last name of the first author from a BibTeX author field.
    
    BibTeX author format: "Last, First and Last2, First2 and ..."
    
    Args:
        author_field: BibTeX author field value
        
    Returns:
        ASCII-normalized lowercase last name (e.g., "einstein")
        
    Example:
        first_author_lastname("Albert Einstein and Niels Bohr")
        -> "einstein"
    """
    if not author_field:
        return 'unknown'
    
    # Split multiple authors by 'and' (BibTeX standard)
    authors = [a.strip() for a in re.split(r'\s+and\s+', author_field, flags=re.IGNORECASE)]
    first = authors[0]
    
    # Two BibTeX author name formats:
    # 1. "Last, First" format
    # 2. "First Last" format
    if ',' in first:
        # Format: "Last, First"
        last = first.split(',')[0].strip()
    else:
        # Format: "First Last" - take the last word
        parts = first.split()
        last = parts[-1] if parts else 'unknown'
    
    # Normalize and extract alphanumeric only
    last = asciiify(last).lower()
    last = re.sub(r'[^a-z0-9]', '', last)
    
    return last or 'unknown'


def extract_field(entry_text, name):
    """
    Extract a field value from a BibTeX entry.
    
    Handles three formats:
    - Braced: field = {value with {nested braces}}
    - Quoted: field = "quoted value"
    - Plain: field = plainvalue (until comma or newline)
    
    Args:
        entry_text: Full BibTeX entry text
        name: Field name to extract (e.g., "author", "title", "year")
        
    Returns:
        Field value (with outer braces/quotes removed) or None if not found
    """
    # Regex to find: fieldname = {value} or "value" or plain
    # Group 2: content inside braces
    # Group 3: content inside quotes
    # Group 4: plain unquoted value
    m = re.search(
        r'%s\s*=\s*(\{((?:[^{}]|\{[^}]*\})*)\}|"([^"]*)"|([^,\n]+))' % re.escape(name),
        entry_text,
        re.IGNORECASE
    )
    
    if not m:
        return None
    
    # Get whichever group matched (braces, quotes, or plain)
    val = m.group(2) or m.group(3) or m.group(4)
    
    if val is None:
        return None
    
    return val.strip()


def short_title_word(title_field):
    """
    Extract first meaningful (non-stopword) word from title for key generation.
    
    Args:
        title_field: BibTeX title field value
        
    Returns:
        First non-stopword (lowercase), or "misc" if title is empty
        
    Example:
        short_title_word("The Analysis of Algorithms")
        -> "analysis"
    """
    if not title_field:
        return 'misc'
    
    # Remove LaTeX commands like \emph{}, \textbf{}, \cite{}, etc.
    t = re.sub(r'\\[A-Za-z]+\*?(?:\[[^\]]*\])?(?:\{[^}]*\})?', '', title_field)
    
    # Remove braces and quotes
    t = re.sub(r'[{}"\\]', '', t)
    
    # Normalize to ASCII and lowercase
    t = asciiify(t).lower()
    
    # Extract words (alphanumeric sequences)
    words = re.findall(r'[a-z0-9]+', t)
    
    # Return first non-stopword, or first word if all are stopwords
    for w in words:
        if w not in COMMON_STOPWORDS:
            return w
    
    return words[0] if words else 'misc'


def make_key(last, year, word):
    """
    Generate standard BibTeX key from author, year, and title word.
    
    Format: lastnameYEARword (e.g., "einstein1905photon")
    
    Args:
        last: Last name (lowercase, ASCII)
        year: Publication year (or None)
        word: Title keyword (lowercase, ASCII)
        
    Returns:
        Generated key string
    """
    # Use 'noyear' if year is missing
    y = year if year else 'noyear'
    return f"{last}{y}{word}"


def extract_domain_from_url(url):
    """
    Extract domain name from URL and format as CamelCase.
    
    Args:
        url: URL (with or without scheme)
        
    Returns:
        Domain formatted as CamelCase (e.g., "HashrateindexCom")
        or None if invalid
        
    Example:
        extract_domain_from_url("https://www.example.com")
        -> "ExampleCom"
    """
    if not url:
        return None
    
    # Remove LaTeX \url{} command if present
    url = re.sub(r'\\url\{([^}]*)\}', r'\1', url)
    url = url.strip()
    
    # Add https:// if no scheme specified (required for urlparse)
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Parse URL to extract domain
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
    except Exception:
        return None
    
    if not domain:
        return None
    
    # Remove www. prefix
    if domain.startswith('www.'):
        domain = domain[4:]
    
    # Convert to CamelCase: "example.com" -> "ExampleCom"
    parts = domain.split('.')
    if len(parts) > 1:
        result = ''.join(part.capitalize() for part in parts)
        return result
    
    return domain.capitalize()


def title_to_camel_case_words(title_field, min_words=3):
    """
    Convert title to CamelCase using at least min_words significant words.
    
    Args:
        title_field: BibTeX title field value
        min_words: Minimum number of words to use (default: 3)
        
    Returns:
        CamelCase string (e.g., "AnalysisOfAlgorithms")
        
    Example:
        title_to_camel_case_words("The Analysis of Algorithms")
        -> "AnalysisOfAlgorithms"
    """
    if not title_field:
        return ''
    
    # Remove LaTeX commands
    t = re.sub(r'\\[A-Za-z]+\*?(?:\[[^\]]*\])?(?:\{[^}]*\})?', '', title_field)
    
    # Remove braces and quotes
    t = re.sub(r'[{}"\\]', '', t)
    
    # Normalize to ASCII
    t = asciiify(t)
    
    # Extract words (sequences of alphanumeric)
    words = re.findall(r'[A-Za-z0-9]+', t)
    
    selected = []
    
    # Collect min_words, preferring non-stopwords
    for w in words:
        if len(selected) >= min_words:
            break
        
        # Include word if it's not a stopword, or if it's the first word
        if w.lower() not in COMMON_STOPWORDS or len(selected) == 0:
            selected.append(w.capitalize())
    
    # If we don't have enough words, just take first min_words
    if len(selected) < min_words:
        selected = [w.capitalize() for w in words[:min_words]]
    
    return ''.join(selected)


def make_key_from_url(url, title):
    """
    Generate BibTeX key for web sources: DomainCamelCase + TitleWordsCamelCase.
    
    Used for entries without authors that have URLs.
    
    Args:
        url: URL field
        title: Title field
        
    Returns:
        Generated key (e.g., "ExampleComAnalysisOfAlgorithms")
    """
    # Extract domain as CamelCase
    domain = extract_domain_from_url(url)
    if not domain:
        domain = 'Web'
    
    # Extract title words as CamelCase
    title_part = title_to_camel_case_words(title, min_words=3)
    if not title_part:
        title_part = 'Page'
    
    # Combine and sanitize
    key = f"{domain}{title_part}"
    
    # Remove any remaining invalid characters (just in case)
    key = re.sub(r'[^a-zA-Z0-9]', '', key)
    
    return key


def read_file(path):
    """
    Read file with encoding fallback.
    
    Tries UTF-8 first, then falls back to Latin-1 for legacy files.
    
    Args:
        path: File path
        
    Returns:
        File contents as string
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Fallback for files with special bytes (old BibTeX files)
        with open(path, 'r', encoding='latin-1') as f:
            return f.read()


def write_file(path, data):
    """
    Write data to file in UTF-8 encoding.
    
    Args:
        path: File path
        data: Data to write
    """
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)


# ============================================================================
# PARSING FUNCTIONS
# ============================================================================

def parse_entries(bibtext):
    """
    Parse BibTeX file into individual entries.
    
    Returns entries as tuples: (key, type, full_entry_text)
    
    Args:
        bibtext: Full BibTeX file contents
        
    Returns:
        List of (key, type, entry_text) tuples
        
    Note:
        Each entry is extracted from one @type{key, to the next entry start.
        This preserves the exact formatting including whitespace and comments.
    """
    entries = []
    
    # Find all entry starts: @type{key,
    matches = list(entry_re.finditer(bibtext))
    
    # For each entry, extract from current start to next start (or EOF)
    for i, m in enumerate(matches):
        start = m.start()
        # End at next entry start, or end of file
        end = matches[i + 1].start() if i + 1 < len(matches) else len(bibtext)
        
        # Extract entry text and clean up trailing whitespace
        entry_text = bibtext[start:end].rstrip('\n')
        
        entry_type = m.group('type')
        key = m.group('key').strip()
        
        entries.append((key, entry_type, entry_text))
    
    return entries


# ============================================================================
# DUPLICATE DETECTION
# ============================================================================

def find_duplicates(bibtext):
    """
    Find duplicate BibTeX entries by comparing normalized metadata.
    
    Duplicates are identified by matching (author, year, title) signature,
    with additional checks for DOI, ISBN, and URL when available.
    
    Args:
        bibtext: Full BibTeX file contents
        
    Returns:
        Tuple: (duplicates_dict, entries_list)
        - duplicates_dict: {signature: [key1, key2, ...], ...}
        - entries_list: [(key, type, text), ...]
    """
    entries = parse_entries(bibtext)
    
    # Map from normalized signature -> list of keys with that signature
    signature_map = defaultdict(list)
    
    for key, etype, entry_text in entries:
        # Extract metadata for comparison
        author = extract_field(entry_text, 'author') or extract_field(entry_text, 'editor')
        year = extract_field(entry_text, 'year')
        title = extract_field(entry_text, 'title')
        
        # Additional fields for more reliable duplicate detection
        doi = extract_field(entry_text, 'doi')
        isbn = extract_field(entry_text, 'isbn')
        url = extract_field(entry_text, 'url')
        
        # Normalize all fields to lowercase ASCII for comparison
        author_norm = asciiify(author or '').lower() if author else ''
        title_norm = asciiify(title or '').lower() if title else ''
        year_norm = year or ''
        doi_norm = asciiify(doi or '').lower() if doi else ''
        isbn_norm = asciiify(isbn or '').lower() if isbn else ''
        url_norm = asciiify(url or '').lower() if url else ''
        
        # Create signature: primary by (author, year, title), secondary by identifiers
        signature = (author_norm, year_norm, title_norm, doi_norm, isbn_norm, url_norm)
        signature_map[signature].append(key)
    
    # Extract only signatures with duplicates (2+ keys)
    duplicates = {sig: keys for sig, keys in signature_map.items() if len(keys) > 1}
    
    return duplicates, entries


def spot_duplicates():
    """
    Report duplicate entries and keys with non-standard naming.
    
    Desired key format: lastnameYYYYword (e.g., "einstein1905photon")
    Acceptable variants: base or base + numeric suffix (e.g., "einstein1905photon2")
    
    This is a read-only analysis function - no files are modified.
    """
    if not os.path.exists(BIB_PATH):
        print(f'ERROR: {BIB_PATH} not found', file=sys.stderr)
        sys.exit(1)
    
    bibtext = read_file(BIB_PATH)
    duplicates, entries = find_duplicates(bibtext)
    
    # --- REPORT DUPLICATES ---
    if duplicates:
        print(f"Found {len(duplicates)} groups of duplicate entries:\n")
        
        for i, (sig, keys) in enumerate(duplicates.items(), 1):
            author_norm, year_norm, title_norm, doi_norm, isbn_norm, url_norm = sig
            
            print(f"Group {i}:")
            print(f"  Keys: {', '.join(keys)}")
            if author_norm:
                print(f"  Author: {author_norm}")
            if year_norm:
                print(f"  Year: {year_norm}")
            if title_norm:
                # Truncate long titles
                title_display = title_norm[:80] + "..." if len(title_norm) > 80 else title_norm
                print(f"  Title: {title_display}")
            if doi_norm:
                print(f"  DOI: {doi_norm}")
            if isbn_norm:
                print(f"  ISBN: {isbn_norm}")
            if url_norm:
                print(f"  URL: {url_norm}")
            print()
    else:
        print("✓ No duplicates found!")
    
    # --- REPORT WRONG KEY NAMES ---
    print()
    wrong_names = {}
    pattern_ok_cache = {}
    
    for key, etype, entry_text in entries:
        # Extract metadata for key generation
        author = extract_field(entry_text, 'author') or extract_field(entry_text, 'editor')
        year = extract_field(entry_text, 'year') or ''
        title = extract_field(entry_text, 'title') or ''
        url = extract_field(entry_text, 'url')
        
        # Generate what the key SHOULD be
        if not author and url:
            # Web source without author: use domain + title format
            base = make_key_from_url(url, title)
        else:
            # Standard format: authorYEARword
            last = first_author_lastname(author)
            word = short_title_word(title)
            base = make_key(last, year, word)
        
        # Cache compiled regex for performance
        if base not in pattern_ok_cache:
            # Acceptable: exact base, or base + numeric suffix
            pattern_ok_cache[base] = re.compile(
                r'^' + re.escape(base) + r'(?:\d+)?$'
            )
        
        # Check if current key matches the expected pattern
        if not pattern_ok_cache[base].match(key):
            wrong_names[key] = base
    
    if wrong_names:
        print(f"Found {len(wrong_names)} keys with unexpected names:\n")
        
        for old, base in sorted(wrong_names.items(), key=lambda x: x[0]):
            print(f"  {old}")
            print(f"    → suggested base: {base}\n")
    else:
        print("✓ All keys conform to the desired naming pattern.")


# ============================================================================
# FIXING FUNCTIONS
# ============================================================================

def fix_all(dry_run=False):
    """
    Comprehensive fix: remove duplicates and rename all keys to standard format.
    
    This function:
    1. Identifies duplicate entries (by author, year, title, DOI, ISBN, URL)
    2. Removes duplicates, keeping the first occurrence
    3. Renames all remaining entries to standard format (authorYEARword)
    4. Updates all .tex files with new key mappings in \cite{} commands
    5. Creates a backup of the original .bib file
    
    Args:
        dry_run: If True, print what would be done without modifying files
    """
    if not os.path.exists(BIB_PATH):
        print(f'ERROR: {BIB_PATH} not found', file=sys.stderr)
        sys.exit(1)
    
    bibtext = read_file(BIB_PATH)
    
    # Create backup BEFORE any modifications
    if not dry_run:
        try:
            write_file(BACKUP_PATH, bibtext)
            print(f"✓ Created backup at {BACKUP_PATH}\n")
        except IOError as e:
            print(f"ERROR: Failed to create backup: {e}", file=sys.stderr)
            sys.exit(1)
    
    # ========== STEP 1: FIND AND REMOVE DUPLICATES ==========
    
    duplicates, entries = find_duplicates(bibtext)
    
    # Build mapping from old keys (duplicates) to canonical keys (kept)
    dup_mapping = {}
    indices_to_remove = set()
    
    if duplicates:
        print(f"Found {len(duplicates)} groups of duplicate entries")
        
        # For each duplicate group, keep first, map others to it, mark others for removal
        for sig, keys in duplicates.items():
            # First key is canonical (will be kept)
            canonical = keys[0]
            
            # All other keys are duplicates (will be removed)
            for dup_key in keys[1:]:
                # Record that dup_key should be replaced with canonical key
                dup_mapping[dup_key] = canonical
                
                # Find and mark for removal all entries with this duplicate key
                for idx, (key, etype, entry_text) in enumerate(entries):
                    if key == dup_key:
                        indices_to_remove.add(idx)
        
        print(f"Removing {len(indices_to_remove)} duplicate entries\n")
    else:
        print("No duplicates found\n")
    
    # Filter out duplicate entries by index
    unique_entries = [
        (key, etype, entry_text)
        for idx, (key, etype, entry_text) in enumerate(entries)
        if idx not in indices_to_remove
    ]
    
    # ========== STEP 2: RENAME ENTRIES TO STANDARD FORMAT ==========
    
    print(f"Renaming {len(unique_entries)} entries to standard format...\n")
    
    # Mapping from old keys to new keys (for updating .tex files later)
    key_mapping = {}
    
    # Track how many keys with same base we've generated (for uniqueness)
    base_counts = defaultdict(int)
    
    new_entries = []
    
    for old_key, etype, entry_text in unique_entries:
        # Extract metadata for key generation
        author = extract_field(entry_text, 'author') or extract_field(entry_text, 'editor')
        year = extract_field(entry_text, 'year')
        title = extract_field(entry_text, 'title')
        url = extract_field(entry_text, 'url') or extract_field(entry_text, 'howpublished')
        
        # Generate new key based on entry type
        if not author and url:
            # Web source without author: use domain + title format
            base_key = make_key_from_url(url, title)
        else:
            # Standard format: authorYEARword
            last = first_author_lastname(author)
            word = short_title_word(title)
            y = year if year else 'noyear'
            base_key = make_key(last, y, word)
        
        # Ensure uniqueness by appending numeric suffix if needed
        new_key = base_key
        if base_counts[base_key] > 0:
            # If we've already used this base, add a numeric suffix
            new_key = f"{base_key}{base_counts[base_key]}"
        
        base_counts[base_key] += 1
        
        # Record the mapping for .tex file updates
        key_mapping[old_key] = new_key
        
        # Replace the key in the BibTeX entry header
        # Pattern: @Type{oldkey, -> @Type{newkey,
        old_pattern = r'@' + re.escape(etype) + r'\s*\{\s*' + re.escape(old_key) + r'\s*,'
        new_entry = re.sub(
            old_pattern,
            f'@{etype}{{{new_key},',
            entry_text,
            count=1,
            flags=re.IGNORECASE
        )
        
        new_entries.append(new_entry)
    
    # Apply duplicate mapping to key_mapping:
    # If old_key was mapped to canonical during dedup, and canonical is now renamed,
    # then old_key should ultimately map to the renamed canonical
    for dup_key, canonical in dup_mapping.items():
        if canonical in key_mapping:
            key_mapping[dup_key] = key_mapping[canonical]
    
    # ========== STEP 3: UPDATE .TEX FILES ==========
    
    # Find all .tex files in the project
    tex_files = []
    
    for root, dirs, files in os.walk(BASE_DIR):
        # Skip .git directories
        if '.git' in dirs:
            dirs.remove('.git')
        
        for fn in files:
            if fn.endswith('.tex'):
                tex_files.append(os.path.join(root, fn))
    
    print(f"Updating {len(tex_files)} .tex files...\n")
    
    # Pattern to match citation commands with their arguments
    # Matches: \cite{key} or \cite[p. 5]{key} or \citep[see]{key} etc.
    # FIXED: Now handles optional arguments correctly
    cite_pattern = re.compile(
        r'(\\(?:cite|citet|citep|citealt|citealp|citeauthor|citeyear|citeyearpar|'
        r'Cite|Citet|Citep|Citealt|Citealp|Citeauthor|Citeyear|Citeyearpar|'
        r'nocite|nocite\*)'
        r'(?:\*)?'  # Optional * for starred variants
        r'(?:\s*\[[^\]]*\])*'  # Optional arguments: [p. 5], [see][chap. 2], etc.
        r')\s*\{([^}]+)\}'  # Required argument with keys
    )
    
    def replace_keys_in_citation(match):
        """
        Replace citation keys within a citation command.
        
        Handles comma-separated key lists: \cite{key1, key2, key3}
        """
        prefix = match.group(1)  # The \cite command and optional args
        keys_str = match.group(2)  # Comma-separated keys
        
        # Split into individual keys and strip whitespace
        keys = [k.strip() for k in keys_str.split(',')]
        
        # Replace each key if it's in the mapping
        new_keys = [key_mapping.get(k, k) for k in keys]
        
        # Reconstruct: \cite{key1, key2}
        return f"{prefix}{{{', '.join(new_keys)}}}"
    
    # Track how many files were modified
    modified_files = 0
    replaced_citations = 0
    
    for tex_file in tex_files:
        try:
            txt = read_file(tex_file)
            original_txt = txt
            
            # Replace all citation keys in this file
            txt, count = cite_pattern.subn(replace_keys_in_citation, txt)
            
            if txt != original_txt:
                modified_files += 1
                replaced_citations += count
                
                if not dry_run:
                    write_file(tex_file, txt)
        
        except IOError as e:
            print(f"WARNING: Could not update {tex_file}: {e}", file=sys.stderr)
    
    # ========== WRITE NEW BIB FILE ==========
    
    # Join entries with double newlines (standard BibTeX formatting)
    new_bib = '\n\n'.join(new_entries) + '\n'
    
    if not dry_run:
        try:
            write_file(BIB_PATH, new_bib)
        except IOError as e:
            print(f"ERROR: Failed to write {BIB_PATH}: {e}", file=sys.stderr)
            sys.exit(1)
    
    # ========== PRINT SUMMARY ==========
    
    print('=' * 70)
    print('SUMMARY')
    print('=' * 70)
    
    if dry_run:
        print('[DRY RUN - No files were modified]')
        print()
    
    print(f"Removed {len(indices_to_remove)} duplicate entries")
    print(f"Renamed {len(unique_entries)} entries to standard format")
    print(f"Updated {modified_files} .tex files")
    print(f"Updated {replaced_citations} citation references")
    
    # Show key mappings (only for keys that actually changed)
    changed_keys = {k: v for k, v in key_mapping.items() if k != v}
    
    if changed_keys:
        print(f"\nKey mappings ({len(changed_keys)} changed):")
        
        # Group by old key for readability
        for old, new in sorted(changed_keys.items()):
            if old in dup_mapping:
                # This was a duplicate - show it was deduplicated
                print(f"  {old} → {new}  [DUPLICATE REMOVED]")
            else:
                # This was renamed
                print(f"  {old} → {new}")
    
    print()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Parse command-line arguments and execute requested operations."""
    
    parser = argparse.ArgumentParser(
        description='Bibliography management tool for merging papers into thesis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  %(prog)s --spot                      Find duplicate entries and wrong key names
  %(prog)s --fix                       Fix everything (remove duplicates + rename)
  %(prog)s --fix --dry-run             Preview changes without modifying files
  %(prog)s --spot --dir /path/to/thesis
  %(prog)s --fix --dir /path/to/thesis --bib custom.bib
        """
    )
    
    # Mutually exclusive: --spot or --fix (required)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--spot', '--find',
        action='store_true',
        dest='spot',
        help='Analyze: find duplicate entries and wrong key names (read-only)'
    )
    group.add_argument(
        '--fix',
        action='store_true',
        help='Fix: remove duplicates and rename all keys to standard format'
    )
    
    # Optional arguments
    parser.add_argument(
        '-d', '--dir',
        dest='dir',
        default='.',
        help='Project root directory containing refs.bib and .tex files (default: current directory)'
    )
    parser.add_argument(
        '--bib',
        dest='bib',
        default=None,
        help='Path to specific .bib file (overrides --dir refs.bib)'
    )
    parser.add_argument(
        '--dry-run',
        dest='dry_run',
        action='store_true',
        help='For --fix: preview changes without modifying files'
    )
    
    args = parser.parse_args()
    
    # ========== CONFIGURE PATHS ==========
    
    global BIB_PATH, BACKUP_PATH, BASE_DIR
    
    # Determine base directory and bib file path
    if args.bib:
        # User provided specific .bib file
        bib_path = os.path.abspath(os.path.expanduser(args.bib))
        
        if not os.path.isfile(bib_path):
            print(f"ERROR: Bib file '{bib_path}' does not exist", file=sys.stderr)
            sys.exit(2)
        
        BIB_PATH = bib_path
        BACKUP_PATH = BIB_PATH + '.bak'
        
        # Base directory is parent of bib file, or user-provided --dir
        if args.dir and args.dir != '.':
            base_dir = os.path.abspath(os.path.expanduser(args.dir))
            if not os.path.isdir(base_dir):
                print(f"ERROR: Directory '{base_dir}' does not exist", file=sys.stderr)
                sys.exit(2)
            BASE_DIR = base_dir
        else:
            # Default: parent directory of bib file
            BASE_DIR = os.path.dirname(BIB_PATH) or os.getcwd()
    
    else:
        # User provided --dir (or using current directory)
        root_dir = os.path.abspath(os.path.expanduser(args.dir))
        
        if not os.path.isdir(root_dir):
            print(f"ERROR: Directory '{root_dir}' does not exist", file=sys.stderr)
            sys.exit(2)
        
        BASE_DIR = root_dir
        BIB_PATH = os.path.join(BASE_DIR, 'refs.bib')
        BACKUP_PATH = BIB_PATH + '.bak'
    
    print(f"Working directory: {BASE_DIR}")
    print(f"BibTeX file: {BIB_PATH}\n")
    
    # ========== EXECUTE REQUESTED COMMAND ==========
    
    try:
        if args.spot:
            spot_duplicates()
        elif args.fix:
            fix_all(dry_run=args.dry_run)
    
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
