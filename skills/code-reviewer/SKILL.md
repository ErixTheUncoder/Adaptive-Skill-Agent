---
name: code-reviewer
description: >
  Reviews code for bugs, security issues, performance problems, and best practices.
  Use when the user asks for a code review, security audit, or wants feedback on
  code quality. Do NOT use for writing new code, debugging runtime errors, or
  explaining how code works.
license: MIT
---

# Code Review Skill

## When to Use
- User asks to review or audit code
- User wants feedback on code quality, security, or performance
- User asks "is this code good?" or "what's wrong with this?"

## Instructions
1. Read the target file(s) using the filesystem tools
2. Analyze the code for:
   - **Bugs**: Logic errors, edge cases, off-by-one errors
   - **Security**: Injection vulnerabilities, hardcoded secrets, unsafe operations
   - **Performance**: Inefficient algorithms, unnecessary allocations, N+1 queries
   - **Readability**: Clear naming, consistent style, appropriate comments
   - **Best Practices**: Language idioms, design patterns, error handling
3. Categorize findings by severity: Critical, Warning, Suggestion
4. Provide specific line references and suggested fixes
5. Write the review to `./workspace/code-review-<filename>.md`

## Output Format
```markdown
# Code Review: [filename]

## Critical Issues
- [Line X] Description of issue. Fix: ...

## Warnings
- [Line X] Description of concern. Suggestion: ...

## Suggestions
- [Line X] Minor improvement. Consider: ...

## Summary
[Overall assessment and next steps]
```
