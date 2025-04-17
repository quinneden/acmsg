import json
import requests


class OpenRouter:
    def post_api_request(api_token, git_status, git_diff, model):
        # spec = requests.get(
        #     "https://github.com/conventional-commits/conventionalcommits.org/raw/refs/heads/master/content/v1.0.0/index.md"
        # )
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json",
            },
            data=json.dumps(
                {
                    "model": model,
                    "stream": False,
                    "messages": [
                        # {
                        #     "role": "system",
                        #     "content": f"```markdown\n{spec.text}\n```",
                        # },
                        {
                            "role": "system",
                            "content": "# IDENTITY AND PURPOSE\nYou are a git commit assistant specializing in writing commit messages following the\nConventional Commits specification (v1.0.0). Your sole passion is finding the differences\nbetween git diffs, analyzing the those changes, and summarizing the most significant affects\nof those changes. You are driven almost to the point of obsession over creating perfect commit\nmessages and strive to create the most concise and informative message possible.\n\n## RULES\n- Type must be one of: feat, fix, docs, style, refactor, perf, test, chore, revert\n- Subject line should be 50-70 characters\n- Use imperative mood in subject line\n- Do not end subject line with period\n- Body should explain what and why, not how\n- For minor changes, use fix instead of feat\n- Response should be the commit message only, no explanations\n- If the commit is an initial commit, type is optional\n\n## COMMIT MESSAGE FORMAT\n<type>(<scope>): <subject>\n\n<body>\n",
                        },
                        {
                            "role": "user",
                            "content": f"Here are the file changes and git diff for the repository:\n\n## File changes\n{git_status}\n\n## Diff\n{git_diff}\n\nNow, take a moment to think about the information, and generate a\nclean, highly readable commit message.\n",
                        },
                    ],
                }
            ),
        )
        if not response.ok:
            error_data = response.json()
            raise Exception(
                f"API request failed: {error_data.get('error', response.text)}"
            )
        else:
            return response
