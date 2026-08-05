#!/bin/sh
set -eu

agent_kit_dir="${AGENT_KIT_HOME:-$HOME/.agent-kit}"
agent_kit_profile="${AGENT_KIT_PROFILE:-base}"
agent_kit_repo="${AGENT_KIT_REPOSITORY:-https://github.com/cubxxw/agent-kit.git}"

if ! command -v git >/dev/null 2>&1; then
  echo "git is required" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required" >&2
  exit 1
fi

if [ ! -d "$agent_kit_dir/.git" ]; then
  if [ -e "$agent_kit_dir" ]; then
    echo "Refusing to replace non-repository path: $agent_kit_dir" >&2
    exit 1
  fi
  git clone --filter=blob:none "$agent_kit_repo" "$agent_kit_dir"
else
  if [ -n "$(git -C "$agent_kit_dir" status --porcelain)" ]; then
    echo "Refusing to update a dirty checkout: $agent_kit_dir" >&2
    exit 1
  fi
  git -C "$agent_kit_dir" pull --ff-only
fi

"$agent_kit_dir/bin/agent-kit" doctor --strict
"$agent_kit_dir/bin/agent-kit" install --profile "$agent_kit_profile" --tool all
"$agent_kit_dir/bin/agent-kit" status --profile "$agent_kit_profile" --tool all
