# Direction F — "Lilac" implementation spec

Everything below is measured from the three artboards, not from the original
reference. Where the spec and the artboards disagree, the artboards win.

## Start here

1. Open the three artboards in a browser to see the target:
   `design/calorie-tracker/TodayLilac.dc.html`, `InsightsLilac.dc.html`,
   `MacroLilac.dc.html`. They are plain HTML — the
   `<script src="./support.js">` line and the `{{accent}}` placeholders belong
   to the design-canvas runtime. To view one standalone, delete the `<helmet>`
   wrapper, move its `<style>` and font `<link>` into `<head>`, and replace
   `{{accent}}` with `#6C4EE8`.
2. Read `TICKET.md` for scope, acceptance criteria and four open questions.
   **Question 4 — which codebase this gets built in — is not answered. Do not
   start writing app code until it is.**
3. The four *Known issues* in the ticket are decisions to raise, not defects
   to silently fix.

---

## 1. Tokens

### Colour

| Token | Value | Use |
|---|---|---|
| `--accent` | `#6C4EE8` | Progress, selected day in calendar, links, tile icons, selected bar |
| `--ink` | `#1B1B22` | Headings, values, primary text |
| `--pill` | `#15151A` | Selected date chip, selected segment — near-black, not the accent |
| `--on-pill` | `#FFFFFF` | Text on `--pill` |
| `--day-ink` | `#4A4857` | Unselected date-chip numbers |
| `--muted` | `#86848F` | Captions, units, sub-text |
| `--muted-2` | `#8A8796` | Weekday letters, chart day labels |
| `--muted-3` | `#7C7A8C` | "Welcome", macro card labels |
| `--muted-4` | `#9D9BA8` | ⋮ row menus |
| `--surface` | `#FFFFFF` | Cards, tiles |
| `--fill` | `#F2F1F7` | ↗ tile button background |
| `--track` | `#F0EEF6` | Donut ring track |
| `--grid` | `#EFEDF5` | Chart gridlines |
| `--tick-off` | `#D5D1E3` | Unfilled dial ticks |

Four tokens fail contrast. See the ticket's *Known issues* #1 before using
them — the table there gives measured ratios against real backgrounds.

**Backgrounds.** All three screens use a four-stop vertical lavender gradient,
tuned per screen:

```
Today        linear-gradient(180deg, #DED7F1 0%, #E7E3F4 20%, #F1F0F6 44%, #F4F3F8 100%)
Insights     linear-gradient(180deg, #E2DCF3 0%, #EAE7F5 30%, #F1F0F6 60%, #F4F3F8 100%)
Macro detail linear-gradient(180deg, #DED7F1 0%, #E8E4F4 22%, #F1F0F6 50%, #F4F3F8 100%)
```

**Accent family** — used on macro icons, donut rings, chart bars and tile
glyphs:

| Role | Value |
|---|---|
| Carbs / primary | `#6C4EE8` |
| Fat / streak | `#F0552B` |
| Protein / balance | `#2EA8E8` |
| Protein chip | `#F05B9E` |
| Fiber / positive delta | `#2CB67D` |
| Chart bar (unselected) | `#AEDDF4` with `#CDEAF9` stripe |

Icon chip tints on Today's macro cards: Carbs `#EDE8FD`, Fat `#DCF1FC`,
Protein `#FDE3F0`.

### Typography

**Plus Jakarta Sans**, weights 400/500/600/700/800. Fallback stack:
`'Plus Jakarta Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif`.

| Role | Size | Weight | Tracking |
|---|---|---|---|
| Dial value | 44px | 700 | −0.035em |
| Summary value (detail) | 30px | 700 | −0.035em |
| Screen title (Insights) | 26px | 700 | −0.03em |
| Chart stat value | 31px | 700 | — |
| Tile value | 24px | 700 | −0.03em |
| Macro card value | 22px | 700 | −0.03em |
| Greeting name | 19px | 700 | −0.02em |
| Section / tile label | 16–16.5px | 700 | −0.015em |
| Meal group title | 15.5px | 700 | −0.015em |
| Food row title | 14.5px | 700 | −0.01em |
| Segment label | 14px | 500/700 | — |
| Caption, meta | 12–12.5px | 500 | — |
| Unit, weekday, tile caption | 11–11.5px | 500 | — |

### Radii

20–25px dominates. Cards and food rows 20px, tiles and meal cards 22px, the
chart card 24px, date chips 21px (full round on a 42px circle), nav 33px,
segments 21px, tag/icon chips 13–17px.

### Spacing

Screen gutter 20px (18px on the date strip). Card padding 14–18px. Vertical
rhythm between blocks 10–18px.

---

## 2. Shared components

