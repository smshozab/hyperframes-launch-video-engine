# HyperFrames Launch Video Engine

A clone-and-run, local-first workflow for making product launch videos with HyperFrames. Set your brand, palette, copy, scene timings, and real product captures in `video.json`; build and preview an editable composition on your own machine.

The starter includes an eight-scene, 60-second example. It ships with abstract vector motion and clearly labeled capture slots. It contains no product-specific branding, screenshots, generated media, API keys, or paid-service dependency.

## What makes this different

This project focuses on one job: turning a product story and genuine product screenshots into an editable launch video. Its niche is a lightweight, reproducible workflow you can clone and adapt, rather than a hosted video platform or an AI video model.

- **Start with a small setup:** use Python, Node.js, and a browser. There is no required plugin bundle, external MCP server, cloud workspace, or paid video-generation API.
- **Keep the process local and low-cost:** the builder reads one `video.json` file and writes ordinary HTML scenes. Motion uses SVG/CSS and GSAP; there are no model weights to download and no inference service to pay for. The HyperFrames CLI is fetched with `npx`, and the preview loads GSAP from jsDelivr, so an internet connection is needed for those parts.
- **Keep your video editable:** the output is a HyperFrames project made from scene files, not a flattened result from a locked editor. Change the config, source, screenshots, and motion, then rebuild.
- **Show the real product:** feature shots use your own captures. Missing captures stay clearly marked as placeholders instead of being replaced by invented interface screens.

The source and assets are kept deliberately small, but final render time still depends on your machine and the browser/FFmpeg setup. Run `npx hyperframes doctor` to check local export prerequisites.

## Quick start

### Requirements

- Python 3.10 or later
- Node.js 20 or later, with npm
- Internet access the first time `npx` downloads the pinned HyperFrames CLI and for the GSAP runtime loaded from jsDelivr
- FFmpeg and the required browser tooling for local MP4 export; run `npx hyperframes doctor` to check your machine

### Build and preview

```bash
git clone https://github.com/smshozab/hyperframes-launch-video-engine.git
cd hyperframes-launch-video-engine

# Edit video.json, then generate the HyperFrames HTML composition
npm run build

# Open the local, editable Studio preview
npm run preview
```

The default preview uses sample copy and abstract motion. Feature scenes display `REAL PRODUCT CAPTURE REQUIRED` until you add screenshots. The builder never draws a fake product interface.

## Make it yours

1. Replace the sample brand, copy, palette, and font stacks in `video.json`.
2. Adjust each scene's `durationSeconds`; the scene durations must add up to `project.durationSeconds`.
3. Add genuine product screenshots at the `capture` paths in the feature scenes. Keep `assets/captures/` local; it is ignored by Git so customer data and private screens are not committed by accident.
4. Rebuild and inspect the complete preview:

   ```bash
   npm run build
   npm run check
   npm run snapshot
   npm run preview
   ```

5. Review the preview and get approval before exporting:

   ```bash
   npm run render
   ```

The MP4 is written to `renders/launch-video.mp4`, which is ignored by Git. See [the capture checklist](docs/CAPTURE-GUIDE.md) and [the low-cost workflow](docs/LOW-COST-METHODOLOGY.md) for details.

## What the builder does

- Reads `video.json` and validates scene IDs, durations, colors, capture paths, and sound-effect entries.
- Generates one HyperFrames subcomposition per scene under `compositions/scenes/` and the main timeline in `index.html`.
- Adds seek-safe entrance and orbit motion with HyperFrames' GSAP timeline runtime.
- Uses real screenshots when present; leaves a labeled placeholder when they are missing.
- Supports optional local SFX files under `assets/sfx/`. The example has no audio cues, no score, and no external media calls.

Generated HTML is output. Edit `video.json` and `scripts/build.py`, then rebuild instead of hand-editing generated scene files.

## Codex workflow (optional)

No MCP server, external connector, or paid generation service is required to use this repository. If you use Codex, the HyperFrames workflow benefits from the optional `hyperframes`, `hyperframes-studio`, `hyperframes-core`, `hyperframes-cli`, `hyperframes-creative`, `hyperframes-keyframes`, and `media-use` skills. A local Studio preview bridge can open the preview in the Codex app; it is not a build dependency. See [AGENTS.md](AGENTS.md) for the safe editing workflow.

## Links

- [HyperFrames CLI guide](https://hyperframes.app/docs/5-packages/cli)
- [HyperFrames rendering guide](https://hyperframes.app/docs/3-guides/4-rendering)
- [MIT license](LICENSE)

## Contributing

Ideas and pull requests are welcome. Please keep examples product-neutral, use only media you have the rights to use, and do not commit private app captures. See [CONTRIBUTING.md](CONTRIBUTING.md).
