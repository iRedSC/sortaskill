---
name: html-communication
description: Use when the user requests a standalone HTML artifact or a visual report best explored outside chat, or when user says "HTML" with no context.
---

# HTML Communication

Create a self-contained HTML document with visual hierarchy suited to the material. Use interaction, color, diagrams, or responsive layout only when they improve comprehension.

Write it to the user-facing output location supplied by the environment. If none exists, use a task-specific workspace directory.

## Publishing

Publish only when the user requests a shareable URL. Read `UPLORD_URL` and `UPLORD_UPLOAD_KEY` from the environment; never print, copy, or embed the key.

## Workflow

1. Confirm the finished file exists and does not overwrite an unrelated artifact.
2. Upload it:

   ```sh
   curl --fail-with-body --silent --show-error \
     --request POST \
     --header "Authorization: Bearer $UPLORD_UPLOAD_KEY" \
     --form "file=@FILE" \
     "$UPLORD_URL/api/uploads/bundu/god-files"
   ```
3. Return the public `url` from the JSON response.

If the document is sensitive or the user requests an unguessable name, add `?random=1`. The resulting URL remains public.

Uploading the same filename to a folder replaces it. Use this to update the document you are working on when changes are requested. Do not replace a file unless you created it or the user requests it.
