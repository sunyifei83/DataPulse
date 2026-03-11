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

## Console Visual System

- Topbar and dock form one sticky control rail: section jumps, saved-view context, command palette, reset, and language switch all live in the same visual band.
- Panels, cards, and tool clusters should read as one family of dark-glass surfaces with clear depth steps instead of flat admin-dashboard tiles.
- Chips and compact toolbars carry mode, filter, and quick-action state; primary actions should stand out without turning every control into a CTA.
- Empty states should keep the same framed shell and muted operational copy so missing data still feels intentional and navigable.
- Danger actions reserve `Signal Red` fills and should appear only on destructive moves such as route, triage, or story deletion.
- Bilingual console surfaces should switch to the Chinese type stack for labels, chips, and headings instead of inheriting condensed Latin styling unchanged.

## Responsive Interaction Contract

- Desktop `> 1100px`: comfortable density, split-pane work surfaces, side-panel utilities, and inline secondary actions remain the default operating posture.
- Compact `761px - 1100px`: compact density, stacked panes, and sheet-style utilities keep the same lifecycle order while reducing scroll churn and chrome weight.
- Touch `<= 760px`: touch density, one dominant pane at a time, full-screen context/palette utilities, and action-sheet fallback for secondary or danger controls.
- The command-chamber visual language survives every breakpoint, but hero treatment must yield to current-object facts, the active rail, and the primary CTA on smaller screens.

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
