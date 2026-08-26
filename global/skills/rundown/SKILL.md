---
name: rundown
description: Use when the user asks for a rundown of a code change before implementation.
---

# Rundown

Review the request, then inspect only enough code to ground the response. Trace the primary path, nearby types or callers, and relevant tests. Do not edit files or begin implementation.

Return two concise sections:

## Problem

Reiterate the problem in concrete terms, including the expected behavior and the current gap.

## Proposed solution

Describe the simplest cohesive approach. Call out an important tradeoff or uncertainty only when it materially affects the solution.

Keep the response quick and scoped. Do not turn it into a full implementation plan.
