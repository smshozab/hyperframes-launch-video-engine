# Prompt: make a launch-video storyboard

Paste this prompt and fill in the bracketed fields. Ask the assistant for a draft; verify every claim against the product before using it.

```text
Create a concise, factual storyboard for a product launch video.

Product: [name]
Audience: [who this is for]
Product promise: [one sentence]
Verified features: [list]
Proof points that may be used: [list; write "none" if none]
Call to action: [destination or next step]
Target length: [seconds]
Tone and palette: [description]
Available authentic screenshots: [scene names and file paths, or none]

Return a JSON object with:
- project: brand, title, width, height, fps, durationSeconds, palette, fonts
- scenes: id, type, durationSeconds, eyebrow, title, support, and capture where type is feature
- audio: an empty array unless I explicitly provide licensed local SFX paths

Use only the facts above. Do not invent metrics, testimonials, features, screenshots, UI, integrations, or customer names. Make each scene communicate one idea. Scene durations must add up exactly to the target length. For every feature that lacks an authentic screenshot, set a capture path under assets/captures/ and leave the placeholder workflow intact. Keep copy short enough to fit on a 16:9 frame.
```
