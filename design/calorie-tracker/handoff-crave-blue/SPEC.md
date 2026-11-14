# Direction G — "Crave blue" implementation spec

Everything below is measured from the three artboards, not from the original
reference. Where the spec and the artboards disagree, the artboards win.

## Start here

1. Open the three artboards in a browser to see the target:
   `design/calorie-tracker/CraveHome.dc.html`, `CraveChat.dc.html`,
   `CraveMeal.dc.html`. They are plain HTML — the `<script src="./support.js">`
   line and the `{{accent}}` placeholders belong to the design-canvas runtime.
   To view one standalone, delete the `<helmet>` wrapper, move its `<style>`
   and font `<link>` into `<head>`, and replace `{{accent}}` with `#2563EB`.
2. Read `TICKET.md` in this folder for scope, acceptance criteria and the three
   open questions. **Question 2 — which codebase this gets built in — is not
   answered. Do not start writing app code until it is.**
3. Treat the two *Known issues* in the ticket as decisions to raise, not
   defects to silently fix.

---

## 1. Tokens

### Colour

| Token | Value | Use |
|---|---|---|
| `--accent` | `#2563EB` | Primary action, active nav, links, selected date, user bubble |
| `--ink` | `#111827` | Headings, values, primary text |
| `--body` | `#6B7280` | Body copy, descriptions |
| `--muted` | `#9CA3AF` | Labels, timestamps, units, inactive nav — **see contrast issue** |
| `--muted-strong` | `#4B5563` | Chip text, outline button labels |
| `--surface` | `#FFFFFF` | Cards, bars, nav |
| `--ground` | `#F7F8FA` | Home screen background (chat and detail are white) |
| `--fill` | `#F3F4F6` | Icon buttons, tag chips |
| `--track` | `#EEF0F4` | Macro bar track |
| `--ring-track` | `#F0F2F6` | Nutrition ring track |
| `--gauge-empty` | `#DCE3F2` | Unfilled gauge bars |
| `--hairline` | `#ECEEF2` | Card borders, stat box borders |
| `--hairline-2` | `#E8EAEF` | Chip and composer borders |
| `--alert` | `#EF4444` | Notification dot |

Macro colours are fixed and consistent across all three screens:

| Macro | Value |
|---|---|
| Carbos | `#7C5CE0` |
| Protein | `#22B8D9` |
| Fat | `#F59E42` |

### Typography

**Urbanist**, weights 400/500/600/700/800. Fallback stack:
`'Urbanist', 'Helvetica Neue', Helvetica, Arial, sans-serif`.

| Role | Size | Weight | Tracking |
|---|---|---|---|
| Gauge value | 34px | 700 | −0.03em |
| Price | 22px | 700 | −0.02em |
| Screen title (detail) | 20px | 700 | −0.02em |
| Greeting | 20px | 700 | −0.015em |
| Meal kcal | 20px | 700 | −0.02em |
| Nav bar title | 17px | 700 | −0.015em |
| Section heading | 16.5px | 700 | −0.015em |
| Card title | 14.5px | 700 | — |
| Stat value | 15px | 700 | — |
| Body / description | 13px | 500 | — |
| Bubble text | 13px | 500 | line-height 1.45 |
| Label / caption | 12.5px | 500 | — |
| Meta, unit, timestamp | 11–11.5px | 500 | — |
| Stat box label | 10.5px | 500 | — |

### Radii

20px is the workhorse (cards, date chips, photos, pills). Also in use: 28px
(composer, primary button), 22px (progress card), 18px (chat bubble, servings
row), 17/15px (small pills, tags), 14px (card photo), 12px (stat box).

A chat bubble's tail corner drops to **6px** — bottom-left for assistant,
bottom-right for user.

### Spacing

Screen gutter 20px. Card padding 16px (10px on compact meal cards). Vertical
rhythm between blocks 12–16px.

---

## 2. Shared components

