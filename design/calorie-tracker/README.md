# Calorie Tracker — mockup

Three mobile screens (390x844) for a calorie tracking app, drafted as a Claude
Design canvas. Not part of the CrossPet firmware — design exploration only.

Directions A and B are the shortlist. Canvas page 1 holds them in light and
dark with their original illustration; page 2 holds the same two themes with
voxel art; page 3 keeps directions C, D and E for reference. Direction E
carries a fourth screen.

## Voxel art

`voxel_gen.py` renders the isometric models. Cubes use a 2:1 projection with
three face shades per base colour (top x1.16, right x0.86, left x0.64), drawn
back-to-front by `x + y + z`; fully-enclosed cubes are skipped. Models —
bowl, apple, glass and a square tray tile — are defined on a voxel grid, so
the same object stays consistent from a 44px card thumbnail up to a hero.
Palettes are keyed per direction: magenta/violet for A, Blue Ribbon and
Persimmon for B.

Voxel screens are `*Vox.dc.html` (light) and `*VoxNight.dc.html` (dark). The
voxel colours are deliberately disjoint from both dark-mode colour maps, so
the models pass through the light-to-dark remap untouched — they are self-lit
and need no dark variant.

## Direction A — "Lavender glass" (shortlisted)

| File | Screen |
|------|--------|
| `Main.dc.html` | Today — daily intake, meal filters, calorie balance card |
| `MealDetail.dc.html` | Meal detail — hero art, ingredient breakdown, macro ring |
| `Journal.dc.html` | Day journal — week strip and hour-gutter timeline |

Glassmorphic lavender/blush/sage cards, near-black floating nav, Schibsted
Grotesk display over Manrope UI text, 3D gradient-sphere imagery.

Dark: `TodayGlassNight.dc.html`, `MealDetailGlassNight.dc.html`,
`JournalGlassNight.dc.html`. Deep plum ground, glass panels dropped to 6-10%
white, borders lifted to 11%, near-black chips inverted to light, accent
raised to `#B18BE0`. The gradient spheres carry over unchanged.

## Direction B — "Trippin blue" (shortlisted)

| File | Screen |
|------|--------|
| `TodayBlue.dc.html` | Today — illustrated hero, quick-log bar, intake card |
| `MealDetailBlue.dc.html` | Meal detail — illustrated dish, info rows, ingredient list |
| `JournalBlue.dc.html` | Day journal — month calendar and result-style meal cards |

Follows the Trippin' style guide: Persimmon `#FA644C`, Midnight Blue `#162150`,
Blue Ribbon `#365DF5`, Maya Blue `#6792FF`, white cards on pale blue, blue→violet
gradient pill buttons, navy pill nav with a label on the active tab, flat vector
illustration. Type is Archivo, the closest freely-available stand-in for
Helvetica Now Display (the fallback stack is Helvetica Neue/Helvetica/Arial).

Dark: `TodayBlueNight.dc.html`, `MealDetailBlueNight.dc.html`,
`JournalBlueNight.dc.html`. Midnight Blue extended down to a `#0B111F` ground
with `#141D31` cards; Blue Ribbon and Persimmon are unchanged, the tag pills
become translucent, and the navy nav pill inverts to light.

## Direction C — "Cargo dark" (set aside)

| File | Screen |
|------|--------|
| `TodayDark.dc.html` | Today — intake card with meal stepper, macro tiles, meal cards |
| `MealDetailDark.dc.html` | Meal detail — order-style header card and nutrition card |
| `JournalDark.dc.html` | Day journal — day strip, entry rows, remaining bar |

Near-black cards (`#1A2329`) on `#10161A`, lemon-yellow accent `#EFE23C`, dotted
stepper progress, circular icon buttons, one card per screen inverted to solid
yellow with dark text. Type is Outfit. Thumbnails are flat SVG, tuned for the
dark ground.

## Direction D — "Industrial light" (set aside)

| File | Screen |
|------|--------|
| `TodayLight.dc.html` | Today — object hero, status card, 2-col meal grid |
| `MealDetailLight.dc.html` | Meal detail — object hero, macro bars, ingredient grid |
| `JournalLight.dc.html` | Day journal — day strip, progress card, entry rows |

Near-white ground `#F6F6F6` with bordered white cards, amber accent `#F7B500`,
status pills carrying a coloured bar (green logged / red planned), and
shaded 3D-style objects drawn as gradient SVG. Type pairs Instrument Serif
(all numerals and titles) with Instrument Sans (labels and UI).

## Direction E — "Playful pastel" (set aside)

| File | Screen |
|------|--------|
| `TodayPlay.dc.html` | Today — greeting, search, two colour cards, meal rows |
| `MealDetailPlay.dc.html` | Meal detail — stacked colour ingredient cards |
| `JournalPlay.dc.html` | Day journal — avatar, week bars with face markers, meal rows |
| `CheckInPlay.dc.html` | Check-in — full-bleed colour, character face, tick slider |

Black ground with the four brand pastels (`#9cacff`, `#ffcc90`, `#80d8b8`,
`#f894c4`), overlapping colour cards, white circular arrow buttons, and
hand-drawn character faces in bold black outline. Type is Poppins, as the
style guide specifies. The check-in screen is a post-meal satiety prompt —
the direction's signature screen, which the other directions have no
equivalent for.

`canvas.json` holds the page split, row layout and the direction notes.

All imagery is inline SVG, so nothing loads over the network.

All figures are sample data and internally consistent: the four ingredients on
the detail screen sum to 613 kcal, and 1,558 eaten + 742 remaining = the
2,300 kcal goal shown on the Today screen.
