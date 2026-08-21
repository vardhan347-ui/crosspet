#!/usr/bin/env python3
"""Regenerate grape-loading.html from grape-walk.svg."""
import re, pathlib
root = pathlib.Path(__file__).resolve().parent
svg = root.joinpath('grape-walk.svg').read_text()
# the page hosts one instance, so the SVG's own <style>/ids come along untouched
svg = svg.replace('width="340" height="380" ', '')
svg = re.sub(r'^', '      ', svg, flags=re.M).strip()

HEAD = '''<title>Grape Walk Loader</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;800&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
  :root {
    --paper:  #F7F2FB;
    --raised: #FFFFFF;
    --ink:    #241A2C;
    --muted:  #7A6C87;
    --line:   #E1D5EE;
    --accent: #A342DE;
    --track:  #E9DDF5;
    /* Separates the character's black outline from the ground it sits on. */
    --halo:   radial-gradient(closest-side, rgba(163,66,222,.11), rgba(163,66,222,0));
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --paper:  #1D1526;
      --raised: #271D33;
      --ink:    #F3EBF9;
      --muted:  #A294B0;
      --line:   #35263F;
      --accent: #C77BF0;
      --track:  #32233E;
      --halo:   radial-gradient(closest-side, rgba(199,123,240,.26), rgba(199,123,240,0));
    }
  }
  :root[data-theme="dark"] {
    --paper:  #1D1526;
    --raised: #271D33;
    --ink:    #F3EBF9;
    --muted:  #A294B0;
    --line:   #35263F;
    --accent: #C77BF0;
    --track:  #32233E;
    --halo:   radial-gradient(closest-side, rgba(199,123,240,.26), rgba(199,123,240,0));
  }

  * { box-sizing: border-box; }

  body {
    margin: 0;
    min-height: 100vh;
    display: grid;
    place-items: center;
    padding: 32px 20px;
    background: var(--paper);
    color: var(--ink);
    font-family: "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
    -webkit-font-smoothing: antialiased;
  }

  .loader {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 28px;
    width: 100%;
    max-width: 380px;
  }

  .stage {
    width: 100%;
    display: flex;
    justify-content: center;
    background-image: var(--halo);
    background-repeat: no-repeat;
    background-position: center 46%;
    background-size: 108% 86%;
  }
  .stage svg {
    width: 100%;
    max-width: 300px;
    height: auto;
    display: block;
    color: var(--muted);
  }

  .readout { display: flex; flex-direction: column; align-items: center; gap: 10px; width: 100%; }

  .eyebrow {
    margin: 0;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: .22em;
    text-transform: uppercase;
    color: var(--muted);
  }

  .headline {
    margin: 0;
    font-family: "Baloo 2", "Segoe UI Rounded", "Trebuchet MS", system-ui, sans-serif;
    font-weight: 800;
    font-size: clamp(24px, 6vw, 31px);
    line-height: 1.15;
    letter-spacing: -.01em;
    text-align: center;
    text-wrap: balance;
  }

  .bar {
    width: 100%;
    height: 7px;
    margin-top: 8px;
    border-radius: 99px;
    background: var(--track);
    overflow: hidden;
  }
  .bar span {
    display: block;
    width: 27%;
    height: 100%;
    border-radius: 99px;
    background: var(--accent);
    animation: sweep 1.55s cubic-bezier(.6,0,.4,1) infinite;
  }
  @keyframes sweep {
    from { transform: translateX(-115%); }
    to   { transform: translateX(372%); }
  }

  .step {
    margin: 0;
    font-size: 13px;
    color: var(--muted);
    text-align: center;
    min-height: 1.4em;
    font-variant-numeric: tabular-nums;
  }
  .step b { color: var(--ink); font-weight: 500; }

  @media (prefers-reduced-motion: reduce) {
    .bar span { width: 100%; animation: pulse 2s ease-in-out infinite; }
    @keyframes pulse { 0%, 100% { opacity: .35; } 50% { opacity: 1; } }
  }
</style>'''

BODY = '''<main class="loader">
  <div class="stage">
%SVG%
  </div>

  <div class="readout">
    <p class="eyebrow">CrossPet</p>
    <h1 class="headline">Getting your reader ready</h1>
    <div class="bar" role="progressbar" aria-label="Loading" aria-valuetext="In progress"><span></span></div>
    <p class="step" id="step" aria-live="polite"><b>Mounting SD card</b></p>
  </div>
</main>

<script>
  var steps = [
    "Mounting SD card",
    "Indexing your library",
    "Rebuilding cover cache",
    "Waking your pet"
  ];
  var i = 0, el = document.getElementById("step");
  setInterval(function () {
    i = (i + 1) % steps.length;
    el.innerHTML = "<b>" + steps[i] + "</b>";
  }, 2200);
</script>'''.replace('%SVG%', svg)

full = '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n' + HEAD + '\n</head>\n<body>\n' + BODY + '\n</body>\n</html>\n'
root.joinpath('grape-loading.html').write_text(full)

print('wrote', root / 'grape-loading.html', len(full), 'bytes')
