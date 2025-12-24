#!/usr/bin/env python3
import re
import os
import sys
import unicodedata
import argparse
from collections import defaultdict
from urllib.parse import urlparse

BIB_PATH = 'refs.bib'
BACKUP_PATH = BIB_PATH + '.bak'
BASE_DIR = '.'

entry_re = re.compile(r'@(?P<type>\w+)\s*\{\s*(?P<key>[^,]+),')
field_re = re.compile(r'(?P<name>\w+)\s*=\s*(?P<value>\{(?:[^{}]|\{[^}]*\})*\}|\"[^\"]*\"|[^,\n]+)', re.IGNORECASE)

COMMON_STOPWORDS = {'the','and','of','for','on','in','a','an','to','with','by','via','using'}


def asciiify(s):
    if not s:
        return ''
    s = unicodedata.normalize('NFKD', s)
    s = s.encode('ascii', 'ignore').decode('ascii')
    return s


def first_author_lastname(author_field):
    if not author_field:
        return 'unknown'
    # split multiple authors by ' and ' (BibTeX standard)
    authors = [a.strip() for a in re.split(r'\s+and\s+', author_field)]
    first = authors[0]
    # If format 'Last, First'
    if ',' in first:
        last = first.split(',')[0].strip()
    else:
        parts = first.split()
        last = parts[-1] if parts else 'unknown'
    last = asciiify(last).lower()
    last = re.sub(r'[^a-z0-9]', '', last)
    return last or 'unknown'


def extract_field(entry_text, name):
    m = re.search(r'%s\s*=\s*(\{((?:[^{}]|\{[^}]*\})*)\}|\"([^\"]*)\"|([^,\n]+))' % re.escape(name), entry_text, re.IGNORECASE)
    if not m:
        return None
    # group 2 is inside braces, group 3 is inside quotes, group 4 is plain
    val = m.group(2) or m.group(3) or m.group(4)
    if val is None:
        return None
    return val.strip()


def short_title_word(title_field):
    if not title_field:
        return 'misc'
    # remove braces and LaTeX commands
    t = re.sub(r'\\[A-Za-z]+\*?(?:\[[^\]]*\])?(?:\{[^}]*\})?', '', title_field)
    t = re.sub(r'[{}"]', '', t)
    t = asciiify(t).lower()
    words = re.findall(r"[a-z0-9]+", t)
    for w in words:
        if w not in COMMON_STOPWORDS:
            return w
    return words[0] if words else 'misc'


def make_key(last, year, word):
    y = year if year else 'noyear'
    return f"{last}{y}{word}"


def extract_domain_from_url(url):
    """Extract domain name from URL and convert to camelCase format."""
    if not url:
        return None
    # Remove LaTeX \url{} command if present
    url = re.sub(r'\\url\{([^}]*)\}', r'\1', url)
    url = url.strip()
    
    # Add scheme if missing for urlparse to work correctly
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Parse URL using urllib
    parsed = urlparse(url)
    domain = parsed.netloc
    
    if not domain:
        return None
    
    # Remove www. prefix
    if domain.startswith('www.'):
        domain = domain[4:]
    
    # Split by dots and convert to camelCase
    parts = domain.split('.')
    if len(parts) > 1:
        # e.g., "hashrateindex.com" -> "HashrateindexCom"
        result = ''.join(part.capitalize() for part in parts)
        return result
    return domain.capitalize()


def title_to_camel_case_words(title_field, min_words=3):
    """Convert title to camelCase using at least min_words words."""
    if not title_field:
        return ''
    # Remove braces and LaTeX commands
    t = re.sub(r'\\[A-Za-z]+\*?(?:\[[^\]]*\])?(?:\{[^}]*\})?', '', title_field)
    t = re.sub(r'[{}"]', '', t)
    t = asciiify(t)
    # Extract words
    words = re.findall(r"[A-Za-z0-9]+", t)
    # Take at least min_words, skip common stopwords if possible
    selected = []
    for w in words:
        if len(selected) >= min_words:
            break
        # For the camelCase format, include all significant words
        if w.lower() not in COMMON_STOPWORDS or len(selected) == 0:
            selected.append(w.capitalize())
    # If we don't have enough, just take the first min_words
    if len(selected) < min_words:
        selected = [w.capitalize() for w in words[:min_words]]
    return ''.join(selected)


