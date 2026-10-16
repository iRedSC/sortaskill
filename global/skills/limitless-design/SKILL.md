---
name: limitless-design
description: Use when designing or redesigning a landing page, portfolio, personal site, launch page, or other front-facing web page. Skip in-app product UI such as dashboards, settings, and forms.
---

# Limitless design

Every agent drifts into the same handful of looks when handed the same kind of brief. This skill pulls you out of that headspace with random theme words. Treat them as a spark, not a spec.

## Ground the brief

Identify the subject, the audience, and the page's primary job. If the brief does not say what the subject is, propose one and confirm it. The subject comes first: the words bend how it is expressed, never what it is. Where the brief pins down a visual direction, follow it exactly.

## First round: five designs

Make five designs. For each one, run `python3 theme_words.py` from this skill's directory for a fresh roll. Do not pass a seed unless the user wants to reproduce a roll.

For each roll:

1. Read the five words and look for what they suggest for this subject: a material, a medium, a mechanism, a mood, a metaphor. Not every word needs to be used. One word may carry the whole design. They are purely for inspiration.
2. Name a theme: a world the whole page lives in. Choose the medium that world asks for: paper cutouts, layered collage, subtle 3D, skeuomorphism, realistic objects, or something nobody would expect. Reach for out-of-the-box ideas over safe ones; the page must feel extremely unique.
3. Let the theme own the entire page, not one element on it. Do not start from the usual landing-page outline of nav, headline, buttons, features, testimonial, pricing, and footer and then decorate it. Ask what each thing the page must say would be in this world. If the theme is a cartridge case, the page is the console: features are what the reader shows, pricing is the cartridge editions, and the headline is printed on a label.
4. Decide where the words physically live in that world before laying anything out: stamped into metal, printed on a label, scrawled in a margin, cut from paper. The layout follows from those answers, so each design's first screen should be shaped by its theme.
5. Choose a focal point: the place a visitor enters the world. Spend boldness there and keep the rest disciplined, so the page reads as one tight, clean thing.

Each design is its own direction. Do not let one design soften toward the others.

## Materials are all or nothing

A material named in the theme must read as that material on screen, not only in your description. Mercury needs mirror reflections, glass needs refraction and highlights, stone needs texture and weight. Render it convincingly, with one consistent light source, real shadows, and texture, or stylize it deliberately as flat graphics. Never ship the half-real middle: a gray circle labeled mercury is worse than an honest flat drawing.

Typography carries personality. Choose typefaces for this theme, not the families you reach for on every project. Write real copy in plain words; a button says exactly what happens when it is used.

## Motion is all or nothing

Prefer interaction the visitor drives: things that respond to the pointer, dragging, clicking, and typing, and that change the world rather than decorate it. Movement should feel three-dimensional and alive.

Commit to motion only when you have an extremely confident idea of how the entire page moves as one unified thing. If the theme offers no such idea, skip motion entirely and make each piece straightforward and solid. Never add unrelated animations to fill a budget.

Motion tied to scrolling is the easiest to get wrong, because one screenshot cannot show it. Use it only when the theme demands it, and before keeping it, screenshot at least five scroll positions or record the page scrolling, and judge the motion as a sequence.

When you commit, keep it working for everyone: respect `prefers-reduced-motion`, give touch screens an equivalent with no pointer to follow, animate transforms and opacity so it stays smooth, and keep keyboard focus visible.

## Review the round

Put each design in its own directory, such as `designs/<n>-<slug>/index.html`, or follow the project's routing if it already has a framework. Copy [viewer.html](viewer.html) to `designs/index.html` and fill in its `DESIGNS` list. Start a static server in the background, such as `python3 -m http.server` from `designs/`, or use the project's own dev server, and give the user the URL. The viewer switches designs with the arrow keys and shows each design's words, theme, and focal point.

After all five are built, and not before, review them:

1. Save screenshots of each design: full pages at desktop and mobile widths, the first screen alone, and zoomed-in crops of the focal point and each interaction state.
2. You know what you meant to build, so you will see it in your own screenshots. Have a fresh reviewer judge what is actually there: spawn a subagent that can read images and give it only the brief, each design's theme name, the screenshot paths, and [review.md](review.md). Never give it your descriptions of the designs. If your harness has no subagents, describe each screenshot literally before recalling what you intended, and review against that description.
3. Fix everything the review finds, then check the fixes yourself against [review.md](review.md). One fresh review per round is enough.

## Later rounds

After the first round, iterate on the design the user chose. Make five new designs only when the user explicitly asks for them, with fresh rolls.
