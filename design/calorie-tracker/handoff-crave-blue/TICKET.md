# Build the Crave blue calorie-tracker UI (direction G)

**Type:** Feature · **Area:** Design → Front-end · **Size:** M
**Status:** Ready for pickup · **Assignee:** unassigned
**Branch to work from:** `claude/calorie-tracking-mockup-kz5iey`

---

## Summary

Implement three mobile screens for the calorie-tracking app in direction G
("Crave blue"): **Home**, **Crave AI chat**, and **Meal Details**. Static
high-fidelity mockups exist and are signed off as the visual target. This
ticket covers turning them into working UI.

## Context

Seven visual directions were explored against references the stakeholder
supplied. Direction G was drawn from a screenshot of an AI-assistant calorie
app and is the only direction with a **conversational surface**, which makes it
a product decision as much as a visual one — see *Open questions*.

The mockups are artboards in `design/calorie-tracker/`:

| Screen | Artboard |
|---|---|
| Home | `CraveHome.dc.html` |
| Crave AI chat | `CraveChat.dc.html` |
| Meal Details | `CraveMeal.dc.html` |

Each is a self-contained 390×844 HTML file. `SPEC.md` in this folder is the
implementation specification — tokens, component anatomy, exact measurements
and the generated-geometry formulas.

## Scope

**In scope**
- Home, Crave AI chat and Meal Details at 390×844, matching `SPEC.md`
- The radiating-bar progress gauge, nutrition ring gauges and date strip as
  reusable components driven by real values, not fixed geometry
- Five-tab bottom navigation with the raised centre action
- Responsive behaviour from 320px to 430px width

**Out of scope**
- Backend, food database, any real AI integration (chat is presentation only —
  see *Open questions*)
- Dark mode (not designed for this direction)
- Onboarding, auth, settings, any screen not listed above

## Acceptance criteria

1. The three screens render at 390×844 within 2px of the artboards for every
   measurement called out in `SPEC.md`.
2. Gauge, rings and macro bars are driven by props/data. Passing
   `{ consumed: 1250, goal: 2000 }` fills the gauge to 62.5% and prints 1250;
   no hard-coded arc lengths.
3. All five nav tabs render with labels; the active tab and the raised centre
   action match the spec.
4. No horizontal scroll and no clipped text between 320px and 430px.
5. Every interactive element has a touch target of at least 44×44px.
6. Text contrast meets WCAG AA. **Note:** `#9CA3AF` on white is 2.54:1 and
   fails — see *Known issues*.
7. Screens are keyboard navigable and controls are labelled for screen readers.

## Subtasks

- [ ] Set up tokens from `SPEC.md` §1 (colour, type, radii, spacing)
- [ ] Build shared components: `StatCard`, `MacroBar`, `RingGauge`, `DateChip`,
      `TagChip`, `BottomNav`
- [ ] Build `ArcGauge` from the formula in `SPEC.md` §4.1
- [ ] Home screen
- [ ] Meal Details screen
- [ ] Chat screen (presentation only; bubbles, result card, composer)
- [ ] Responsive pass at 320 / 375 / 390 / 430
- [ ] Accessibility pass against criteria 5–7
- [ ] Resolve the `#9CA3AF` contrast issue with the designer

## Known issues carried over from the mockups

1. **Muted text fails contrast.** `#9CA3AF` is 2.54:1 on `#FFFFFF` and 2.39:1
   on the `#F7F8FA` ground, against a 4.5:1 requirement. It is used for most secondary text. This came from the
   reference and was not corrected in the mockups. Darkening to `#6B7280`
   (4.83:1 on white) fixes it and is already the colour used for body copy — confirm
   with the designer before applying globally.
2. **Food imagery is placeholder.** The reference uses photography; the
   mockups use flat SVG plates because no photo source was available. Real
   imagery will change the visual weight of the meal cards and the detail hero.
   Decide on a source before building the detail screen.

## Open questions

1. **Is the AI chat in or out?** It is the direction's differentiator and has
   no equivalent in the other directions. Shipping it means an assistant
   backend, a food database and a cost model. If it is out, the direction
   reduces to a conventional tracker and the Home screen carries it.
2. **Where does this get built?** The only repo currently in scope is the
   CrossPet ESP32 firmware repo, which is unrelated — the mockups live there
   on a branch only because that is where the session ran. A target codebase
   and stack need naming before pickup.
3. **Do the macro colours mean anything fixed?** Purple = Carbos, cyan =
   Protein, orange = Fat is used consistently across all three screens. Confirm
   this is the product-wide convention before encoding it in tokens.

## References

- `SPEC.md` — implementation specification
- `design/calorie-tracker/README.md` — all seven directions and their origins
- Source artboards listed above
