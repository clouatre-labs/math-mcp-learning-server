# Recording the Demo

The demo GIF at the top of the README is generated with [VHS](https://github.com/charmbracelet/vhs), a terminal recording tool that produces reproducible GIFs from a plain-text `.tape` script. The output is committed to `assets/demo.gif` and served via GitHub's raw CDN.

## Prerequisites

```bash
# macOS
brew install vhs

# Linux (requires ttyd and ffmpeg)
brew install vhs   # via Linuxbrew, or see VHS releases for apt/snap packages
```

VHS requires `ttyd` and `ffmpeg`; Homebrew installs both automatically.

## Tape file

The tape script lives at `assets/demo.tape`. To regenerate the GIF:

```bash
cd assets
vhs demo.tape
```

This writes `demo.gif` to the current directory.

## demo.tape

```tape
# math-mcp-learning-server demo
# Renders to: assets/demo.gif

Output demo.gif
Set FontSize 14
Set Width 1000
Set Height 600
Set Theme "Catppuccin Mocha"

# Start the server in stdio mode and show a session via the MCP inspector
Type "uvx 'math-mcp-learning-server[scientific,plotting]'"
Sleep 500ms
Enter
Sleep 3s

# Show a calculation
Type "calc_expression: 2 * pi * 6371"
Sleep 300ms
Enter
Sleep 1500ms

# Show statistics
Type "calc_statistics: [23, 45, 67, 12, 89, 34, 56]"
Sleep 300ms
Enter
Sleep 1500ms

# Save to workspace
Type "workspace_save: circumference=40030"
Sleep 300ms
Enter
Sleep 1500ms

Screenshot
Sleep 2s
```

> Tip: use `fastmcp dev math_mcp/server.py` to get an interactive browser-based inspector instead of raw stdio for a more visual demo.

## Updating the GIF

After editing `demo.tape`, run `vhs demo.tape` and commit both files together:

```bash
vhs assets/demo.tape
git add assets/demo.tape assets/demo.gif
git commit -S --signoff -m "docs: update demo gif"
```

Keep the tape script under version control so the GIF is always reproducible.
