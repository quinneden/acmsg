{
  commitizen,
  version,
  writeShellApplication,
  ...
}:
writeShellApplication {
  name = "create-release-acmsg-v${version}";
  runtimeInputs = [ commitizen ];
  text = ''
    baseDir=$(git rev-parse --show-toplevel)

    uncommitedChanges=$(git diff --compact-summary)
    unpushedCommits=$(git log --format=oneline origin/main..main)

    if [[ $(git rev-parse --show-toplevel) != "$PWD" ]]; then
      echo "This script must be run from the root of the repository" >&2
      exit 1
    elif [[ "$(git symbolic-ref --short HEAD)" != "main" ]]; then
      echo "must be on main branch" >&2
      exit 1
    elif [[ -n "$uncommitedChanges" ]]; then
      echo -e "There are uncommited changes, exiting:\n$uncommittedChanges" >&2
      exit 1
    elif [[ "$unpushed_commits" != "" ]]; then
      echo -e "\nThere are unpushed changes, exiting:\n$unpushedCommits" >&2
      exit 1
    fi

    currentVersion=${version}
    latestReleaseTag=$(git tag --sort=-creatordate | grep -E "^v[0-9]+.[0-9]+.[0-9]+$" | head -n 1)

    if [[ "v$currentVersion" != $latestReleaseTag ]]; then
      echo "error: the version in pyproject.toml doesn't match the latest release tag: $version != $latestReleaseTag" >&2
      exit 1
    fi

    flags=(
      --changelog
      --major-version-zero
    )

    while [[ $# -gt 0 ]]; do
      case "$1" in
        major|minor|patch)
          flags+=(--increment "$1")
          shift
          ;;
        *)
          echo "error: unknown option: $1" >&2
          exit 1
          ;;
      esac
    done

    cz bump "''${flags[@]}" --
  '';
}
