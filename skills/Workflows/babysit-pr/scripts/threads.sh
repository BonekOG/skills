#!/usr/bin/env bash
# Harvest a GitHub pull request's inline review threads and top-level review bodies in one JSON
# object.
#
# Usage: threads.sh <number> [owner/repo]
#        threads.sh 123
#        threads.sh 123 owner/repo
#
# When owner/repo is omitted, detect it from the origin remote in the current directory. The origin
# must be github.com.
#
# Emits JSON on stdout:
#   .repo, .pr, .head, .pr_author
#   .threads[] inline review threads, each with:
#       thread_id      GraphQL node id; use to resolve the thread
#       reply_to       REST comment id; use to reply inside the thread
#       resolved, resolvable, outdated
#       author, author_bot, author_is_pr_author
#       path, line, original_line, line_side, comment_count
#       body, last_author, last_body
#       source         "thread"
#       debate_review, debate_id, debate_status, debate_severity, debate_level
#                      parsed from a debate-review marker in the first comment
#   .reviews[] top-level review bodies with no thread to resolve:
#       id, author, author_bot, state, commit_id, submitted_at, body, source
#       debate_review, debate_head, debate_agreed, debate_contested
#   .unresolved count of unresolved threads
#
# Empty review bodies, including reply wrappers, are excluded from .reviews. Comments from the PR
# author remain in the output; the caller decides whether they are in scope.

set -euo pipefail

usage() {
  while IFS= read -r line; do
    [[ "$line" == '#!/usr/bin/env bash' ]] && continue
    [[ "$line" == 'set -euo pipefail' ]] && break
    printf '%s\n' "$line"
  done < "$0"
}

NUMBER=""; REPO=""
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    *) if [ -z "$NUMBER" ]; then NUMBER="$1"; elif [ -z "$REPO" ]; then REPO="$1"; else echo "unexpected argument: $1" >&2; exit 2; fi; shift ;;
  esac
done
[ -n "$NUMBER" ] || { usage >&2; exit 2; }

if [ -z "$REPO" ]; then
  ORIGIN=$(git remote get-url origin 2>/dev/null || true)
  [ -n "$ORIGIN" ] || { echo "pass owner/repo: no git origin in cwd" >&2; exit 2; }
  ORIGIN_HOST=$(printf '%s' "$ORIGIN" | sed -E 's#^(https?://|ssh://git@|git@)([^/:]+)[/:].*#\2#')
  ORIGIN_PATH=$(printf '%s' "$ORIGIN" | sed -E 's#^(https?://|ssh://git@|git@)[^/:]+[/:]##; s#/$##; s#\.git$##')
  [ "$ORIGIN_HOST" = "github.com" ] || { echo "not a GitHub origin: $ORIGIN_HOST" >&2; exit 2; }
  REPO="$ORIGIN_PATH"
fi

case "$REPO" in
  */*) ;;
  *) echo "owner/repo required, got: $REPO" >&2; exit 2 ;;
esac

JQ_MARKERS='
  def thread_marker:
    . + ((.body // "") | capture("<!-- debate-review:(?<debate_id>[FD][0-9]+) status=(?<debate_status>[a-z-]+) severity=(?<debate_severity>[a-z-]+)(?: level=(?<debate_level>P[0-9]))?[^>]*-->")
          // {debate_id:null, debate_status:null, debate_severity:null, debate_level:null})
    | . + {debate_review: (.debate_id != null)};
  def review_marker:
    . + ((.body // "") | capture("<!-- debate-review head=(?<debate_head>[0-9a-f]+)(?: [^>]*?agreed=(?<debate_agreed>[0-9]+) contested=(?<debate_contested>[0-9]+))?[^>]*-->")
          // {debate_head:null, debate_agreed:null, debate_contested:null})
    | .debate_agreed |= (if . == null then null else tonumber end)
    | .debate_contested |= (if . == null then null else tonumber end)
    | . + {debate_review: (.debate_head != null)};
'

owner="${REPO%%/*}"
name="${REPO##*/}"

pr_author=$(gh api "repos/$REPO/pulls/$NUMBER" --jq '.user.login')

# --paginate follows pageInfo until exhausted; --slurp wraps the pages in one array.
# shellcheck disable=SC2016
pages=$(gh api graphql --paginate --slurp -f query='
query($owner:String!,$repo:String!,$pr:Int!,$endCursor:String){
  repository(owner:$owner,name:$repo){
    pullRequest(number:$pr){
      headRefOid
      reviewThreads(first:100, after:$endCursor){
        pageInfo{ hasNextPage endCursor }
        nodes{
          id isResolved isOutdated path line originalLine diffSide viewerCanResolve
          first: comments(first:1){ totalCount nodes{ databaseId author{login __typename} body } }
          last:  comments(last:1){ nodes{ author{login} body } }
        }
      }
    }
  }
}' -F owner="$owner" -F repo="$name" -F pr="$NUMBER")

head=$(jq -r '.[0].data.repository.pullRequest.headRefOid' <<<"$pages")

threads=$(jq --arg pr_author "$pr_author" "$JQ_MARKERS"'
  [.[].data.repository.pullRequest.reviewThreads.nodes[] | {
      thread_id:     .id,
      reply_to:      .first.nodes[0].databaseId,
      resolved:      .isResolved,
      resolvable:    .viewerCanResolve,
      outdated:      .isOutdated,
      author:        .first.nodes[0].author.login,
      author_bot:    (.first.nodes[0].author.__typename == "Bot"),
      author_is_pr_author: (.first.nodes[0].author.login == $pr_author),
      path:          .path,
      line:          (.line // .originalLine),
      original_line: .originalLine,
      line_side:     .diffSide,
      comment_count: .first.totalCount,
      body:          .first.nodes[0].body,
      last_author:   .last.nodes[0].author.login,
      last_body:     .last.nodes[0].body,
      source:        "thread"
    } | thread_marker ]' <<<"$pages")

# --slurp here too: past one page, bare --paginate emits back-to-back arrays.
reviews=$(gh api "repos/$REPO/pulls/$NUMBER/reviews" --paginate --slurp \
  | jq "$JQ_MARKERS"'
    [.[][] | {id, author: .user.login, author_bot: (.user.type == "Bot"),
              state, commit_id, submitted_at, body, source: "review"}
     | select(.body != "") | review_marker ]')

jq -n --arg repo "$REPO" --arg pr "$NUMBER" --arg head "$head" --arg pr_author "$pr_author" \
      --argjson threads "$threads" --argjson reviews "$reviews" \
  '{repo:$repo, pr:($pr|tonumber), head:$head, pr_author:$pr_author,
    threads:$threads, reviews:$reviews,
    unresolved:[$threads[] | select(.resolved == false)] | length}'
