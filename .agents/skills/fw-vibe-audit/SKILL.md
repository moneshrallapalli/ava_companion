---
name: fw-vibe-audit
description: Run a Future Wonder Vibe Code Rescue audit across a repository and its live platform setup. Use when the user asks for a Vibe Code Rescue audit, repo-and-platform audit, product rescue audit, whole-project audit, audit matrix, suggested tickets, docs updates, or `/fw-vibe-audit`.
---

# FW Vibe Audit

Use this skill to run a repo-and-platform audit of an application's current
product state. This is a whole-project audit, not a branch diff review.

Use these rules when the user asks for `/fw-vibe-audit`, a Vibe Code Rescue
audit, a whole-project audit, a repo-and-platform audit, a product rescue
audit, an audit matrix, or an audit that should produce suggested tickets or
docs.

## Purpose

The audit must:

- Inspect the current repository and available live platform evidence.
- Build a Current Platform Snapshot.
- Identify risks, gaps, strengths, and open questions.
- Suggest tickets, wiki or docs updates, and backlog order.
- Stop for human approval before publishing or changing anything.

## Start

Default to a low-friction setup. When the user only types
`/fw-vibe-audit`, infer what you can, choose safe defaults, and proceed to
setup confirmation instead of asking preference questions.

Use these defaults unless the user says otherwise:

1. **Repository path**: current workspace or current directory.
2. **Audit type**: repo-first Vibe Code Rescue audit.
3. **Output target**: markdown in chat.
4. **Publishing mode**: draft only until human approval.
5. **Pass structure**: one discovery pass and one findings pass before the
   approval gate for small repos; the six-pass structure below for medium or
   large repos. Run the drafting pass only after approval.

Before setup confirmation, try to identify useful context:

- Detect repository name, stack, package manager, and main app directories.
- Detect likely hosting, database/auth, CMS, analytics, monitoring, and CI
  from repo evidence.
- Detect README/docs, environment examples, deployment config, tests, and
  scripts.
- Detect an issue tracker or parent ticket only if available from the user,
  repo metadata, branch name, or active environment.
- Do not promise dashboard verification when the active environment lacks
  access.

Ask the user only when blocked:

- Ask for the repository path only if the current workspace is not the target
  repository.
- Ask for dashboard login or access only when repo evidence cannot answer the
  audit question.
- Ask for a parent tracker ticket only if the user wants ticket or comment
  output tied to a tracker.
- Ask for approved terminology only if client-facing output is requested.

## Access Rules

The following access is automatic:

- Repo files in the current workspace.
- Local read-only commands, git history, tests, docs, and config.
- Public URLs and public documentation.

The following access is not automatic:

- Logged-in dashboards such as GitHub, GitLab, Vercel, Supabase, Sanity,
  Figma, Stripe, analytics, and monitoring.
- Private staging or production sites.
- Organization settings behind authentication.
- Any page that requires a browser session, token, or API key.

Apply these rules:

- Start with repo evidence first.
- Use the browser only when the repo cannot answer the question.
- Use authenticated CLI or API access only if it is already available and
  appropriate.
- Treat dashboard findings as confirmed only if they are actually visible.
- If access is missing, state exactly what is missing and ask for the correct
  login, account, or workspace.
- Do not infer dashboard state from code alone.

## Setup Confirmation

Begin with setup confirmation only. Before running audit passes, state:

1. Project or client name.
2. Target repository path or URL.
3. Parent tracker ticket, if detected or provided.
4. Available access:
   - repo/workspace,
   - issue tracker,
   - browser session,
   - hosting dashboards,
   - database/auth dashboards,
   - CMS dashboards,
   - analytics/monitoring dashboards,
   - staging and production URLs.
5. Known platforms and environments.
6. Proposed pass structure.
7. Output target.
8. Confirmation that no tickets, comments, wiki pages, docs, backlog changes,
   or other outputs will be published or edited without approval.

Ask the human reviewer to reply exactly `CONFIRM` before detailed audit work
when any of these conditions apply:

- The target project or scope was inferred.
- Dashboard access is required.
- The audit is medium or large.
- Any output may later be published.

Do not begin detailed audit findings until the reviewer confirms when
confirmation is required.

## Default Workflow

### 1. Intake And Access Check

Collect:

- Repo URL or path.
- Issue tracker or board.
- Hosting.
- Database or auth.
- CMS.
- Analytics and monitoring.
- Environments.
- Approved terminology.
- Terms to avoid.
- Parent tracker ticket.
- Whether AI may draft only or create approved output.

### 2. Discovery Pass

Build a Current Platform Snapshot. Confirm the actual stack first instead of
assuming the framework, hosting, CMS, database, or architecture.

The snapshot must include:

- Product purpose.
- Main stack.
- Repo structure.
- Environments.
- Hosting and deployment.
- Database/auth.
- CMS/content.
- Analytics/monitoring.
- CI/build/test setup.
- Documentation state.
- Known owners and release responsibilities.
- Confirmed live URLs or missing access.

### 3. Choose Pass Structure

For smaller audits:

1. Discovery pass.
2. Findings pass.
3. Drafting pass after approval.