def make_key_from_url(url, title):
    """Generate key for web sources: domainCamelCase + TitleWordsCamelCase."""
    domain = extract_domain_from_url(url)
    if not domain:
        domain = 'Web'
    title_part = title_to_camel_case_words(title, min_words=3)
    if not title_part:
        title_part = 'Page'
    # Ensure the key only contains alphanumeric characters
    key = f"{domain}{title_part}"
    # Remove any remaining invalid characters (backslashes, colons, etc.)
    key = re.sub(r'[^a-zA-Z0-9]', '', key)
    return key


def read_file(path):
    # Try utf-8 first, fall back to latin-1 for files with special bytes
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(path, 'r', encoding='latin-1') as f:
            return f.read()


def write_file(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)


def parse_entries(bibtext):
    entries = []
    # find all entry starts
    matches = list(entry_re.finditer(bibtext))
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(bibtext)
        entry_text = bibtext[start:end].rstrip('\n')
        etype = m.group('type')
        key = m.group('key').strip()
        entries.append((key, etype, entry_text))
    return entries


def parse_entries(bibtext):
    entries = []
    # find all entry starts
    matches = list(entry_re.finditer(bibtext))
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(bibtext)
        entry_text = bibtext[start:end].rstrip('\n')
        etype = m.group('type')
        key = m.group('key').strip()
        entries.append((key, etype, entry_text))
    return entries


def find_duplicates(bibtext):
    """Find duplicate bib entries by normalizing key content."""
    entries = parse_entries(bibtext)
    # Map from normalized signature -> list of keys
    signature_map = defaultdict(list)
    
    for key, etype, entry_text in entries:
        author = extract_field(entry_text, 'author') or extract_field(entry_text, 'editor')
        year = extract_field(entry_text, 'year')
        title = extract_field(entry_text, 'title')
        
        # Create a normalized signature
        author_norm = asciiify(author or '').lower() if author else ''
        title_norm = asciiify(title or '').lower() if title else ''
        year_norm = year or ''
        
        signature = (author_norm, year_norm, title_norm)
        signature_map[signature].append(key)
    
    # Find duplicates
    duplicates = {sig: keys for sig, keys in signature_map.items() if len(keys) > 1}
    return duplicates, entries


def spot_duplicates():
    r"""Report duplicate bibliography entries and keys not matching desired format.

    Desired format: `lastnameYYYYshortword` (e.g. albert2009termination).
    Keys that don't match the base pattern `base(\d+)?` are reported as "wrong name".
    """
    if not os.path.exists(BIB_PATH):
        print('refs.bib not found', file=sys.stderr)
        sys.exit(1)

    bibtext = read_file(BIB_PATH)
    duplicates, entries = find_duplicates(bibtext)

    # Report duplicates
    if duplicates:
        print(f"Found {len(duplicates)} groups of duplicate entries:\n")
        for i, (sig, keys) in enumerate(duplicates.items(), 1):
            author_norm, year_norm, title_norm = sig
            print(f"Group {i}:")
            print(f"  Keys: {', '.join(keys)}")
            if author_norm:
                print(f"  Author: {author_norm}")
            if year_norm:
                print(f"  Year: {year_norm}")
            if title_norm:
                print(f"  Title: {title_norm[:80]}..." if len(title_norm) > 80 else f"  Title: {title_norm}")
            print()
    else:
        print("No duplicates found!")

    # Check key naming
    wrong_names = {}
    pattern_ok_cache = {}
    for key, etype, entry_text in entries:
        author = extract_field(entry_text, 'author') or extract_field(entry_text, 'editor')
        year = extract_field(entry_text, 'year') or ''
        title = extract_field(entry_text, 'title') or ''
        last = first_author_lastname(author)
        word = short_title_word(title)
        base = make_key(last, year, word)

        # Accept either exact base or base plus numeric suffix (base, base1, base2...)
        # Cache compiled regex for performance
        if base not in pattern_ok_cache:
            pattern_ok_cache[base] = re.compile(r'^' + re.escape(base) + r'(?:\d+)?$')
        if not pattern_ok_cache[base].match(key):
            wrong_names[key] = base

    if wrong_names:
        print(f"\nFound {len(wrong_names)} keys with unexpected names:\n")
        for old, base in sorted(wrong_names.items(), key=lambda x: x[0]):
            print(f"  {old}  -> suggested base: {base}")
    else:
        print("All keys conform to the desired naming base pattern.")


