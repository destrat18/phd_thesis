#!/usr/bin/env python3
import re
import os
import sys
import unicodedata
import argparse
from collections import defaultdict

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
    """Report duplicate bibliography entries."""
    if not os.path.exists(BIB_PATH):
        print('refs.bib not found', file=sys.stderr)
        sys.exit(1)
    
    bibtext = read_file(BIB_PATH)
    duplicates, entries = find_duplicates(bibtext)
    
    if not duplicates:
        print("No duplicates found!")
        return
    
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


def fix_duplicates():
    """Remove duplicate entries by keeping the first occurrence of each."""
    if not os.path.exists(BIB_PATH):
        print('refs.bib not found', file=sys.stderr)
        sys.exit(1)
    
    bibtext = read_file(BIB_PATH)
    duplicates, entries = find_duplicates(bibtext)
    
    if not duplicates:
        print("No duplicates found to fix!")
        return
    
    # Backup
    write_file(BACKUP_PATH, bibtext)
    print(f"Created backup at {BACKUP_PATH}")
    
    # Build mapping from duplicate keys to the canonical key (first one)
    dup_mapping = {}
    keys_to_remove = set()
    
    for sig, keys in duplicates.items():
        canonical = keys[0]  # Keep the first one
        for dup_key in keys[1:]:
            dup_mapping[dup_key] = canonical
            keys_to_remove.add(dup_key)
    
    # Filter out duplicate entries
    new_entries = []
    for key, etype, entry_text in entries:
        if key not in keys_to_remove:
            new_entries.append(entry_text)
    
    # Write new bib file
    new_bib = '\n\n'.join(new_entries) + '\n'
    write_file(BIB_PATH, new_bib)
    
    # Update .tex files to use canonical keys
    tex_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        if '.git' in root.split(os.sep):
            continue
        for fn in files:
            if fn.endswith('.tex'):
                tex_files.append(os.path.join(root, fn))
    
    replaced_count = 0
    for tf in tex_files:
        txt = read_file(tf)
        original = txt
        for old, new in dup_mapping.items():
            # replace only whole-word occurrences
            txt = re.sub(r'(?<![\\\w])' + re.escape(old) + r'(?![\w])', new, txt)
        if txt != original:
            write_file(tf, txt)
            replaced_count += 1
    
    print(f"\nRemoved {len(keys_to_remove)} duplicate entries")
    print(f"Updated {replaced_count} .tex files with canonical keys")
    print("\nDuplicate key mappings:")
    for old, new in dup_mapping.items():
        print(f"  {old} -> {new}")


def rename_all_keys():
    """Original functionality: rename all bib keys to a standard format."""
    if not os.path.exists(BIB_PATH):
        print('refs.bib not found', file=sys.stderr)
        sys.exit(1)
    bibtext = read_file(BIB_PATH)
    # backup
    write_file(BACKUP_PATH, bibtext)
    entries = parse_entries(bibtext)
    mapping = {}
    counts = defaultdict(int)
    new_entries = []
    for old_key, etype, entry_text in entries:
        author = extract_field(entry_text, 'author') or extract_field(entry_text, 'editor')
        year = extract_field(entry_text, 'year')
        title = extract_field(entry_text, 'title')
        last = first_author_lastname(author)
        word = short_title_word(title)
        y = year if year else 'noyear'
        base = make_key(last, y, word)
        candidate = base
        # ensure uniqueness
        while candidate in counts:
            counts[base] += 1
            candidate = f"{base}{counts[base]}"
        counts[candidate] += 1
        mapping[old_key] = candidate
        # replace the key in the entry header
        new_entry = re.sub(r'@' + re.escape(etype) + r'\s*\{\s*' + re.escape(old_key) + r'\s*,',
                           f'@{etype}{{{candidate},', entry_text, count=1)
        new_entries.append((old_key, candidate, new_entry))

    # assemble new bib
    new_bib = '\n\n'.join(ne for (_,_,ne) in new_entries) + '\n'
    write_file(BIB_PATH, new_bib)

    # update .tex files
    tex_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        # skip .git and scripts folder
        if '.git' in root.split(os.sep):
            continue
        for fn in files:
            if fn.endswith('.tex'):
                tex_files.append(os.path.join(root, fn))
    replaced_count = 0
    for tf in tex_files:
        txt = read_file(tf)
        original = txt
        for old, new in mapping.items():
            # replace only whole-word occurrences
            txt = re.sub(r'(?<![\\\w])' + re.escape(old) + r'(?![\w])', new, txt)
        if txt != original:
            write_file(tf, txt)
            replaced_count += 1
    # print summary
    print('Processed', len(entries), 'bib entries')
    print('Wrote backup to', BACKUP_PATH)
    print('Wrote new refs.bib with', len(new_entries), 'entries')
    print('Updated', replaced_count, '.tex files')
    print('\nMapping:')
    for old, new in mapping.items():
        print(f'{old} -> {new}')


def main():
    parser = argparse.ArgumentParser(
        description='Bibliography management tool for refs.bib',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --spot          # Find duplicate entries
  %(prog)s --fix           # Remove duplicate entries
  %(prog)s --rename        # Rename all keys to standard format
  %(prog)s --spot --dir path/to/project    # specify project directory
        """
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--spot', action='store_true',
                      help='Spot duplicate bibliography entries')
    group.add_argument('--fix', action='store_true',
                      help='Fix duplicate entries by removing duplicates')
    group.add_argument('--rename', action='store_true',
                      help='Rename all bibliography keys to standard format')
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
        fix_duplicates()
    elif args.rename:
        rename_all_keys()

if __name__ == '__main__':
    main()
