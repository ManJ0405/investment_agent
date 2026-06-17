# PR Title

<!--
Format suggestion:
type(scope): short summary
Example: feat(pillar7): add sentiment baseline inference
-->

## What changed

<!-- 3-6 bullets. Focus on behavior and why. -->
- 

## Why this change

<!-- Problem, user impact, or engineering goal. -->
- 

## Scope

<!-- Mark one -->
- [ ] Feature
- [ ] Bug fix
- [ ] Refactor
- [ ] Test only
- [ ] Docs only
- [ ] CI/CD or DevEx

## Pillar impact

<!-- Mark all that apply -->
- [ ] Pillar 1: Price Prediction
- [ ] Pillar 2: Trend Follow
- [ ] Pillar 3: Bull/Bear Signal
- [ ] Pillar 4: Risk Governor
- [ ] Pillar 5: Fundamental Potential
- [ ] Pillar 6: Sector Trends
- [ ] Pillar 7: News Sentiment
- [ ] Pillar 8: 10-K/10-Q RAG
- [ ] Orchestration / Shared infra

## Testing

### Local test commands run

<!-- Paste exact commands -->
```bash
```

### Test results

- [ ] Unit tests pass
- [ ] Integration/e2e tests pass (if touched)
- [ ] Prompt tests pass (if prompt/model behavior changed)
- [ ] Manual smoke test done

## Prompt/Model change checklist (if applicable)

- [ ] Prompt output schema unchanged, or migration included
- [ ] Regression cases checked (recommended: 15-case suite)
- [ ] Critical negative-risk cases reviewed
- [ ] Hallucination/format failure risk considered

## Data and schema impact

- [ ] No schema change
- [ ] Backward-compatible schema change
- [ ] Breaking schema change (migration required)

### Migration notes (if needed)

<!-- DB/schema/config migration steps -->
- 

## Risk and rollback

### Risks introduced

<!-- What can go wrong after merge? -->
- 

### Rollback plan

<!-- Revert PR, toggle flag, or fallback behavior -->
- 

## Observability

- [ ] Logs added/updated where needed
- [ ] Metrics added/updated where needed
- [ ] Error handling/alerts considered

## Deployment plan

- [ ] Safe to deploy immediately
- [ ] Deploy behind feature flag
- [ ] Staging validation required before prod

## Security and secrets

- [ ] No secrets added
- [ ] `.env` / credentials not committed
- [ ] External API permissions reviewed

## Documentation

- [ ] README updated (if behavior changed)
- [ ] `backend/IMPLEMENTATION_GUIDE.md` updated (if process changed)
- [ ] Inline comments/docs added where logic is non-obvious

## Screenshots / artifacts (optional)

<!-- Add logs, charts, sample request/response, or test report snippets -->

## Reviewer checklist

<!-- Helpful for self-review too -->
- [ ] Problem and scope are clear
- [ ] Code is readable and modular
- [ ] Tests are meaningful (not only happy path)
- [ ] Failure paths are handled
- [ ] Merge is safe
