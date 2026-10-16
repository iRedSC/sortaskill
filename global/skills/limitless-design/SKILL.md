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
2. Name a theme and a single focal point that come from that reading.
3. Choose the medium the theme asks for: paper cutouts, layered collage, subtle 3D, skeuomorphism, realistic objects, or something nobody would expect. Reach for out-of-the-box ideas over safe ones; the page must feel extremely unique.
4. Wrap everything into a tight, clean page around the focal point. Spend boldness in one place and keep everything around it quiet and disciplined.

Each design is its own direction. Do not let one design soften toward the others.

Typography carries personality. Choose typefaces for this theme, not the families you reach for on every project. Write real copy in plain words; a button says exactly what happens when it is used.

## Motion is all or nothing

Motion here means scroll craft: elements that travel through depth, images cut apart and moving as pieces, a scene that responds to scrolling, pointer movement, and interaction as one living system. It should feel three-dimensional and alive over time.

Commit to motion only when you have an extremely confident idea of how the entire page moves as one unified thing. If the theme offers no such idea, skip motion entirely and make each piece straightforward and solid. Never add unrelated animations to fill a budget. Fade-and-slide-up sections, hover lifts on every card, and parallax for its own sake are the cringe this rules out.

When you commit, keep it working for everyone: respect `prefers-reduced-motion`, give touch screens an equivalent with no pointer to follow, animate transforms and opacity so it stays smooth, and keep keyboard focus visible.

## Review the round

Put each design in its own directory, such as `designs/<n>-<slug>/index.html`, or follow the project's routing if it already has a framework. Copy [viewer.html](viewer.html) to `designs/index.html` and fill in its `DESIGNS` list. Start a static server in the background, such as `python3 -m http.server` from `designs/`, or use the project's own dev server, and give the user the URL. The viewer switches designs with the arrow keys and shows each design's words, theme, and focal point.

Screenshot every design at desktop and mobile widths before handing over. Fix anything broken, and rework anything that reads as a template rather than its theme.

## Later rounds

After the first round, iterate on the design the user chose. Make five new designs only when the user explicitly asks for them, with fresh rolls.
