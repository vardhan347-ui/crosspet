# Build the Lilac calorie-tracker UI (direction F)

**Type:** Feature · **Area:** Design → Front-end · **Size:** M
**Status:** Ready for pickup · **Assignee:** unassigned
**Branch to work from:** `claude/calorie-tracking-mockup-kz5iey`

---

## Summary

Implement three mobile screens for the calorie-tracking app in direction F
("Lilac"): **Today**, **Insights**, and **Macro detail**. Static high-fidelity
mockups exist and are the visual target. This ticket covers turning them into
working UI.

## Context

Seven visual directions were explored against references the stakeholder
supplied. Direction F was drawn from a screen recording of a calorie app. Its
distinguishing idea is a **customisable widget grid** — Insights is a board of
tiles the user arranges, and every tile drills into a detail screen. That is a
structural decision, not just a skin: see *Open questions*.

The mockups are artboards in `design/calorie-tracker/`:

| Screen | Artboard |
|---|---|
| Today | `TodayLilac.dc.html` |
| Insights | `InsightsLilac.dc.html` |
| Macro detail | `MacroLilac.dc.html` |

Each is a self-contained 390×844 HTML file. `SPEC.md` in this folder is the
implementation specification — tokens, component anatomy, exact measurements
and the generated-geometry formulas.

## Scope

**In scope**
- Today, Insights and Macro detail at 390×844, matching `SPEC.md`
- The ticked dial, date chips with progress rings, the triple-ring macro
  donut and the striped bar chart as reusable components driven by real
  values, not fixed geometry
- The four-item bottom nav
- Responsive behaviour from 320px to 430px width

**Out of scope**
- Backend, food database, any logging flow
- Dark mode (not designed for this direction)
- Widget add / remove / reorder behaviour behind "Edit" — see *Open questions*
- Onboarding, auth, settings, any screen not listed above

## Acceptance criteria

1. The three screens render at 390×844 within 2px of the artboards for every
   measurement called out in `SPEC.md`.
2. The dial, date rings, donut and bar chart are driven by props/data. Passing
   `{ consumed: 1558, goal: 2300 }` fills the dial to 68% and prints 1558; no
   hard-coded arc lengths or path data.
3. The Insights grid lays out from a list of widget descriptors, not from
   hand-placed markup. Adding a widget to the list adds a tile.
4. No horizontal scroll and no clipped text between 320px and 430px.
5. Every interactive element has a touch target of at least 44×44px. **The ↗
   tile buttons are 32px in the mockups and fail this** — see *Known issues*.
6. Text contrast meets WCAG AA — see *Known issues* for the four tokens that
   currently do not.
7. Screens are keyboard navigable and controls are labelled for screen readers.

## Subtasks

- [ ] Set up tokens from `SPEC.md` §1 (colour, type, radii, spacing)
- [ ] Build shared components: `InsightTile`, `MacroCard`, `FoodRow`,
      `DateChip`, `SegmentedControl`, `BottomNav`
- [ ] Build `TickDial` from the formula in `SPEC.md` §4.1
- [ ] Build `RingDonut` (§4.3) and `StripedBarChart` (§4.4)
- [ ] Today screen
- [ ] Insights screen with a descriptor-driven grid
- [ ] Macro detail screen
- [ ] Responsive pass at 320 / 375 / 390 / 430
- [ ] Accessibility pass against criteria 5–7
- [ ] Take the contrast and hit-target findings back to the designer

## Known issues carried over from the mockups

1. **Four muted tokens fail contrast.** Measured against their real backgrounds:

   | Token | On | Ratio | Needs | Used for |
   |---|---|---|---|---|
   | `#9D9BA8` | `#FFFFFF` | 2.73:1 | 4.5 / 3 | ⋮ row menus |
   | `#7C7A8C` | lavender ground | 3.44:1 | 4.5 | "Welcome", macro labels |
   | `#8A8796` | `#FFFFFF` | 3.51:1 | 4.5 | Weekday letters, chart day labels |
   | `#86848F` | `#FFFFFF` | 3.68:1 | 4.5 | Captions, units, sub-text |

   `#4A4857` (7.32:1 on lavender) and `#1B1B22` (17.12:1 on white) are fine.
   Darkening the four above is a design decision — raise it, do not silently
   swap them.

2. **The ↗ tile buttons are 32px.** Every Insights tile's drill-in control is
   a 32px circle, below the 44px minimum. Either grow the control or make the
   whole tile the tap target and leave the ↗ as an affordance.

3. **The Fat tile is incoherent.** It reads "89 Cal" with the caption "4 Days
   Met" — a value and a caption that do not describe the same quantity. This
   came from the reference verbatim. Needs a real spec before wiring data.

4. **Food thumbnails are placeholder SVG.** The reference uses photography.
   Real imagery changes the weight of the food rows on Today.

## Open questions

1. **What does "Edit" on Insights do?** The grid implies add / remove /
   reorder, and that drives whether tiles are a fixed layout or a persisted
   per-user arrangement. Nothing behind it is designed. Build the grid
   descriptor-driven (criterion 3) so either answer is cheap, but the
   behaviour needs design before it ships.
2. **One detail template or many?** Every tile drills in via ↗. `MacroLilac`
   is spec'd as a single reusable template parameterised by metric. Confirm
   that Weight, Streak and Balance can all use it, or scope the exceptions.
3. **What do the date-strip rings measure?** Each day chip wears a progress
   ring. Assumed to be calories against goal. Confirm before wiring.
4. **Where does this get built?** The only repo currently in scope is the
   CrossPet ESP32 firmware repo, which is unrelated — the mockups live there
   on a branch only because that is where the session ran. A target codebase
   and stack need naming before pickup.

## References

- `SPEC.md` — implementation specification
- `design/calorie-tracker/README.md` — all seven directions and their origins
- `design/calorie-tracker/handoff-crave-blue/` — the same package for
  direction G, if that direction is revived