| Component | Props | Notes |
|---|---|---|
| `TickDial` | `consumed`, `goal` | §4.1 |
| `DateChip` | `day`, `weekday`, `pct`, `selected` | §4.2 |
| `RingDonut` | three `{value, pct, colour}` | §4.3 |
| `StripedBarChart` | `series`, `selectedIndex` | §4.4 |
| `InsightTile` | `icon`, `label`, `value`, `caption` | 118px tall, radius 22px, padding 14px, ↗ at top-right |
| `MacroCard` | `label`, `value`, `goal`, `tint`, `icon` | 96px tall, radius 20px, padding 14px |
| `FoodRow` | `thumb`, `title`, `meta` | 72px tall, radius 20px, 46px round thumb |
| `SegmentedControl` | `options`, `selected` | 42px tall, radius 21px, selected = `--pill` |

---

## 3. Screens

### 3.1 Today (`TodayLilac.dc.html`)

1. **Header**, padding `24px 20px 0`. "Welcome" 12.5/500 `--muted-3` over the
   name 19/700. 44px bell button at `rgba(255,255,255,0.72)`.
2. **Date strip**, 18px below, gutter 18px, `space-between`. Seven
   `DateChip` (§4.2).
3. **Dial block**, 4px below, 220px tall (§4.1). Value at y=100, "of 2,300
   kcal" 13.5/500 `--muted` at y=152, wave at y=174.
   - **Wave**: a 250×46 SVG at `left: 70px`. One smooth path, stroke 6px round,
     filled with a horizontal gradient whose stops are
     `0 → transparent, 22% → accent, 78% → accent, 100% → transparent`, so it
     fades at both ends. A 7px accent dot sits at the midpoint (125, 20).
   - Below the block, "742" 15/700 + " kcal left" 12/500 `--muted`, centred.
4. **Macro cards**, 10px below, three equal columns, gap 10px. Label
   12.5/500 `--muted-3` left with a 28px tinted icon chip right; value 22/700
   with the goal as 11.5/500 `--muted` on the same line.
5. **Meal group row**: 62px, radius 20px, "Breakfast" 15.5/700 over
   "8:00 AM · 412 kcal" 12/500 `--muted`, chevron right.
6. **Food rows**, three, gap 10px (§2), starting at y=584. The third starts at
   y=748, so only 8px of it clears the nav — the list is meant to read as
   continuing under the bar, not as a third readable row.
7. **Bottom nav**, 66px tall, radius 33px, inset 20px, 22px from the bottom
   (top edge at y=756).
   `rgba(240,239,244,0.86)` with `backdrop-filter: blur(16px)` and shadow
   `0 10px 30px rgba(40,30,80,0.10)`. Four slots: active is a 50px `--pill`
   circle with a white glyph; two `#8B8996` glyphs; the last is a 50px
   `--accent` circle holding a 26px white circle with an accent `+`.

### 3.2 Insights (`InsightsLilac.dc.html`)

1. **Header**: "Insights" 26/700 with an "Edit" pill right — 34px tall,
   radius 17px, `--surface`, 13/600.
2. **Tile grid**, gutter 20px, gap 12px, two columns. Order: Streak · Weight,
   then the full-width Macros tile, then Calories · Balance, Carbs · Fat,
   Protein · Fiber. The last pair is clipped by the nav.
   - **Tile**: 118px, radius 22px, padding 14px. An 18px coloured glyph and a
     14.5/700 label on one row; value 24/700 at 14px below; caption 11.5/500
     `--muted`. A 32px ↗ button at `top: 12px; right: 12px`, background
     `--fill`, 14px `--muted` arrow. *See ticket Known issue #2 — this control
     is under the 44px minimum.*
   - **Macros tile**: 170px tall, full width. Left column: label row,
     "Daily Averages" 11.5/500 `--muted`, then three rows of an 8px colour dot
     + value 16/700 + percentage 11.5/600 `--muted`. A 118px `RingDonut`
     (§4.3) sits at `right: 16px; bottom: 16px`.
3. **Bottom nav** as Today, with the second slot active.

### 3.3 Macro detail (`MacroLilac.dc.html`)

Spec'd as **one reusable template** parameterised by metric — see ticket open
question 2.

1. **Header**: 44px back button · spacer · 44px share · 44px overflow, all
   `rgba(255,255,255,0.72)`.
2. **Segmented control**, 20px below. Three equal pills, 42px, radius 21px.
   Selected `--pill` with white 14/700; unselected `--surface` with
   `--day-ink` 14/500.
3. **Summary card**, 12px below. `rgba(255,255,255,0.55)`, radius 20px,
   padding `16px 18px`. Left: "Carbs · Daily Average" 12/500 `--muted-3`, then
   the value 30/700 beside a delta — a 12px arrow glyph and percentage,
   13/600, in `#2CB67D` for a fall. Right, baseline-aligned: the range
   12.5/500 `--muted-3`.
