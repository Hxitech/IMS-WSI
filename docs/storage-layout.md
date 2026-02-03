# Local Storage Layout

`STORAGE_ROOT` defaults to `./storage` (mounted to `/app/storage` in docker).

Proposed structure:

```
storage/
  attachments/
    {case_id}/
      {slide_id}/
        original-filename.ext
  slides/
    {case_id}/
      {slide_id}/
        ... (DZI tiles, etc.)
```

Currently implemented:
- attachment uploads stored at `attachments/{case_id}/{slide_id}/{filename}`
