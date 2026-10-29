#!/usr/bin/env python3
"""Compatibility entrypoint for historical taxa ZIP imports.

The old implementation wrote into Hays-County-Botany/content/taxa and rebuilt
the public website manifest; that was retired by the user-approved family-only
write system on 2026-10-28. Historical logic remains in Git history.

This now delegates to the non-destructive family destination installer.
No automatic push, new-photo download, or old-hub botanical write is possible.
See workflow/NEW_PLANT_WRITES_FAMILY_REPOS_ONLY_20261028.md.
"""
from family_repo_installer import main

if __name__ == "__main__":
    main()