4. **Chart card**, 14px below. `--surface`, radius 24px, padding
   `18px 10px 12px`. Holds `StripedBarChart` (§4.4).
5. **Stat rows**, 14px below, four rows, gap 10px. Each 64px, radius 20px,
   `--surface`, padding `0 18px`: key 14/500 `#6E6C7B` left, value 15.5/700
   right.

No bottom nav on this screen — it is a pushed detail view.

---

## 4. Generated geometry

All four of these are computed. Reimplement from the formulas; do not copy
path data or dash arrays out of the artboards.

### 4.1 TickDial

A shallow arc of radial tick marks across the top of a large circle whose
centre sits far below the visible area.

```
viewBox      390 × 220
centre       (195, 420)      ← below the frame
inner radius 334
outer radius 356
sweep        230° → 310°, step 1.9°   (43 ticks)
stroke       2.6px, round caps
```

For each angle θ:

```
inner = (cx + 334·cos θ, cy + 334·sin θ)
outer = (cx + 356·cos θ, cy + 356·sin θ)
```

The first `round(43 × consumed/goal)` ticks take `--accent`; the rest take
`--tick-off`. At 1558/2300 that is 68% — 29 accent ticks.

The large radius is load-bearing. It puts the outer apex at y=64 and the inner
edge at y=86 directly above the value, rising to y≈91 at the value's left
edge — just clear of the 44px value sitting at y=100. Shrinking the radius
re-introduces a collision; an earlier build at r=342 had the ticks running
through the digits.

### 4.2 DateChip

42px circle, weekday letter 5px below.

- **Unselected**: an SVG ring at `r=19`, `stroke-width 2.6`. Track
  `rgba(255,255,255,0.9)`; progress `--accent`, round cap,
  `stroke-dasharray = "{119.38 × pct} 119.38"`, `transform="rotate(-90 21 21)"`
  (circumference = 2π × 19 = 119.38). Number 14/600 `--day-ink` centred over it.
- **Selected**: no ring. Solid `--pill` circle, number 14/700 `--on-pill`,
  weekday letter 11/700 `--ink`.

### 4.3 RingDonut

Three concentric arcs, all `stroke-width: 9`, round caps, track `--track`,
`transform="rotate(-90 59 59)"` on a 118×118 viewBox centred at (59, 59).

| Ring | r | Circumference | Mockup pct | Colour |
|---|---|---|---|---|
| Outer | 50 | 314.16 | 40% | `--accent` |
| Middle | 38 | 238.76 | 30% | `#F0552B` |
| Inner | 26 | 163.36 | 30% | `#2EA8E8` |

`stroke-dasharray = "{C × pct} {C}"`.

### 4.4 StripedBarChart

```
viewBox   330 × 236
baseline  y = 206
bars      7, width 28, rx 14, centres at x = 29 + i·45.5
gridlines y = 56, 94, 132, 170, 206 — #EFEDF5, 1.4px, dasharray "3 5"
day labels y = 232, 12.5px
```

**Unselected bars** fill with a pattern:

```
<pattern id="stB" width="7" height="7" patternUnits="userSpaceOnUse"
         patternTransform="rotate(58)">
  <rect width="7"   height="7" fill="#AEDDF4"/>
  <rect width="3.1" height="7" fill="#CDEAF9"/>
</pattern>
```

**Selected bar** is solid `--accent`, plus a dotted white centre line
(`stroke-width 1.6`, `dasharray "2 5"`, round cap, `opacity 0.85`) inset 12px
from both the bar's top and the baseline, and a value label 12.5/700
`--accent` centred 12px above the bar.

Day label for the selected index is 12.5/700 `--accent`; the rest are
12.5/500 `--muted-2`.

Mockup heights, Mon→Sun: `122, 128, 150, 52, 110, 84, 96` with index 2
selected. Scale real values so the tallest bar plus its 12px label clears the
viewBox top — the first build of this chart overflowed and lost the label.

---

## 5. Assets

All imagery in the artboards is **inline SVG placeholder**, not final: three
food thumbnails on Today (oats, yogurt, blueberries) drawn as flat shapes in
46px circles. Replace with real photography or a commissioned set. See the
ticket's *Known issues* #4.

## 6. Not designed yet

Anything here needs design input before it can be built:

- Dark mode
- Everything behind the Insights "Edit" affordance (ticket open question 1)
- Detail templates for the non-macro tiles — Weight, Streak, Balance
  (open question 2)
- Empty states: no meals logged, a day with no data, a new user with no
  history to chart
- Loading and skeleton states
- Error states
- Scroll behaviour: does the dial collapse on scroll? does the date strip stick?
- Long content: food names over two lines, five-digit values, 8+ food rows
- Month and Year ranges on the macro detail — only Week is designed
- Localisation, including right-to-left
