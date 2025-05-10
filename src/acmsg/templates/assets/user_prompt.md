## TASK
Generate a commit message describing the changes in this git diff.

## GUIDELINES
- Use imperative mood ("Add feature" not "Added feature")
- Prioritize functional impacts over files changed
- Identify patterns suggesting unified purpose across changes
- Consider relationships between changes when determining significance
- Limit body to ~200 characters unless complexity requires more detail
- Omit body entirely if the subject line captures the change adequately

## INPUT
File statuses:
{{ status }}

Diff:
{{ diff }}