| Component | Props | Notes |
|---|---|---|
| `ArcGauge` | `consumed`, `goal` | §4.1 |
| `RingGauge` | `value`, `pct`, `label`, `colour` | §4.2 |
| `MacroBar` | `value`, `goal`, `label`, `colour` | Track 5px, radius 3px, width = value/goal |
| `DateChip` | `day`, `weekday`, `selected` | 58px tall, radius 20px, 7 across, gap 6px |
| `StatBox` | `value`, `label` | 54px tall, radius 12px, 1px `--hairline` border |
| `TagChip` | `label` | 30px tall, radius 15px, `--fill` |
| `BottomNav` | `active` | §3.1 |

---

## 3. Screens

### 3.1 Home (`CraveHome.dc.html`)

Background `--ground`. Top to bottom:

1. **Header**, padding `22px 20px 0`. 48px avatar · greeting block
   (20/700 name, 12.5/500 `--muted` subtitle) · 44px bell button with an 8px
   `--alert` dot at top-right · 44px settings button. Both buttons `--surface`.
2. **Date strip**, 16px below. 7 chips, `flex: 1 1 0`, gap 6px. Unselected:
   `--surface`, 15/600 `--ink` day over 11/500 `--muted` weekday. Selected:
   `--accent`, white day, `rgba(255,255,255,0.8)` weekday.
3. **Daily Progress card**, 14px below, `--surface`, radius 22px, padding 16px.
   - Header row: "Daily Progress" 16.5/700 · value 15/700 · "/ 2000 cal"
     12.5/500 `--muted`, baseline-aligned.
   - Gauge block 172px tall (§4.1). Flame at y=56, value at y=78,
     "Calories" at y=118, "0%" / "100%" at y=150 flush to the edges.
   - Macro row 14px below: three equal columns, each `value / goal` on one
     line, a `MacroBar`, then the label. All centred.
4. **Section header** "Today's Meals" 16.5/700 with "See all" 13/600 `--accent`.
5. **Meal cards**, two columns, gap 12px, padding 10px. 112px photo at radius
   14px, then name 14.5/700 with time 11/500 `--muted` right, then kcal 20/700
   with "Kcal" 11.5/500 and a ⋯ affordance.
6. **Bottom nav**, fixed, 88px tall, `--surface`, shadow
   `0 -4px 20px rgba(17,24,39,0.06)`, padding-top 14px. Five 62px slots:
   Home · My Meals · *centre* · Progress · Profile. Icons 22px, labels 11.5px;
   active is `--accent` at 600, inactive `--muted` at 500. The centre slot
   holds a 50px `--accent` circle pulled up 6px with shadow
   `0 6px 16px rgba(37,99,235,0.35)` and a white sparkle.

### 3.2 Crave AI chat (`CraveChat.dc.html`)

Background white.

1. **Header**: 40px back button (`--fill`) · centred title block (17/700 +
   11.5/500 `--muted`) · 40px menu button.
2. **Messages**, gutter 20px, 12px apart. Max bubble width 248px, padding
   `11px 14px`.
   - Assistant: 30px `--accent` avatar with white sparkle, then a white bubble
     with shadow `0 3px 14px rgba(17,24,39,0.09)`, tail corner 6px. Inline
     `<strong>` at 700 for suggested phrasings.
   - User: right-aligned `--accent` bubble, white text, tail corner 6px, 30px
     avatar on the right. Timestamp 10/500 at 0.75 opacity, right-aligned
     inside the bubble.
   - Assistant timestamps are 10/500 `--muted` on their own line.
3. **Meal result card**, inset to align with the assistant bubble
   (`margin-left: 59px`), padding 10px, radius 20px, shadow
   `0 4px 18px rgba(17,24,39,0.10)`. 120px photo · name 14/700 with price
   15/700 right · meta row (clock, servings) 11.5/500 `--muted` · three
   `StatBox` · two buttons, each `flex: 1`, 40px tall, radius 20px:
   "Alternatives" outlined `--hairline-2` with `--muted-strong` label,
   "Customize meal" solid `--accent` white label.
4. **Suggestion chips**, 32px tall, radius 16px, 1px `--hairline-2` border,
   12/500 `--muted-strong`. Horizontally scrollable, clipped at the right edge.
