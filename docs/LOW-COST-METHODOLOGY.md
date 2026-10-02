# Low-cost launch-video workflow

This workflow aims to get a polished, editable first cut without requiring a paid generative-video service. HyperFrames handles the timeline and local rendering; your product provides the real screens and your brief provides the story.

## 1. Write the brief before animating

Answer these in a short document:

- Who should understand this video?
- What job does the product help them do?
- What should viewers remember after one minute?
- Which three to five features prove that promise?
- What is the one next step you want viewers to take?

Use [`../prompts/plan-storyboard.md`](../prompts/plan-storyboard.md) to turn the answers into a timed scene list.

## 2. Use a short, paced storyboard

Start with a hook, a familiar problem, the product promise, a small number of feature beats, proof or outcome, and a call to action. Keep each scene to one idea. Use `video.json` as the source of truth for timing and copy.

## 3. Gather authentic capture assets

Capture the actual app at the moments named in the storyboard. Use a fictional demo workspace when possible. Remove customer information, credentials, API keys, browser notifications, and personal data. If a feature is not live, label it clearly instead of implying that it is available.

## 4. Build with lightweight motion

The included builder uses HTML, CSS, SVG, and HyperFrames' timeline runtime. Make the typography, color, layout, and timing do most of the work. Add optional SFX only when they help the edit; keep audio assets local and licensed. The starter includes no music or image/video generation calls.

## 5. Preview and check before rendering

```bash
npm run build
npm run check
npm run snapshot
npm run preview
```

Check the complete timeline in Studio, including text fit, capture legibility, and the final frame. Ask for approval before rendering. Local render time depends on machine performance, frame rate, and visual complexity.

## 6. Keep costs visible

- The sample has no hosted AI API call and needs no API key.
- HyperFrames CLI is fetched with `npx` on first use; it is pinned in `package.json` for repeatable examples. Scene motion loads GSAP from jsDelivr.
- Bring your own screenshots, fonts, and licensed SFX; the repository bundles none.
- Optional paid generation tools, stock media, and hosted rendering are separate choices, not requirements of this starter.

This is a workflow template, not a promise that every user's render will be free. Hardware, service plans, and licensed media choices can add cost.