def fix_all():
    """Comprehensive fix: remove duplicates and rename all keys to standard format."""
    if not os.path.exists(BIB_PATH):
        print('refs.bib not found', file=sys.stderr)
        sys.exit(1)
    
    bibtext = read_file(BIB_PATH)
    write_file(BACKUP_PATH, bibtext)
    print(f"Created backup at {BACKUP_PATH}")
    
    # Step 1: Find and remove duplicates
    duplicates, entries = find_duplicates(bibtext)
    dup_mapping = {}
    indices_to_remove = set()
    
    if duplicates:
        print(f"\nFound {len(duplicates)} groups of duplicate entries")
        # Build a map from key to list of indices where it appears
        key_to_indices = defaultdict(list)
        for idx, (key, etype, entry_text) in enumerate(entries):
            key_to_indices[key].append(idx)
        
        for sig, keys in duplicates.items():
            canonical = keys[0]
            # For duplicate keys, mark all but the first occurrence for removal
            for dup_key in keys[1:]:
                dup_mapping[dup_key] = canonical
                # If this is a key that appears multiple times, only remove later occurrences
                if dup_key in key_to_indices:
                    for idx in key_to_indices[dup_key][1:]:  # Skip first occurrence
                        indices_to_remove.add(idx)
                    # If the dup_key is different from canonical, remove its first occurrence too
                    if dup_key != canonical:
                        indices_to_remove.add(key_to_indices[dup_key][0])
        
        print(f"Removing {len(indices_to_remove)} duplicate entries")
    else:
        print("\nNo duplicates found")
    
    # Filter out duplicates by index
    unique_entries = [(key, etype, entry_text) for idx, (key, etype, entry_text) in enumerate(entries) 
                      if idx not in indices_to_remove]
    
    # Step 2: Rename all keys to standard format
    print(f"\nRenaming {len(unique_entries)} entries to standard format...")
    mapping = {}
    counts = defaultdict(int)
    new_entries = []
    
    for old_key, etype, entry_text in unique_entries:
        author = extract_field(entry_text, 'author') or extract_field(entry_text, 'editor')
        year = extract_field(entry_text, 'year')
        title = extract_field(entry_text, 'title')
        url = extract_field(entry_text, 'url') or extract_field(entry_text, 'howpublished')
        
        # For web sources without author, use domain + title format
        if not author and url:
            base = make_key_from_url(url, title)
        else:
            last = first_author_lastname(author)
            word = short_title_word(title)
            y = year if year else 'noyear'
            base = make_key(last, y, word)
        candidate = base
        
        # Ensure uniqueness
        while candidate in counts:
            counts[base] += 1
            candidate = f"{base}{counts[base]}"
        counts[candidate] += 1
        mapping[old_key] = candidate
        
        # Replace the key in the entry header
        # Escape backslashes in candidate to avoid re.sub interpretation issues
        escaped_candidate = candidate.replace('\\', '\\\\')
        new_entry = re.sub(r'@' + re.escape(etype) + r'\s*\{\s*' + re.escape(old_key) + r'\s*,',
                           f'@{etype}{{{escaped_candidate},', entry_text, count=1)
        new_entries.append(new_entry)
    
    # Merge duplicate mappings with rename mappings
    # If a key was duplicated, map it through: dup -> canonical -> new_name
    for dup_key, canonical in dup_mapping.items():
        if canonical in mapping:
            mapping[dup_key] = mapping[canonical]
    
    # Write new bib file
    new_bib = '\n\n'.join(new_entries) + '\n'
    write_file(BIB_PATH, new_bib)
    
    # Step 3: Update all .tex files
    tex_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        if '.git' in root.split(os.sep):
            continue
        for fn in files:
            if fn.endswith('.tex'):
                tex_files.append(os.path.join(root, fn))
    
    print(f"\nUpdating {len(tex_files)} .tex files...")
    replaced_count = 0
    
    # Pattern to match LaTeX citation commands
    cite_pattern = re.compile(
        r'(\\(?:cite|citet|citep|citealt|citealp|citeauthor|citeyear|citeyearpar|Cite|Citet|Citep)'
        r'(?:\*)?(?:\[[^\]]*\])*)\{([^}]+)\}'
    )
    
    def replace_keys_in_citation(match):
        """Replace citation keys within a single citation command."""
        prefix = match.group(1)  # The \cite command part
        keys_str = match.group(2)  # The comma-separated keys
        keys = [k.strip() for k in keys_str.split(',')]
        # Replace each key if it's in the mapping
        new_keys = [mapping.get(k, k) for k in keys]
        return f"{prefix}{{{', '.join(new_keys)}}}"
    
    for tf in tex_files:
        txt = read_file(tf)
        original = txt
        # Replace keys only within citation commands
        txt = cite_pattern.sub(replace_keys_in_citation, txt)
        if txt != original:
            write_file(tf, txt)
            replaced_count += 1
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Removed {len(indices_to_remove)} duplicate entries")
    print(f"Renamed {len(unique_entries)} entries to standard format")
    print(f"Updated {replaced_count} .tex files")
    if mapping:
        changed_keys = {k: v for k, v in mapping.items() if k != v}
        if changed_keys:
            print(f"\nKey mappings ({len(changed_keys)} changed):")
            for old, new in sorted(changed_keys.items()):
                print(f"  {old} -> {new}")


