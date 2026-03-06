# DataPulse Brand Identity

## Primary Visual

- Main key visual: [`docs/形象.jpg`](/Users/sunyifei/DataPulse/docs/形象.jpg)
- Hero crop for README / chamber shell: [`docs/assets/datapulse-command-chamber-hero.jpg`](/Users/sunyifei/DataPulse/docs/assets/datapulse-command-chamber-hero.jpg)
- Square crop for compact brand placements: [`docs/assets/datapulse-command-chamber-square.jpg`](/Users/sunyifei/DataPulse/docs/assets/datapulse-command-chamber-square.jpg)
- Icon crop for browser/tab surfaces: [`docs/assets/datapulse-command-chamber-icon.png`](/Users/sunyifei/DataPulse/docs/assets/datapulse-command-chamber-icon.png)
- Repository-safe vector derivative: [`docs/assets/datapulse-command-chamber.svg`](/Users/sunyifei/DataPulse/docs/assets/datapulse-command-chamber.svg)
- Brand direction: steel-blue command chamber, holographic evidence globe, twin containment rings, operator consoles
- Product posture: not a generic dashboard, but a local-first intelligence operations room

## Brand Cues

- Space: enclosed command chamber, not open canvas
- Focus object: central evidence globe / truth core
- Framing device: twin red containment rings
- Materials: dark glass, steel, neon telemetry, restrained cyan overlays
- Motion bias: scanning, pulsing, containment, replay

## Palette

- `Midnight Core` `#0E1625`
- `Graphite Floor` `#050B14`
- `Signal Red` `#FF6C84`
- `Glass Cyan` `#7FE4FF`
- `Steel Line` `#93B5D7`
- `Fog Text` `#9CB1C9`
- `Cold White` `#EAF6FF`

## Usage Rules

- README, release notes, and console entry surfaces should use the command chamber visual as the primary banner.
- UI should favor dark glass panels with red alert accents and cyan telemetry, not warm paper or generic SaaS palettes.
- Headlines should sound operational: command chamber, mission board, signal operations, evidence replay.
- Decorative motion should stay sparse and purposeful.

## Regeneration

- Default rebuild command: `bash scripts/build_brand_assets.sh`
- Custom source rebuild: `bash scripts/build_brand_assets.sh /absolute/path/to/source.jpg`
- The rebuild script refreshes the wide hero, square crop, and browser icon from the canonical bitmap.

## Asset Intent

- `docs/形象.jpg` is the canonical repository bitmap for the current brand visual.
- `docs/assets/datapulse-command-chamber-hero.jpg` is the default render asset for wide hero surfaces.
- `docs/assets/datapulse-command-chamber-square.jpg` is the default compact crop for future icon/card placements.
- `docs/assets/datapulse-command-chamber-icon.png` is the default browser favicon/app icon asset.
- The SVG in `docs/assets/` remains the repository-safe derived asset for contexts that prefer vector delivery.
