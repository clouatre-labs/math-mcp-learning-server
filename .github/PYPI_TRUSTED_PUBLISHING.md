# PyPI Trusted Publishing Configuration

This document explains how to configure PyPI Trusted Publishing for automatic package publishing via GitHub Actions.

## What is Trusted Publishing?

Trusted Publishing uses OpenID Connect (OIDC) to allow GitHub Actions to publish packages to PyPI without storing long-lived API tokens. Instead, PyPI cryptographically verifies the workflow's identity and issues short-lived tokens on-demand.

**Benefits:**
- No secrets to manage or rotate
- More secure than API tokens
- Automatic token expiration
- Audit trail through GitHub Actions logs

## One-Time Setup (Already Complete)

These steps have already been completed for this repository:

1. ✅ GitHub Actions workflow created (`.github/workflows/python-publish.yml`)
2. ✅ GitHub environment `pypi` created
3. ⚠️ **PyPI Trusted Publisher configuration** (requires manual setup - see below)

## Configure PyPI Trusted Publishing

**This step must be done manually via PyPI web interface by a package maintainer:**

### Step 1: Log into PyPI

Go to https://pypi.org and log in with your account.

### Step 2: Navigate to Publishing Settings

1. Go to your project page: https://pypi.org/project/math-mcp-learning-server/
2. Click "Manage" → "Publishing"
3. Scroll to "Trusted Publishers" section

### Step 3: Add GitHub Actions Publisher

Click "Add a new publisher" and fill in:

```
Publisher: GitHub
Repository owner: clouatre
Repository name: math-mcp-learning-server
Workflow name: python-publish.yml
Environment name: pypi
```

**Important:**
- Workflow name must exactly match: `python-publish.yml`
- Environment name must exactly match: `pypi`

### Step 4: Save

Click "Add" to save the configuration.

## How It Works

### On Each GitHub Release

1. **Release Created:** You run `gh release create v0.x.x`
2. **Tests Run:** GitHub Actions runs test suite
3. **Build Package:** If tests pass, builds wheel and sdist
4. **OIDC Authentication:**
   - Workflow requests OIDC token from GitHub
   - GitHub provides signed proof of identity
   - PyPI verifies signature against Trusted Publisher config
   - PyPI mints short-lived API token (~15 minutes)
5. **Publish:** Package uploaded to PyPI
6. **Token Expires:** Short-lived token becomes invalid

### Security Flow

```
GitHub Actions Workflow
  ↓ (requests OIDC token with audience "pypi")
GitHub Identity Provider
  ↓ (returns signed JWT proving workflow identity)
PyPI OIDC Endpoint
  ↓ (verifies JWT signature and Trusted Publisher config)
  ↓ (mints short-lived API token)
pypa/gh-action-pypi-publish
  ↓ (uploads package using short-lived token)
PyPI Package Index
```

## Troubleshooting

### "Publisher configuration not found"

**Cause:** PyPI Trusted Publisher not configured or misconfigured.

**Solution:**
1. Verify configuration at https://pypi.org/manage/project/math-mcp-learning-server/settings/publishing/
2. Check that workflow name and environment name exactly match
3. Ensure you have maintainer permissions on PyPI project

### "Token verification failed"

**Cause:** OIDC token signature invalid or expired.

**Solution:**
- Re-run the workflow
- Check GitHub Actions logs for detailed error
- Verify the workflow has `id-token: write` permission

### "Environment not found"

**Cause:** GitHub environment `pypi` not configured.

**Solution:**
- Verify environment exists: https://github.com/clouatre-labs/math-mcp-learning-server/settings/environments
- Check workflow references correct environment name

## References

- [PyPI Trusted Publishing Documentation](https://docs.pypi.org/trusted-publishers/)
- [GitHub OIDC Documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [pypa/gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish)

## Testing

To test the workflow without publishing to production PyPI:

1. Configure TestPyPI Trusted Publisher at https://test.pypi.org
2. Modify workflow to add `repository-url: https://test.pypi.org/legacy/`
3. Create a pre-release: `gh release create v0.x.x-rc1 --prerelease`

## Reverting to Manual Publishing

If you need to publish manually:

```bash
# Build package
uv build

# Publish with API token
uv publish --token YOUR_PYPI_TOKEN
```

However, Trusted Publishing is strongly recommended for security and automation.