def main():
    parser = argparse.ArgumentParser(
        description='Bibliography management tool for merging papers into thesis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s --spot                        # Find problems (duplicates, wrong names)
    %(prog)s --fix                         # Fix everything (remove duplicates + rename all)
    %(prog)s --spot --dir /path/to/thesis  # Specify project directory
    %(prog)s --fix --dir /path/to/thesis   # Fix in specific directory
                """
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--spot', '--find', action='store_true', dest='spot',
                      help='Spot problems: find duplicate entries and wrong key names')
    group.add_argument('--fix', action='store_true',
                      help='Fix everything: remove duplicates and rename all keys to standard format')
    parser.add_argument('-d', '--dir', dest='dir', default='.',
                        help='Project root directory containing refs.bib and .tex files (default: .)')
    parser.add_argument('--bib', dest='bib', default=None,
                        help='Path to a .bib file to operate on (overrides --dir refs.bib)')
    
    args = parser.parse_args()
    # Resolve provided options and set globals
    global BIB_PATH, BACKUP_PATH, BASE_DIR
    # If a bib path is provided, prefer it. Expand ~ and make absolute.
    if args.bib:
        bib_path = os.path.abspath(os.path.expanduser(args.bib))
        if not os.path.isfile(bib_path):
            print(f"Provided bib file '{bib_path}' does not exist", file=sys.stderr)
            sys.exit(2)
        BIB_PATH = bib_path
        BACKUP_PATH = BIB_PATH + '.bak'
        # Determine base dir: either user-provided --dir or parent of bib
        if args.dir and args.dir != '.':
            base_dir = os.path.abspath(os.path.expanduser(args.dir))
            if not os.path.isdir(base_dir):
                print(f"Provided path '{base_dir}' is not a directory", file=sys.stderr)
                sys.exit(2)
            BASE_DIR = base_dir
        else:
            BASE_DIR = os.path.dirname(BIB_PATH) or os.getcwd()
    else:
        root_dir = os.path.abspath(os.path.expanduser(args.dir))
        if not os.path.isdir(root_dir):
            print(f"Provided path '{root_dir}' is not a directory", file=sys.stderr)
            sys.exit(2)
        BASE_DIR = root_dir
        BIB_PATH = os.path.join(BASE_DIR, 'refs.bib')
        BACKUP_PATH = BIB_PATH + '.bak'
    
    if args.spot:
        spot_duplicates()
    elif args.fix:
        fix_all()

if __name__ == '__main__':
    main()
