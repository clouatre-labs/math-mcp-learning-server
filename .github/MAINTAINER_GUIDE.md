# Maintainer Guide

This guide is for project maintainers responsible for releases, PyPI publishing, and infrastructure decisions.

## Release Process

We use [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`

- **Major:** Breaking changes
- **Minor:** New features (backward compatible)
- **Patch:** Bug fixes

### Create a Release

The project uses **PyPI Trusted Publishing** for secure, automated releases without API tokens.

#### Step 1: Create GitHub Release

```bash
# For production releases
gh release create v1.2.0 \
  --title "v1.2.0 - Add matrix operations" \
  --notes-file RELEASE_NOTES_v1.2.0.md

# For pre-releases (testing)
gh release create v1.2.0-rc1 \
  --title "v1.2.0-rc1 - Release Candidate" \
  --prerelease
```

#### Step 2: Automated Workflow

Once the release is published, GitHub Actions automatically:

1. Runs the test suite (ensures code quality)
2. Builds the wheel and sdist packages
3. Publishes to PyPI using Trusted Publishing

#### Step 3: Verify Release

Monitor progress at: https://github.com/clouatre-labs/math-mcp-learning-server/actions

Verify installation:
```bash
uv pip install math-mcp-learning-server==1.2.0
```

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
2. Configure at: https://pypi.org/manage/project/math-mcp-learning-server/settings/publishing/
3. Add GitHub Actions as trusted publisher

### Troubleshooting Releases

**Tests Fail:**
- Fix issues locally and push to main
- Create new release tag

**Build Fails:**
- Check GitHub Actions logs
- Verify `pyproject.toml` is valid
- Ensure `uv.lock` is up to date

**Publish Fails:**
- Verify PyPI Trusted Publisher is configured correctly
- Check [python-publish.yml](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/.github/workflows/python-publish.yml) has `id-token: write`
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

- Project: https://pypi.org/project/math-mcp-learning-server/
- Trusted Publisher: GitHub Actions (clouatre-labs/math-mcp-learning-server)

### Workflow Files

- `.github/workflows/ci.yml` - Runs tests, linting, type checking on every push/PR
- `.github/workflows/python-publish.yml` - Publishes to PyPI on release tags

## Maintenance Tasks

### Before Release

1. Verify all tests pass: `uv run pytest -v`
2. Update version in `pyproject.toml`
3. Update `CHANGELOG.md` or release notes
4. Ensure `uv.lock` is up to date: `uv lock --upgrade`
5. Review git log since last release: `git log --oneline v0.x.0..HEAD`

### After Release

1. Verify PyPI page updated: https://pypi.org/project/math-mcp-learning-server/
2. Test installation from PyPI
3. Close any related GitHub issues
4. Announce release (if applicable)

## Contributing Guidelines for Maintainers

See [CONTRIBUTING.md](https://github.com/clouatre-labs/math-mcp-learning-server/blob/main/CONTRIBUTING.md) for contributor-facing guidelines.

Key points for maintainers:
- All PRs require passing automated checks
- Enforce conventional commits in PR titles
- Review code for security and educational value
- Ensure test coverage remains above 80%
- Document breaking changes clearly

---

For questions, open an issue or contact the project maintainers.
