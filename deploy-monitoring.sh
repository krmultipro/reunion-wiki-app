#!/usr/bin/env bash
# Deploy only committed monitoring files; application checkout is untouched.
set -euo pipefail
cd "$(dirname "$0")"
commit=$(git rev-parse "${1:-HEAD}")
remote=reunionwiki
stage="/home/reunionwiki/deployments/monitoring-$commit"
if [[ -n "$(git status --porcelain -- monitoring deploy-monitoring.sh)" ]]; then
  echo 'Committer les modifications du monitoring avant le déploiement.' >&2
  exit 1
fi
ssh "$remote" "umask 077; mkdir -p '$stage'"
git archive "$commit" monitoring | ssh "$remote" "tar -x -C '$stage'"
ssh "$remote" bash "$stage/monitoring/deploy-remote.sh" "$stage" "$commit"
