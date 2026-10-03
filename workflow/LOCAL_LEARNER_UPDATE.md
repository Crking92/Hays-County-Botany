# One-click local learner update

Use **UPDATE_AND_RUN.bat** for normal day-to-day website checking.

It does four things:

1. Checks for tracked local edits that should not be overwritten.
2. If `research-queue.json` contains local approval decisions, saves a timestamped backup.
3. Pulls the latest `main` branch from GitHub and reapplies local approval decisions when the remote copy is not newer.
4. Starts `RUN_LOCAL_SERVER.bat`, which opens `http://localhost:8000/?fresh=1` with browser caching disabled.

## Normal workflow

After ChatGPT commits a website/learner change:

1. Close the existing local-server terminal.
2. Double-click `UPDATE_AND_RUN.bat`.
3. Wait for the browser to open.
4. Check the change in the learner.

There is normally no need to run `git pull`, `git stash`, or cache-clearing commands manually.

## Safety behavior

The updater only auto-handles `research-queue.json`, because the local approval dashboard intentionally writes there.

If any other tracked file has local changes, the updater stops and lists those files rather than overwriting them. Untracked personal working files are ignored by the update.

Queue backups are written under `local-backups/` and are ignored by Git.

If a local and remote approval both exist for the same item, the updater keeps the newer/equal remote decision; otherwise it reapplies the local decision.
