{
  commitizen,
  git,
  version,
  writeShellApplication,
  ...
}:
writeShellApplication {
  name = "acmsg-bump-version";
  runtimeInputs = [
    commitizen
    git
  ];

  text = ''
    flags=()
    explicit_version=

    while [[ $# -gt 0 ]]; do
      case "$1" in
        major|minor|patch)
          flags+=("--increment" "$1")
          shift
          ;;
        [v]*.*.*)
          explicit_version="''${1/v}"
          shift
          ;;
        -*)
          if [[ $# -gt 1 ]] && [[ ! $2 == -* ]]; then
            flags+=("$1" "$2")
            shift 2
          else
            flags+=("$1")
            shift
          fi
          ;;
        *)
          echo "error: unknown option: $1" >&2
          exit 1
          ;;
      esac
    done

    baseDir=$(git rev-parse --show-toplevel)
    branch=$(git symbolic-ref --short HEAD)
    currentVersion=${version}
    latestReleaseTag=$(git tag --sort=-creatordate | grep -E "^v[0-9]+.[0-9]+.[0-9]+$" | head -n 1)
    uncommittedChanges=$(git diff --compact-summary && git diff --cached --compact-summary)
    unpushedCommits=$(git log --format=oneline origin/main..main)

    if [[ $baseDir != "$PWD" ]]; then
      echo "This script must be run from the root of the repository" >&2
      exit 1
    elif [[ $branch != "main" ]]; then
      echo "must be on main branch" >&2
      exit 1
    elif [[ -n "$uncommittedChanges" ]]; then
      echo -e "There are uncommitted changes, exiting.\n\n$uncommittedChanges" >&2
      exit 1
    elif [[ -n "$unpushedCommits" ]]; then
      echo -e "\nThere are unpushed changes, exiting.\n\n$unpushedCommits" >&2
      exit 1
    elif [[ "v$currentVersion" != "$latestReleaseTag" ]]; then
      echo "error: the version in pyproject.toml doesn't match the latest release tag: $currentVersion != $latestReleaseTag" >&2
      exit 1
    fi

    if [[ -z $explicit_version ]]; then
      flags+=("--major-version-zero")
    fi

    cz bump "''${flags[@]}" --

    newVersion=$(cz version --project)

    read -rN1 -p "Push v$newVersion to remote? (y/N): " input
    if [[ $input != [yY] ]]; then
      echo "To push the new tag to the remote, run:"
      echo
      echo "    git push origin main v$newVersion"
      exit 0
    else
      git push origin main "v$newVersion"
    fi
  '';
}
