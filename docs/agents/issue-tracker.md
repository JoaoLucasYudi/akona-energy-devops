# Issue tracker: Linear

Issues and specs for this repo live in Linear, accessed through the `linear-server` MCP tools (`mcp__linear-server__*`; load them with ToolSearch if deferred).

- **Team**: `João Lucas Personal` (key `JOA`)
- **Project**: `gs-devops`

## Conventions

- **Create an issue**: `save_issue` without `id`, always with `team: "JOA"` and `project: "gs-devops"`. Check `list_issues` (project `gs-devops`, `query`) first to avoid duplicates.
- **Read an issue**: `get_issue` with the identifier (e.g. `JOA-5`); comments come from `list_comments`.
- **List issues**: `list_issues` with `project: "gs-devops"` and optional `label` / `state` filters. Follow `cursor` while `hasNextPage` is true.
- **Comment**: `save_comment` on the issue.
- **Apply / remove labels**: `save_issue` with `id` and `addLabels` / `removeLabels` (never `labels`, which replaces the whole set).
- **Close**: `save_issue` with `id` and `state: "Done"` (or `"Canceled"`), plus a comment explaining the outcome.
- **Blocking**: `save_issue` with `blockedBy` / `blocks` (append-only).
- **Sub-issues**: `save_issue` with `parentId`.
- **Link work**: branch names follow the repo convention (`epic/e<n>-<nome>`); put the Linear ID (e.g. `Refs JOA-5`) in the commit/PR body.
- Write issue text in Brazilian Portuguese. Put agent-only detail in a collapsible `+++ Agent notes` block at the end of the description.

## Pull requests as a triage surface

**PRs as a request surface: no.**

## When a skill says "publish to the issue tracker"

Create a Linear issue in team `JOA`, project `gs-devops`.

## When a skill says "fetch the relevant ticket"

Read it with `get_issue` and `list_comments`.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a single issue with **child** issues as tickets.

- **Map**: an issue labelled `wayfinder:map` (create the label if missing), holding the Notes / Decisions-so-far / Fog body.
- **Child ticket**: an issue with `parentId` set to the map. Labels: `wayfinder:<type>` (`research`/`prototype`/`grilling`/`task`). Once claimed, assigned to the driving dev (`assignee: "me"`).
- **Blocking**: Linear's native relations via `blockedBy`. A ticket is unblocked when every blocker is Done.
- **Frontier query**: `list_issues` with `parentId` = map, state not Done/Canceled; drop any with an open blocker or an assignee; first in map order wins.
- **Claim**: `save_issue` with `assignee: "me"`, the session's first write.
- **Resolve**: `save_comment` with the answer, set `state: "Done"`, then append a context pointer to the map's Decisions-so-far (use `patch`).
