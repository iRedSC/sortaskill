---
name: file-upload
description: Use when the user asks to publish or share a local file through their configured upload service, or when user says "LINK" with no context. Do not invoke merely to display a local file.
metadata:
  location-key: FILE_UPLOAD
---

# File upload

Read `FILE_UPLOAD` from the injected locations index, then read that file and follow its publishing workflow.

If the key or file does not exist, interview the user before uploading anything. Ask which service or local workflow they use, where its instructions should live, and what authorization or replacement rules apply. Create the instructions and append `FILE_UPLOAD=<location>` to the canonical index after they confirm.

Publish only files the user authorized sharing. Never print or copy upload credentials. Return the resulting shareable location.

<!-- locations-index: setup.py replaces this comment in installed copies -->
