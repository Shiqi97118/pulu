# PULU workspace rules

Read README.md, CONTINUE.md and docs/milestones/m01/01_DECISIONS_AND_QUESTIONS.md before changes.

- Treat the milestone documents as historical design requirements; use root CONTINUE for actual progress.
- Electron is a candidate under feasibility testing. Procedural meshes are placeholders, not approved character assets.
- No private reference photographs, credentials, user desktop content, raw pointer histories or telemetry in Git.
- Preserve an independent hide/quit path. Never use the overlay to block underlying desktop operations.
- Keep contextIsolation and sandbox enabled, Node disabled in renderer, local-only resources and a narrow validated IPC API.
- No cloud AI, payments, autostart or data uploads by default.
- Run npm run check for code changes; desktop interaction claims require actual recorded desktop checks.
- Record NOT_RUN/BLOCKED honestly. Do not lower milestone acceptance gates without an explicit decision record.

## User authorization update · 2026-11-16

The user explicitly authorized public upload of the three cat JPEGs in docs/milestones/m01/references. This overrides the earlier restriction for those three files only. Do not publish additional private materials.