For medium or large audits:

1. Snapshot, ownership, and environments.
2. Deployment, CI, docs drift, and release flow.
3. Security, data, auth, secrets, and public access control.
4. Features, CMS or content workflow, and placeholder content.
5. Tests, accessibility, performance, SEO, analytics, and monitoring.
6. Ticket drafting, wiki or docs split, and backlog order.

Split security, performance, CMS/content, or accessibility into separate
passes when project risk justifies it. Do not create tiny passes merely
because it is possible; combine smaller topics when the repo is simple or
the context is manageable.

### 4. Review By Section

For each section, capture:

- Evidence.
- Risk.
- Open questions.
- Recommended follow-up.
- Disposition: `Apply`, `Skip`, or `Spin-off`.

Disposition meanings:

- `Apply`: belongs in the current audit output or ticket set.
- `Skip`: is not relevant or is not supported by evidence.
- `Spin-off`: is useful but outside the current audit scope.

Separate facts, assumptions, risks, questions, and recommendations.

### 5. Human Approval Gate

Stop after presenting the audit matrix and suggested ticket set.

Do not publish or change tickets, comments, wiki pages, docs, or backlog order
until a human approves:

- Which tickets to create.
- What belongs in tickets versus wiki or docs.
- Naming.
- Client questions.
- Backlog order.

This publishing approval is separate from the setup `CONFIRM` gate.

### 6. Drafting Pass

After approval, draft or create only the approved outputs:

- Parent tracker updates.
- Spin-off tickets.
- Audit comments.
- Wiki or docs updates.
- Backlog order.
- Executive Summary.

### 7. Follow-Up Pass

If context gets tight, continue from:

- Approved plan.
- Current Platform Snapshot.
- Audit Matrix.
- Approved ticket set.
- Current backlog order.

Do not restart from scratch unless the user asks.

## Standard Audit Sections

- Deployment and release flow.
- CI stability.
- Environment and secret drift.
- Documentation and onboarding drift.
- Security, data, auth, and public access control.
- CMS and content workflow.
- Feature inventory and user-story gaps.
- Test gaps.
- Accessibility.
- Performance and maintainability.
- Analytics and monitoring.
- SEO basics.
- Placeholder or demo content.
- Ownership and release responsibilities.

## Output Requirements

The confirmed output target is binding. When it is `markdown in chat`, return
setup confirmation, pass summaries, findings, and drafts directly in chat.
Do not create a Cursor Canvas, `.canvas.tsx` file, docs file, or other output
artifact unless the human reviewer explicitly requests that destination.
Structured audit content, matrices, or tables do not override a confirmed
chat output target.

Use this required structure:

```markdown
# Vibe Code Rescue Audit: <project>

## Setup Confirmation

## Current Platform Snapshot

## Audit Matrix

## Suggested Tickets

## Suggested Wiki Or Docs Pages

## Questions

## Suggested Backlog Order

## Risks And Unknowns

## Approval Gate
```

## Ticket And Wiki Rules

- Put stable onboarding or reference material in wiki or docs.
- Put findings, risks, and follow-up work in tickets.
- Use short, plain-English ticket titles.
- Start every suggested ticket with a checklist.
- Use one consolidated audit comment per ticket unless a later question needs
  a new comment.
- Link ticket numbers with markdown links when URLs are available.

## Executive Summary Rules

Use the Executive Summary only after:

- The audit is approved.
- The ticket set is in place or drafted.
- Open client decisions are identified.
- Backlog order is approved.

Use these sections:

- `Summary`
- `Stats`
- `Work Completed`
- `Strengths Already In Place`
- `Key Risks`
- `Actions Needed From <client decision-maker>`
- `Next Steps`

Use this tone:

- Plain English.
- Short bullets and short sentences.
- No filler.
- No vague praise.
- Do not put placeholder, partial, or future work in Strengths.
- Keep client action items limited to decisions or approvals.

## Quality Rules

- Detect the actual stack first.
- Use repo evidence first.
- Confirm dashboard findings only when dashboard access is available.
- Keep client-facing language plain, short, and evidence-based.
- Preserve the requested terminology and avoid disallowed terms.

## Completion Summary

End each audit pass with:

- Scope covered.
- Scope not covered.
- Evidence used.
- Confirmed risks.
- Open questions.
- Recommended next step.
- Whether approval is required before continuing.

## Copy-Paste Prompt

If the user wants a ready-to-send prompt, provide this template.
`/fw-vibe-audit` is typed in Cursor chat, not run in the terminal.

```text
/fw-vibe-audit

Project name: <client or project name>
Repository path: <absolute path to target repository>
Parent tracker ticket: <ticket URL or number>
Known platforms: <hosting, database/auth, CMS, analytics, monitoring>
Environments: <local, staging, production URLs if known>
Approved terminology: <terms>
Terms to avoid: <terms>
Output target: <markdown in chat | docs file | ticket draft>
Publishing mode: draft only until human approval

Begin setup confirmation only. Do not generate final findings yet.
Confirm access, proposed pass structure, output target, and approval gates.
After setup confirmation, ask me to reply with exactly:

CONFIRM
```
