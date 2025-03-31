import json
import requests


class OpenRouter:
    def post_api_request(api_token, git_status, git_diff, model):
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": model,
                "stream": False,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a git commit message generator. Your job is to generate conventional commit messages based on the provided context. The commit message should be formatted according to the conventional commits specification."
                    },
                    {
                        "role": "user",
                        "content": f"Generate a commit message for these changes:\n\nFile changes:\n{git_status}\n\nDiff:\n{git_diff}\n\nFormat:\n###STARTFORMAT###\n<type>(<optional scope>): <subject>\n\n<optional body>\n###ENDFORMAT###\nImportant:\n- Type must be one of: feat, fix, docs, style, refactor, perf, test, chore\n- Subject line should be 50-70 characters\n- Use imperative mood in subject line\n- Do not end subject line with period\n- Body should explain what and why, not how\n- For minor changes, use fix instead of feat\n\nResponse should be the commit message only, no explanations\n- If the commit is an initial commit, type is optional"
                    }
                ],
            })
        )
        if not response.ok:
            error_data = response.json()
            raise Exception(
                f"API request failed: {error_data.get('error', response.text)}"
            )
        else:
            return response
