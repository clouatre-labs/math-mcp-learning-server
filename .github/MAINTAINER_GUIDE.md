# Maintainer Guide

This guide is for project maintainers responsible for releases, PyPI publishing, and infrastructure decisions.

## Release Process

We use [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`

- **Major:** Breaking changes
- **Minor:** New features (backward compatible)
- **Patch:** Bug fixes

### Create a Release

The project uses **GPG-signed annotated tags** with **PyPI Trusted Publishing** for secure, automated releases without API tokens.

#### Step 1: Update Version and Prepare

```bash
# Update version in pyproject.toml
# Update CHANGELOG.md or release notes
# Ensure uv.lock is up to date
uv lock --upgrade

# Verify all tests pass
uv run pytest -v
```

#### Step 2: Create GPG-Signed Annotated Tag

```bash
# Create an annotated, GPG-signed tag
git tag -s v1.2.0 -m "Release v1.2.0 - Add matrix operations"

# Verify the tag is signed
git tag -v v1.2.0

# Push the tag to trigger the release workflow
git push origin v1.2.0
```

**Important:** Only annotated, GPG-signed tags are accepted. Lightweight tags will be rejected by the release workflow.

#### Step 3: Automated Workflow

Once the tag is pushed, GitHub Actions automatically:

1. Verifies the tag is annotated and GPG-signed
2. Validates tag version matches `pyproject.toml`
3. Creates a GitHub release
4. Builds wheel and sdist packages with SLSA provenance attestation
5. Publishes to PyPI using Trusted Publishing with Sigstore attestations
6. Syncs version to MCP Registry

#### Step 4: Verify Release

Monitor progress at: <https://github.com/clouatre-labs/math-mcp-learning-server/actions>

Verify installation:

```bash
uvx math-mcp-learning-server@1.2.0
```

### Dry-Run Release

To test the release workflow without publishing:

```bash
# Trigger workflow_dispatch with dry_run=true
gh workflow run release.yml -f version=1.2.0 -f dry_run=true
```

This will:

- Skip GitHub release creation
- Skip PyPI publishing
- Skip MCP Registry sync
- Still build and attest packages (for validation)

### Manual Publishing (Emergency Only)

If automated publishing fails:

```bash
# Build package
uv build

# Publish with API token
uv publish --token $PYPI_API_TOKEN
```

Note: Trusted Publishing is strongly preferred for security.

## PyPI Trusted Publishing Setup

For new maintainers, PyPI Trusted Publishing must be configured once:

1. See [PyPI Trusted Publishing Configuration](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/.github/PYPI_TRUSTED_PUBLISHING.md)
2. Configure at: <https://pypi.org/manage/project/math-mcp-learning-server/settings/publishing/>
3. Add GitHub Actions as trusted publisher

### Troubleshooting Releases

**Tag Verification Fails:**

- Ensure tag is annotated (not lightweight): `git tag -v v1.2.0`
- Ensure tag is GPG-signed: `git tag -v v1.2.0` should show signature
- Recreate tag if needed: `git tag -d v1.2.0 && git tag -s v1.2.0 -m "Release v1.2.0"`
- Push updated tag: `git push origin v1.2.0 --force`

**Version Mismatch:**

- Ensure `pyproject.toml` version matches tag: `grep '^version = ' pyproject.toml`
- Tag should be `v<version>` (e.g., `v1.2.0` for version `1.2.0`)
- Update `pyproject.toml` and recreate tag if needed

**Tests Fail:**

- Fix issues locally and push to main
- Create new release tag after fixes

**Build Fails:**

- Check GitHub Actions logs at: <https://github.com/clouatre-labs/math-mcp-learning-server/actions>
- Verify `pyproject.toml` is valid
- Ensure `uv.lock` is up to date

**Publish Fails:**

- Verify PyPI Trusted Publisher is configured correctly
- Check [release.yml](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/.github/workflows/release.yml) has `id-token: write`
- Ensure environment `pypi` exists in GitHub settings

For detailed help, see [PyPI Trusted Publishing Configuration](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/.github/PYPI_TRUSTED_PUBLISHING.md).

## HTTP Integration Tests

HTTP integration tests run **only on release tags** (conditional on `startsWith(github.ref, 'refs/tags/')`).

These tests validate the server's HTTP interface in realistic deployment scenarios. They're excluded from normal CI to keep feedback loops fast.

To test locally before release:

```bash
uv run pytest tests/test_http_integration.py -v
```

## Infrastructure & Configuration

### GitHub Settings

Required for Trusted Publishing:

- Environment `pypi` must exist
- Trusted Publisher configured at PyPI
- Workflow has `permissions: id-token: write`

### PyPI Configuration

- Project: <https://pypi.org/project/math-mcp-learning-server/>
- Trusted Publisher: GitHub Actions (clouatre-labs/math-mcp-learning-server)
- Workflow filename in Trusted Publisher config must match: `release.yml`
- Environment name in Trusted Publisher config must match: `pypi`

### Workflow Files

- `.github/workflows/ci.yml` - Runs tests, linting, type checking on every push/PR
- `.github/workflows/release.yml` - Publishes to PyPI on GPG-signed tag push or workflow_dispatch

## Maintenance Tasks

### Before Release

1. Verify all tests pass: `uv run pytest -v`
2. Update version in `pyproject.toml`
3. Update `CHANGELOG.md` or release notes
4. Ensure `uv.lock` is up to date: `uv lock --upgrade`
5. Review git log since last release: `git log --oneline v0.x.0..HEAD`

### After Release

1. Verify PyPI page updated: <https://pypi.org/project/math-mcp-learning-server/>
2. Test installation from PyPI
3. Close any related GitHub issues
4. Announce release (if applicable)

## Contributing Guidelines for Maintainers

See [CONTRIBUTING.md](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/CONTRIBUTING.md) for contributor-facing guidelines.

Key points for maintainers:

- All PRs require passing automated checks
- Enforce conventional commits in PR titles
- Review code for security and educational value
- Ensure test coverage remains above 90%
- Document breaking changes clearly

## Merge Queue

Disabled (PR #130). Unnecessary overhead for a small project. To re-enable, see PR #71 for the original implementation.

---

For questions, open an issue or contact the project maintainers.
