# Calorie Tracker — mockup

Three mobile screens (390x844) for a calorie tracking app, drafted as a Claude
Design canvas. Not part of the CrossPet firmware — design exploration only.

| File | Screen |
|------|--------|
| `Main.dc.html` | Today — daily intake, meal filters, calorie balance card |
| `MealDetail.dc.html` | Meal detail — hero art, ingredient breakdown, macro ring |
| `Journal.dc.html` | Day journal — week strip and hour-gutter timeline |
| `canvas.json` | Artboard layout for the canvas |

Aesthetic: glassmorphic lavender/blush/sage cards, near-black floating nav,
Schibsted Grotesk display over Manrope UI text. All imagery is inline SVG
(radial-gradient spheres and a chrome tube), so nothing loads over the network.

All figures are sample data and internally consistent: the four ingredients on
the detail screen sum to 613 kcal, and 1,558 eaten + 742 remaining = the
2,300 kcal goal shown on the Today screen.
