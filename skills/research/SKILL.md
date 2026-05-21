---
name: research
description: >
  Conducts comprehensive web research on any topic. Use when the user asks for
  research, information gathering, competitive analysis, market research, or needs
  current data from the web. Do NOT use for writing content or code review.
license: MIT
compatibility: Requires internet access
---

# Web Research Skill

## When to Use
- User asks to research a topic, find information, or gather data
- User needs current/recent information from the web
- Competitive analysis or market research requests

## Instructions
1. Parse the research query to identify key topics and sub-questions
2. Break complex queries into multiple focused search queries
3. Use available search tools to gather initial results
4. If results are insufficient, refine queries with different keywords
5. Cross-reference multiple sources for accuracy
6. Synthesize findings into a structured summary with:
   - Key findings
   - Sources referenced
   - Any gaps or uncertainties
7. Save detailed findings to `./workspace/research-<topic>.md`

## Output Format
```markdown
# Research: [Topic]

## Summary
[Brief overview of findings]

## Key Findings
- Finding 1 (source)
- Finding 2 (source)

## Sources
- [Source 1](url)
- [Source 2](url)

## Notes
[Any caveats or areas needing further research]
```