5. **Composer**, pinned 26px from the bottom. 56px tall, radius 28px, 1px
   `--hairline-2`. 36px `+` button (`--fill`) · placeholder 13.5/500 `--muted`
   · 40px `--accent` send button.

### 3.3 Meal Details (`CraveMeal.dc.html`)

Background white.

1. **Header**: back · centred "Meal Details" 17/700 · menu.
2. **Photo** 200px tall, radius 20px, full width inside the gutter.
3. **Title** 20/700, line-height 1.25, wraps to two lines.
4. **Meta row**: clock + duration, servings icon + count, 12.5/500 `--muted`.
5. **Price row**: 22/700 left; "Add Location" pill right — 34px tall, radius
   17px, background `#F4F7FF`, border `#C7D7FB`, 12.5/600 `--accent` label.
6. **Description** 13/500 `--body`, line-height 1.5, `text-wrap: pretty`.
7. **Tag chips**, three, gap 8px.
8. **"Nutrition Breakdown"** 16.5/700 with a chevron (collapsible).
9. **Ring row**: four `RingGauge`, equal width, gap 10px.
10. **Servings row**: 18px above the button. Radius 18px, 1px `--hairline`
    border. Label block left, then a 34px `−` button (`--fill`), the count
    15/700, and a 34px `+` button (`--accent`, white glyph).
11. **Primary button**, pinned 28px from the bottom. 56px tall, radius 28px,
    `--accent`, 15/700 white, shadow `0 8px 22px rgba(37,99,235,0.3)`.

---

## 4. Generated geometry

Both of these are computed, not drawn. Reimplement from the formulas; do not
copy the path data out of the artboards.

### 4.1 ArcGauge

A 180° sweep of discrete rounded bars, drawn clockwise from the left.

```
viewBox      318 × 172
centre       (159, 140)
inner radius 92
outer radius 122
bars         34
stroke       7px, round caps
```

For bar `i` in `0..33`:

```
theta = 180° + (i + 0.5) × (180 / 34)
inner = (cx + 92·cos θ,  cy + 92·sin θ)
outer = (cx + 122·cos θ, cy + 122·sin θ)
```

Fill rule — with `pct = consumed / goal` and `frac = i / 33`:

- `i < pct × 34` → lerp `#A8C2F2 → #1D4ED8` by `frac`, channel-wise in sRGB
- otherwise → `--gauge-empty`

At 1250/2000 that is 22 filled bars. The gradient runs across the **whole**
bar index, not just the filled span, so the filled run always ends mid-ramp —
this is intentional and matches the reference.

### 4.2 RingGauge

```
viewBox 66 × 66,  r = 26,  stroke 6px, round cap
circumference = 2π × 26 = 163.36
track  --ring-track
arc    stroke-dasharray = "{163.36 × pct} 163.36", transform="rotate(-90 33 33)"
```

Value sits centred at 13/700; label 7px below at 11.5/500 `--body`.

Mockup values: Calories 450g/0.72 `--accent` · Protein 44g/0.55 `#22B8D9` ·
Carbs 60g/0.64 `#7C5CE0` · Fats 18g/0.38 `#F59E42`.

> The reference labels the first ring "Calories" but gives it a gram unit.
> That inconsistency was carried over verbatim. Fix it when wiring real data.

---

## 5. Assets

All imagery in the artboards is **inline SVG placeholder**, not final:

- Three plate illustrations (salmon, breakfast, lunch) and one detail hero
- Two avatar illustrations (header, chat)

Replace with real photography or a commissioned illustration set. See the
ticket's *Known issues* #2 — this changes the visual weight of the meal cards
and the detail hero, so settle it before building those.

## 6. Not designed yet

Anything here needs design input before it can be built:

- Dark mode
- Empty states (no meals logged, no chat history)
- Loading and skeleton states, including the assistant's "thinking" state
- Error states — failed send, no network, food not found
- Scroll behaviour: does the header collapse? does the date strip stick?
- Long content: names over two lines, four-digit kcal, 10+ chat turns
- Any screen behind the four non-active nav tabs
- Localisation, including right-to-left
