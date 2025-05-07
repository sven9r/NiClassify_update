# Changelog

## [Unreleased] – 2025-05-07
### Changed
- Refactored `get_data()` in `core/utilities/general_utils.py` to improve file encoding compatibility.
  - Introduced conditional fallback from `utf-8` to `windows-1252` encoding for `.csv`, `.tsv`, and `.txt` files.
  - Reduced reliance on `engine="python"` in `pandas.read_csv()` unless necessary (e.g., when delimiter is unspecified or fallback required).
  - Improved delimiter detection for single-column fallback: now retries with tab separator (`\t`) if only one column is detected.
  - Removed deprecated or unnecessary `engine` parameters in favor of default pandas behavior for better performance and clarity.

### Fixed
- Resolved UnicodeDecodeErrors when reading malformed or mixed-encoding TSV/CSV files on macOS.
- Eliminated console crash when opening Windows-encoded files that include smart quotes or em dashes.
- Avoided silent misparsing of improperly delimited `.csv` files by introducing explicit fallback logic.

### Added
- User-friendly fallback strategy for corrupted or improperly formatted data files.
- Clarified error pathway when decoding or separator inference fails.

### Notes
- These changes improve cross-platform stability and make the GUI tools more tolerant of real-world BOLD and user-supplied data files.
- Manual editing of `engine` parameters in other scripts should be avoided unless explicitly needed; the updated parser now handles most edge cases automatically.