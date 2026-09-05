# ADR-007: JSON Files for Workspace Persistence

## Status

Accepted

## Context

The persistence tools (`tools/persistence.py`) store named workspaces (sets of user-defined
variables) across server restarts. Options considered:

- **SQLite**: relational queries, transactions, atomic writes. Overhead is unjustified: workspaces
  are small key-value stores with simple read/write access patterns. Adds a dependency and a
  binary file format that is not human-readable.
- **In-memory only**: no persistence across restarts. Unacceptable for a workspace feature.
- **Cloud storage (S3, etc.)**: introduces network I/O, credentials, and provider lock-in.
  Incompatible with the project's minimal-dependency philosophy.
- **JSON files under XDG_DATA_HOME**: human-readable, no dependencies beyond the standard
  library, portable across operating systems, trivially inspectable and debuggable.

## Decision

Store each workspace as a JSON file under `~/.local/share/math-mcp/workspaces/`. The path
follows the XDG Base Directory specification. One file per workspace; filename is the workspace
name (validated to alphanumeric + underscore/hyphen by `validate_variable_name()` in `eval.py`).

Access pattern: load on read, write on save. No caching layer; files are small and infrequent.

## Consequences

**Gained:**

- Zero dependencies beyond `pathlib` and `json` (standard library)
- Human-readable; workspaces can be inspected, edited, or backed up with standard tools
- XDG compliance; storage location is predictable and follows OS conventions
- No migration path needed for schema changes: JSON is self-describing

**Accepted:**

- No atomic writes; a crash mid-write can corrupt a workspace file. Acceptable for an
  educational tool where data loss is recoverable by the user.
- No querying across workspaces; listing requires reading all files. Acceptable given
  the expected number of workspaces is small.
- Concurrent writes from multiple server instances are not safe. FastMCP Cloud runs one
  instance per invocation; this is not a practical concern.
