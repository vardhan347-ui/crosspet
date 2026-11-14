# Calorie Tracker — mockup

Three mobile screens (390x844) for a calorie tracking app, drafted as a Claude
Design canvas. Not part of the CrossPet firmware — design exploration only.

Directions G and F are drawn from references the user supplied and sit on
canvas pages 1 and 2. Directions A and B are the earlier shortlist, each in light and
dark, on page 2. Directions C, D and E are kept for reference on page 3.
Direction E carries a fourth screen.

## Direction G — "Crave blue"

| File | Screen |
|------|--------|
| `CraveHome.dc.html` | Home — radiating bar gauge, macro bars, meal cards |
| `CraveChat.dc.html` | Crave AI — chat with an inline meal result card |
| `CraveMeal.dc.html` | Meal details — photo, tags, ring gauges, servings stepper |

White cards on `#F7F8FA`, accent `#2563EB`, Urbanist. Macro colours are purple
(Carbos), cyan (Protein) and orange (Fat). Signature elements: a semicircular
speedometer built from 34 radiating rounded bars with a blue gradient across
the filled portion, a five-tab labelled nav with a raised centre action, an AI
chat surface with an inline meal card, and four ring gauges on the detail
screen. Gauge bars, date chips and rings are generated geometry.

The chat screen has no equivalent in any other direction.

## Direction F — "Lilac"

| File | Screen |
|------|--------|
| `TodayLilac.dc.html` | Today — ticked dial, date chips, macro cards, meal list |
| `InsightsLilac.dc.html` | Insights — widget grid with triple-ring macro donut |
| `MacroLilac.dc.html` | Macro detail — segmented range, striped bar chart, stat rows |

Lavender ground (`#DED7F1` to `#F4F3F8`) with white cards, accent `#6C4EE8`,
black selected pill, Plus Jakarta Sans. Signature elements lifted from the
reference: a large ticked gauge arc (the leading 68% of ticks carries the
accent), date chips wrapped in progress rings, widget cards each with a
circular arrow button, a three-ring macro donut, and a bar chart of striped
rounded bars with one solid selected bar and a dotted centre line.

Dial ticks and chart bars are generated geometry, embedded in the artboards.
Food thumbnails are flat SVG rather than the reference's photography.

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
