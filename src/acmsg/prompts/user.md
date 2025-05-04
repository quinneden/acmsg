## USER-SPECIFIED TASK

I am about to provide you with a git diff and file statuses of the changed files in my codebase.

Generate a commit message describing the changes made in the codebase based on the provided data.

Bias towards a shorter message body, e.g. ~200 characters, but prioritize clarity over brevity. Write with an imperative mood.

If a longer message body is required to sufficiently describe a change, then do so, but do not over explain.

Think about which changes are most significant to the functionality of the code.

## USER INPUT

Here are the statuses of each changed file in the codebase:

{{ status }}

Here is the diff of every changed file in the codebase:

{{ diff }}
