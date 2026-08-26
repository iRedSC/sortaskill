---
name: file-upload
description: Use when the user asks to publish or share a local image or video through the configured Uplord service. Do not invoke merely to display a local file.
---

# File Upload

Publish only files the user authorized sharing. Read `UPLORD_URL` and `UPLORD_UPLOAD_KEY` from the environment; never print, copy, or embed the key.

## Workflow

1. Resolve each requested local file and confirm it exists.
2. Upload one file to a human-readable folder path:

   ```sh
   curl --fail-with-body --silent --show-error \
     --request POST \
     --header "Authorization: Bearer $UPLORD_UPLOAD_KEY" \
     --form "file=@FILE" \
     "$UPLORD_URL/api/uploads/bundu/images?random=1"
   ```

3. Prefer `random=1`; it replaces the filename with a UUID, making the public URL harder to guess but not private.
4. Return the public `url` from the JSON response.

Uploading the same filename to a folder replaces it. Do not replace a file unless the user requested it or clearly authorized the replacement.
