---
name: babysit-pr
description: Use when babysitting a GitHub pull request through review rounds.
compatibility: "Requires bash, cat, gh, git, jq, and sed. The GitHub CLI must be authenticated."
disable-model-invocation: true
---

# Babysit a PR

Carry a GitHub pull request to a reviewed, merge-ready state. Each push starts another review round
and can expose adjacent findings. Verify every finding against the current code, fix blockers, and
close every in-scope review loop in writing.

## Operating rules

- Verify each finding against the current code. Record the claim, code evidence, and reproduction
  result; a severity badge is not evidence.
- Reply to every in-scope item. Resolve an inline thread only after it is fixed and pushed, rejected
  with evidence, or deferred with a real issue.
- Do not autonomously handle human reviews or ordinary comments from the PR author; surface them.
  The exception is a debate-review thread marked from the author's account.
- Never merge the PR. Prepare it for the user's decision.

## Harvest the round

Run the collector from the PR checkout, or pass `owner/repo` as the second argument:

```bash
"<skill-dir>/scripts/threads.sh" <N> > /tmp/pr-<N>-round-<k>.json
```

The JSON has three surfaces:

- `.threads` contains inline review threads, including resolved and outdated entries. `thread_id` is
  the GraphQL node ID used to resolve; `reply_to` is the REST comment ID used to reply in-thread.
- `.reviews` contains non-empty top-level review bodies and no resolvable thread. Answer the
  relevant bodies with one PR conversation comment per round.
- `.head`, `.pr_author`, and `.unresolved` provide the reviewed SHA, PR author, and unresolved count.

Compare filtered and unfiltered totals before relying on a `jq` query:

```bash
jq '{threads: (.threads|length), reviews: (.reviews|length)}' /tmp/pr-<N>-round-<k>.json
```

An empty or failed lookup is missing data, not a clean round. Compare each round with the previous
one: `outdated` may mean the finding is already fixed, and a higher `comment_count` may contain a
follow-up.

Compare `.reviews[].commit_id` with `.head`; for debate-review, compare `debate_head` with `.head`.
A timestamp does not prove that the reviewer saw the push.

Only treat a review as in scope when `author_bot` is true or the thread has `debate_review: true`.
Do not hardcode bot names. Use `.pr_author` and `author_is_pr_author` to distinguish the author's
ordinary comments from review findings.

## Classify by impact

- Blocking: a correctness bug or broken edge case, security or data hazard, contract or
  acceptance-criteria violation, migration or schema risk, or a failing or newly flaky check.
- Non-blocking: naming, structure, documentation, test nitpicks, micro-performance, or style unless
  it causes a blocking outcome.

Treat an ambiguous finding as blocking until the code resolves it. For a debate-review thread with
`debate_status: contested`, verify the counter-argument and state which side the code supports.

## Fix and publish

Work the round in one pass:

- Reproduce behavioral defects where practical and fix the confirmed blockers.
- Run the repository's required gate once. Do not rerun an already passing gate for the same SHA.
- Commit and push once, re-harvest, and confirm that `.head` matches the published SHA.
- Reject a finding only with code, guard, or test evidence.
- If publication or verification fails, leave the thread open and report the blocker.
- Include user-approved non-blocking fixes in the next consolidated push.

## Reply and resolve

Get the reply attribution once per session:

```bash
gh api user --jq '.name // .login'
```

Begin every reply with `I am <model-slug> writing on behalf of <user>.` Sign your own model name;
the person is the owner of the account posting the reply.

Reply inside the originating thread:

```bash
gh api --method POST "repos/<owner>/<repo>/pulls/<N>/comments/<reply_to>/replies" \
  -f body="$(cat /tmp/reply.md)"
```

Resolve the thread:

```bash
gh api graphql -f query='mutation($t:ID!){
  resolveReviewThread(input:{threadId:$t}){ thread{ isResolved } } }' -F t="<thread_id>"
```

For relevant top-level reviews, post one conversation comment per round:

```bash
gh api --method POST "repos/<owner>/<repo>/issues/<N>/comments" \
  -f body="$(cat /tmp/review-reply.md)"
```

Use one verdict template:

```text
I am <model-slug> writing on behalf of <user>.

<Confirmed and fixed in `SHA` | Declining | Deferred> - <brief evidence, reproduction, or issue link>.
```

A deferred finding needs a real issue with a link to the thread, the affected file, and the reason.

## Non-blockers

After handling blockers, present the remaining non-blocking findings together once per round with a
recommendation for each: fix now, open an issue, or reject. Let the user choose, then close each
thread by the same closure rules.

## Re-trigger and wait

One invocation covers the initial harvest, at most two consolidated repair pushes, and two re-review
cycles unless the user explicitly extends it.

- For debate-review, run `<debate-review skill-dir>/scripts/review-pr.mjs <pr-url>`, wait for it to
  post, then harvest. It reviews one head SHA per run and exits with status 3 when that head was
  already reviewed.
- For Codex, run `gh pr comment <N> --body '@codex review'`. Verify `commit_id` before treating the
  response as coverage of the current push.
- Greptile and similar bots re-review pushes automatically. Handle their findings when they appear.

Poll in the background. Wait 8 to 15 minutes for Codex. Allow other bots up to 10 minutes beyond
their normal window, with an explicitly longer deadline for a large diff. When a deadline passes,
mark that reviewer unavailable and report it; unavailable is not clean. A round is ready only when
every expected reviewer has reviewed the current head or exhausted its budget.

At the budget boundary, hand off the remaining findings, unresolved threads, last reviewed SHA, and
unavailable reviewers.

## Before merge

The merge gate is a clean round from the repository's primary reviewer on the final head SHA. Every
push, including a documentation-only or nit-only push, creates a new final-head review requirement.

- Codex: a plain no-findings response against the final head. No response is not a pass.
- debate-review: its round body is present with `debate_head` equal to the final head,
  `debate_agreed` and `debate_contested` both zero, and no unresolved review threads. If the body is
  missing, rerun the review.

Re-harvest and read the latest PR comments. Report rounds run, blockers fixed with their SHAs,
findings rejected and why, issues filed, unresolved threads, and CI state. Then ask whether to merge.

## Stop and surface

Pause and report when:

- a correct bot finding requires work outside the PR's scope
- two bots contradict each other and the code, tests, and contract do not settle the point
- the same finding recurs after a re-verified retry
- a human reviewer or ordinary PR-author comment needs a decision
- CI fails for infrastructure reasons
- the repair-cycle budget is exhausted
- the user asks to stop, publish current work, or end the loop

For a user-requested stop, cancel active polls and long-running gates, run only the smallest check
that can finish promptly, publish only safe work, disclose incomplete verification, and start no new
review round.
