#!/usr/bin/env bash
set -euo pipefail

: "${GITHUB_TOKEN:?Defina GITHUB_TOKEN ou GH_TOKEN antes de executar.}"
: "${REPO:?Defina REPO no formato OWNER/REPO. Ex.: HUGOALMEIDARAMOS/3AIER}"

curl -sS -X PUT \
  -H "Authorization: Bearer ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/${REPO}/branches/main/protection" \
  -d @- <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "checks": [
      { "context": "agent-smoke" },
      { "context": "evals" }
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "require_last_push_approval": true,
    "bypass_pull_request_allowances": {}
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_linear_history": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": true
}
JSON

printf '\nProteção de branch aplicada para main.\n'
printf 'Exigências: 1 review obrigatório + CODEOWNERS + status checks obrigatórios.\n'
