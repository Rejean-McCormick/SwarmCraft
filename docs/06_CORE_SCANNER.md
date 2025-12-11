# TextCraft Scanner Logic (`core/scanner.py`)

**Version:** 2.1.0 (Refactored for Specialized Services)
**Status:** Core Definition
**Role:** The Sensory Input System (The Eyes)

-----

## 1\. Overview

The **Scanner** (`core/scanner.py`) is the only component in TextCraft that directly interacts with the file system state of the manuscripts. Its primary job is to provide ground truth to the AI. It prevents hallucinations by ensuring the **Story Matrix** reflects the physical reality of the hard drive.

  * **Responsibility:** "See" the project.
  * **Input:** The `data/manuscripts/` directory tree.
  * **Output:** Updates the `content` and `meta` sections of `data/matrix.json`.
  * **Frequency:** Runs automatically at the start of every Orchestrator loop (Step 1: SCAN).

-----

## 2\. Core Logic

The Scanner executes a non-destructive read operation. It does not modify manuscript files; it only reports on them.

### Step 1: Directory Traversal

  * **Root:** `data/manuscripts/`
  * **Filter:** `*.md` files only.
  * **Normalization:** Converts file paths to relative keys (e.g., `data/manuscripts/ch01.md` becomes the key `ch01`).

### Step 2: Content Analysis (Heuristics)

For every file found, the Scanner performs a lightweight analysis:

1.  **Read Content:** Opens the file in UTF-8.
2.  **Count Words:** Splits content by whitespace to calculate `word_count`.
3.  **Check Freshness:** Reads the OS `st_mtime` to update `last_modified`.
4.  **Scan Markers:** Looks for specific string patterns (e.g., `[TODO]`, \`\`) to assist status determination.

### Step 3: Matrix Reconciliation

The Scanner merges physical data with existing Matrix data.

  * **New File:** If a file exists on disk but not in the Matrix, create a new entry with status `DRAFTING`.
  * **Missing File:** If a file is in the Matrix but not on disk, mark status as `MISSING` (or remove, based on config).
  * **Existing File:** Update `word_count` and `last_modified`. **Crucial:** Do *not* overwrite `status` if it is `LOCKED`, unless a discrepancy flag is set.

-----

## 3\. Status Determination Logic (The Heuristics)

The Scanner automatically infers the `status` of a chapter based on its content, *unless* the Orchestrator has explicitly overridden it.

| Condition | Inferred Status | Logic |
| :--- | :--- | :--- |
| `word_count` \< 50 | `EMPTY` | File is effectively blank or just a header. |
| `word_count` \> 50 AND `[TODO]` present | `DRAFTING` | Content exists but agent has left markers. |
| `word_count` \> `target_word_count` | `REVIEW_READY` | Meets the length constraints defined in `project_conf.json`. |
| No change since last scan | `STAGNANT` | (Optional) Flag for the Architect if a file hasn't moved in X cycles. |

*Note: The Scanner never sets a file to `LOCKED` or `PASS`. Only **The Editor Service** (via the Orchestrator) can grant those statuses.*

-----

## 4\. Variable Mapping

The Scanner maps physical file attributes to the JSON schema defined in `docs/01_SCHEMA_MATRIX.md`.

### Input: File System (`os.stat`, `open()`)

| Physical Attribute | Matrix Variable | Transformation |
| :--- | :--- | :--- |
| `os.path.basename` | `content.{id}.title` | Derived from filename (e.g., `ch01_The_Hook.md` $\rightarrow$ "The Hook"). |
| `len(text.split())` | `content.{id}.word_count` | Integer count. |
| `os.path.getmtime` | `content.{id}.last_modified` | Converted to ISO-8601 String. |
| `file.read()` | *Internal Analysis* | Used to detect `[TODO]` markers; content is **not** stored in Matrix. |

### Output: Matrix Updates (`data/matrix.json`)

| Matrix Section | Field | Update Rule |
| :--- | :--- | :--- |
| `meta` | `last_scan_timestamp` | Always updated to `datetime.now()` on successful completion. |
| `metrics` | `total_word_count` | Sum of all `content.*.word_count`. |
| `metrics` | `chapter_count` | Count of keys in `content`. |
| `content` | `{id}.path` | Absolute or relative path update (if file moved). |

-----

## 5\. Public Interface

```python
class ProjectScanner:
    def __init__(self, root_dir: str = "data/manuscripts"):
        self.root = Path(root_dir)
        self.matrix_path = Path("data/matrix.json")

    def scan(self) -> dict:
        """
        Main entry point.
        1. Reads matrix.json (if exists).
        2. Walks directory.
        3. Updates data.
        4. Writes matrix.json.
        5. Returns the updated dictionary.
        """
        pass

    def _calculate_status(self, current_status: str, content: str, word_count: int) -> str:
        """
        Applies heuristics to determine if status should change.
        Protect LOCKED status from being overwritten by simple scans.
        """
        pass
```

-----

## 6\. Implementation Notes

  * **Performance:** The Scanner processes text files. For very large projects (\>100k words), consider optimizing the `word_count` logic to avoid loading entire files into memory if not needed.
  * **Concurrency:** The Scanner is a synchronous operation. The Orchestrator waits for the Scan to complete before planning. This prevents "Brain/Body dissociation" where the AI thinks a file is empty when it has actually been written.
  * **Safety:** The Scanner should never delete a file from the disk. It only observes.