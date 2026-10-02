# Product capture checklist

Feature scenes should show genuine app screens. The starter intentionally uses labeled placeholders until you provide them.

## File paths

The sample `video.json` expects:

| Scene | File |
| --- | --- |
| Feature one | `assets/captures/feature-one.png` |
| Feature two | `assets/captures/feature-two.png` |
| Feature three | `assets/captures/feature-three.png` |

Use PNG, JPEG, or WebP. Update each scene's `capture` field if you choose a different filename. Screenshots in `assets/captures/` are ignored by Git by default.

## Capture checklist

- Capture at 16:9 when practical; 1920 × 1080 gives a clear starting point.
- Hide browser chrome and unrelated windows; crop to the real product view.
- Use a fictional or sanitized workspace and remove personal, customer, clinical, financial, and secret data.
- Keep the real product controls and labels intact. Do not replace missing product UI with a mock screenshot.
- Ensure the key area remains readable at 1080p and on a phone-sized preview.
- Capture a complete state, not a loading spinner, tooltip, or menu covering the feature.
- Keep unreleased features marked as planned or in development.

If you only have a walkthrough recording, note timestamps for each scene and extract still frames locally before rebuilding. The generator reads image paths from `video.json`; it does not extract frames from video automatically.
