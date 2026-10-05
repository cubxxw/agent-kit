#!/bin/sh
set -eu

agent_kit_dir="${AGENT_KIT_HOME:-$HOME/.agent-kit}"
agent_kit_profile="${AGENT_KIT_PROFILE:-base}"
agent_kit_tool="${AGENT_KIT_TOOL:-core}"
agent_kit_repo="${AGENT_KIT_REPOSITORY:-https://github.com/cubxxw/agent-kit.git}"
agent_kit_branch="${AGENT_KIT_BRANCH:-main}"

normalize_repository() {
  printf '%s\n' "$1" | sed \
    -e 's|^git@github.com:|https://github.com/|' \
    -e 's|^ssh://git@github.com/|https://github.com/|' \
    -e 's|/$||' -e 's|\.git$||'
}

if ! command -v git >/dev/null 2>&1; then
  echo "git is required" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required" >&2
  exit 1
fi

if [ ! -e "$agent_kit_dir/.git" ]; then
  if [ -e "$agent_kit_dir" ]; then
    echo "Refusing to replace non-repository path: $agent_kit_dir" >&2
    exit 1
  fi
  git clone --filter=blob:none --branch "$agent_kit_branch" "$agent_kit_repo" "$agent_kit_dir"
else
  agent_kit_origin=$(git -C "$agent_kit_dir" remote get-url origin)
  if [ "$(normalize_repository "$agent_kit_origin")" != "$(normalize_repository "$agent_kit_repo")" ]; then
    echo "Refusing to update a checkout with an unexpected origin. Check the repository before retrying." >&2
    exit 1
  fi
  if [ "$(git -C "$agent_kit_dir" branch --show-current)" != "$agent_kit_branch" ]; then
    echo "Refusing to update an unexpected branch. Expected: $agent_kit_branch" >&2
    exit 1
  fi
  if [ -n "$(git -C "$agent_kit_dir" status --porcelain)" ]; then
    echo "Refusing to update a dirty checkout: $agent_kit_dir" >&2
    exit 1
  fi
  git -C "$agent_kit_dir" fetch origin "$agent_kit_branch"
  git -C "$agent_kit_dir" merge --ff-only FETCH_HEAD
fi

"$agent_kit_dir/bin/agent-kit" doctor --strict
"$agent_kit_dir/bin/agent-kit" plan --profile "$agent_kit_profile" --tool "$agent_kit_tool" --json
"$agent_kit_dir/bin/agent-kit" install --profile "$agent_kit_profile" --tool "$agent_kit_tool"
"$agent_kit_dir/bin/agent-kit" status --profile "$agent_kit_profile" --tool "$agent_kit_tool"
