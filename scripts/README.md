# Bibliography Management Script

A tool for managing bibliography files when merging multiple papers into a PhD thesis.

## Features

- **Duplicate Detection**: Finds duplicate bibliography entries based on author, year, and title
- **Key Naming Validation**: Identifies keys that don't follow the standard format
- **Automatic Fixing**: Removes duplicates and renames all keys to standard format
- **Smart Updates**: Automatically updates all `.tex` files with new keys

## Usage

### Two Main Commands

#### 1. Spot Problems (Read-Only)
```bash
python3 scripts/rename_bibkeys.py --spot
```

This will:
- Find all duplicate entries
- Identify keys with non-standard names
- Suggest proper names for problematic keys
- **Does NOT modify any files**

#### 2. Fix Everything
```bash
python3 scripts/rename_bibkeys.py --fix
```

This will:
- Create a backup (`refs.bib.bak`)
- Remove all duplicate entries (keeps first occurrence)
- Rename all keys to standard format: `lastnameYYYYshortword`
- Update all `.tex` files recursively with new keys
- Show a summary of changes

### Options

- `--dir <path>`: Specify project directory (default: current directory)
  ```bash
  python3 scripts/rename_bibkeys.py --fix --dir /path/to/thesis
  ```

- `--bib <path>`: Use a specific `.bib` file instead of `refs.bib`
  ```bash
  python3 scripts/rename_bibkeys.py --spot --bib custom.bib
  ```

## Standard Key Format

Keys follow this pattern: `lastnameYYYYshortword`

**Examples:**
- `albert2009termination`
- `nakamoto2008bitcoin`
- `wood2014ethereum`

For multiple entries with the same base, numeric suffixes are added:
- `albert2009termination`
- `albert2009termination2`
- `albert2009termination3`

## Workflow for Merging Papers

1. **Before merging**: Run `--spot` on your thesis to see current state
2. **Add papers**: Copy bibliography entries from your papers into `refs.bib`
3. **Check for problems**: Run `--spot` to see duplicates and naming issues
4. **Fix everything**: Run `--fix` to clean up and standardize
5. **Verify**: Check the backup and summary output

## Example Session

```bash
# Check current state
python3 scripts/rename_bibkeys.py --spot

# Output shows duplicates and wrong names
# Found 81 groups of duplicate entries
# Found 31 keys with unexpected names

# Fix everything in one go
python3 scripts/rename_bibkeys.py --fix

# Output:
# Created backup at refs.bib.bak
# Found 81 groups of duplicate entries
# Removing 81 duplicate entries
# Renaming 42 entries to standard format...
# Updating 8 .tex files...
# SUMMARY:
# Removed 81 duplicate entries
# Renamed 42 entries to standard format
# Updated 8 .tex files
```

## Safety

- Always creates a backup before making changes
- Only modifies files when using `--fix` (not `--spot`)
- Uses word-boundary regex to avoid partial matches in `.tex` files
- Preserves first occurrence when removing duplicates
