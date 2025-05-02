## USER-SPECIFIED TASK
I am about to provide you with a git diff and file statuses of the changed files in my codebase.
Generate a commit message describing the changes made in the codebase based on the provided data.
Bias towards a shorter message body, e.g. ~200 characters, but prioritize clarity over brevity. Write with an imperative mood.
If a longer message body is required to sufficiently describe a change, then do so, but do not over explain.
If you need a better understanding of a change, then reread the section of the git diff that corresponds
to the change, and analyze the purpose of the changed code and its impact on the overall functionality of the codebase.

## USER INPUT
Here are the statuses of each changed file in the codebase:
{{ status }}
---

Here is the git diff of every changed file in the codebase:
{{ diff }}
---
