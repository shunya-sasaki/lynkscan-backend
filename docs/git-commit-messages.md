# Instructions for Git Commit Messages

- Use the conventional commit format, the commit message should be structured as follows:

  '''
  <type>[optional scope]: <description>

  [optional body]

  [optional footer(s)]
  '''

- The first line is the commit title and should be concise
- The length of the first line must be at most 50 characters.
- The third line is optional and can provide additional context or details about the change.
- The type in the first line must be one of the following:
  - build: Changes that affect the build system or external dependencies
  - ci: Changes to our CI configuration files and scripts
  - docs: Documentation only changes
  - feat: A new feature
  - fix: A bug fix
  - perf: A code change that improves performance
  - refactor: A code change that neither fixes a bug nor adds a feature
  - style: Changes that do not affect the meaning of the code
  - test: Adding missing tests or correcting existing tests
