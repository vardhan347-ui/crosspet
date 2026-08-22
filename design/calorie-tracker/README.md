# Calorie Tracker — mockup

Three mobile screens (390x844) for a calorie tracking app, drafted as a Claude
Design canvas. Not part of the CrossPet firmware — design exploration only.

Two visual directions of the same three screens, on two canvas pages.

## Direction A — "Lavender glass" (page 1)

| File | Screen |
|------|--------|
| `Main.dc.html` | Today — daily intake, meal filters, calorie balance card |
| `MealDetail.dc.html` | Meal detail — hero art, ingredient breakdown, macro ring |
| `Journal.dc.html` | Day journal — week strip and hour-gutter timeline |

Glassmorphic lavender/blush/sage cards, near-black floating nav, Schibsted
Grotesk display over Manrope UI text, 3D gradient-sphere imagery.

## Direction B — "Trippin blue" (page 2)

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

`canvas.json` holds the page split and artboard layout for both.

All imagery is inline SVG, so nothing loads over the network.

All figures are sample data and internally consistent: the four ingredients on
the detail screen sum to 613 kcal, and 1,558 eaten + 742 remaining = the
2,300 kcal goal shown on the Today screen.
