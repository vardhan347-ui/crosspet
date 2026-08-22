# Calorie Tracker — mockup

Three mobile screens (390x844) for a calorie tracking app, drafted as a Claude
Design canvas. Not part of the CrossPet firmware — design exploration only.

Four visual directions of the same three screens, laid out as four rows
on one canvas.

## Direction A — "Lavender glass"

| File | Screen |
|------|--------|
| `Main.dc.html` | Today — daily intake, meal filters, calorie balance card |
| `MealDetail.dc.html` | Meal detail — hero art, ingredient breakdown, macro ring |
| `Journal.dc.html` | Day journal — week strip and hour-gutter timeline |

Glassmorphic lavender/blush/sage cards, near-black floating nav, Schibsted
Grotesk display over Manrope UI text, 3D gradient-sphere imagery.

## Direction B — "Trippin blue"

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

## Direction C — "Cargo dark"

| File | Screen |
|------|--------|
| `TodayDark.dc.html` | Today — intake card with meal stepper, macro tiles, meal cards |
| `MealDetailDark.dc.html` | Meal detail — order-style header card and nutrition card |
| `JournalDark.dc.html` | Day journal — day strip, entry rows, remaining bar |

Near-black cards (`#1A2329`) on `#10161A`, lemon-yellow accent `#EFE23C`, dotted
stepper progress, circular icon buttons, one card per screen inverted to solid
yellow with dark text. Type is Outfit. Thumbnails are flat SVG, tuned for the
dark ground.

## Direction D — "Industrial light"

| File | Screen |
|------|--------|
| `TodayLight.dc.html` | Today — object hero, status card, 2-col meal grid |
| `MealDetailLight.dc.html` | Meal detail — object hero, macro bars, ingredient grid |
| `JournalLight.dc.html` | Day journal — day strip, progress card, entry rows |

Near-white ground `#F6F6F6` with bordered white cards, amber accent `#F7B500`,
status pills carrying a coloured bar (green logged / red planned), and
shaded 3D-style objects drawn as gradient SVG. Type pairs Instrument Serif
(all numerals and titles) with Instrument Sans (labels and UI).

`canvas.json` holds the row layout and the direction notes.

All imagery is inline SVG, so nothing loads over the network.

All figures are sample data and internally consistent: the four ingredients on
the detail screen sum to 613 kcal, and 1,558 eaten + 742 remaining = the
2,300 kcal goal shown on the Today screen.
