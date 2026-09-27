# WebSim: the Weave

A whole fictional internet for testing web agents.

Real-web benchmarks have a problem: models already know the real web. They know Wikipedia
is for facts, Stack Exchange for math, Amazon for shopping. That prior does a lot of the work.
The Weave is the internet of **Averra**, a world that does not exist, so none of those priors
apply. An agent has to work out from first principles how this internet is organised, which
sources can be trusted, and where information actually lives.

```
54 sites · ~8,800 pages · ~4,200 generated images · 117 recorded facts · 224 eval questions
```

Everything is generated from one consistent world simulation, so the same fact (a price, a
date, a name) agrees across every site that mentions it, except where the world is
*meant* to disagree (a tabloid gets the numbers wrong, an encyclopedia folio is out of
date, a highly voted answer is incorrect).

## Quick start

Needs only Python 3 (tested on 3.11), no packages.

```bash
python -m othernet.build          # writes ./web (the sites) and ./meta (ground truth), ~7s
python -m othernet.serve          # serves on http://127.0.0.1:8080
```

Then either:

* **As a person:** open <http://morrow.ves.localhost:8080/>. Chromium-based browsers resolve
  `*.localhost` automatically, and the server rewrites links so you stay on localhost.
* **As an agent / Playwright:** use the server as an HTTP proxy and visit the real fictional
  addresses. Nothing is rewritten.

  ```js
  const browser = await chromium.launch({ proxy: { server: 'http://127.0.0.1:8080' } });
  await page.goto('http://lanthorn.ves/');
  ```
* **With curl:** `curl -x http://127.0.0.1:8080 http://bazaar.ves/`

Good starting points for an agent are the same as for a resident of Averra: `morrow.ves`
(the portal), `lanthorn.ves` (search), and `hearthring.fol` (the hand-kept directory).

## What makes it hard (on purpose)

* **Search doesn't see everything.** Lanthorn crawls only about two thirds of the sites, only
  statically visible text, and it demotes personal `.fol` sites (the "Lamp update"). The rest
  of the Weave is reachable only through the Hearthring directory, webrings, and links.
* **Unfamiliar conventions.** A 10-month calendar with 36-day months, 6-day weeks and 5
  Hollowdays. Dates written four different ways by four nations, one of which counts years
  from a different epoch (HR = CR + 880). A currency with 12 bits to the tally. Units like
  ells, leagues, thumbs, fenwicks. Kethren names are written clan-first.
* **Sources disagree.** News outlets report different numbers for the same event. An
  encyclopedia folio is years out of date. The accepted answer on the Q&A site is stale, and a
  wrong answer has more votes.
* **Interaction is required.** A metered paywall (credentials live on another site), a
  password-gated forum room (the password is a puzzle across two threads), a poll whose results
  appear only after voting, forms, calculators, a journey planner, a cart, "show more"
  buttons, cookie walls, tabs, hover text, and pages rendered entirely by script.
* **The web has history.** A company deleted its site; only the archive (Stillframe) has
  it. Short links chain through redirects or point at nothing. One page is linked only from an
  HTML comment.
* **Images carry information.** Specials boards with prices, floor plans with room sizes,
  auction photos with repair stamps, a temperature map.

## The sites

| Kind | Sites |
|---|---|
| Finding things | `lanthorn.ves` search, `hearthring.fol` directory and webrings, `morrow.ves` portal, `snip.ves` short links, `stillframe.hal` archive |
| Reference | `commonplace.hal` encyclopedia, `numerary.gld` mathematics, `lexicon.hal` dictionary, `chartroom.ves` atlas, `observatory.pel` moons and tides, `quorum.fol` Q&A |
| News | `ostmerecourier.wir` (paywall), `tidings.slt`, `thecrier.wir` (tabloid, script-rendered), `lodestone.wir` (science), `radiolantern.pel` (schedules, transcripts) |
| Commerce | `bazaar.ves` (1,400+ products), `emberline.ves` ferries and airships, `drovers.ves` bank, `hollowmarket.ves` auctions, `hearthfind.ves` property, `vantle.ves` tech, `copperkettle.ves` tea rooms, `quillmere.ves` publisher, `tastemark.ves` reviews, `noticeboard.fol` classifieds |
| Civic | `registry.vey` companies, `assembly.vey` legislature, `exchange.slt` stock exchange, `weather.vey`, `tramways.slt`, `rulings.khr` court rulings, `stats.pel` statistics, `post.vey` post office, `patentrolls.gld` patents, `synod.odd` |
| Learning and culture | `lanternport.hal` university, `annals.hal` journal, `athenaeum.hal` library catalogue, `deephalls.khr` museum, `reelhouse.ves` films, `bellows.ves` records, `vaultball.ves` sport |
| Community and personal | `chatter.fol` microblog, `tallowboards.fol` forum, `wrenwrites.fol`, `spirekeeper.fol`, `ossawatcher.fol`, `hearthandhob.fol` recipes, `inkling.fol` webcomic, `fathomwiki.fol` game wiki, `guildwork.gld` jobs, `whiskerhaven.fol` pets, `weft.gld` programming language |

## Ground truth for evals

`python -m othernet.build` also writes `meta/`:

* `meta/sites.json`: every site, its category, whether Lanthorn indexes it, and page count.
* `meta/pages.jsonl`: every page URL and title.
* `meta/facts.jsonl`: facts recorded by the generators as they rendered them, each with the
  question, answer, URL where it appears, modality (`text`, `image`, `interaction`, `hover`,
  `source`), and hop count.

`evals/questions.jsonl` holds **224 eval questions** (90 easy, 77 medium, 57 hard), each with a
single objective answer, verified against the built Weave. `evals/grade.py` scores answers. See
[evals/README.md](evals/README.md). `docs/WORLD.md` is the spoiler guide to the world and its
storylines, for people writing new questions.

## Running agents

`harness/` runs agents such as Codex on the questions through
[Harbor](https://github.com/harbor-framework/harbor). The agent gets one question and a
browser it controls with screenshots and clicks, and nothing else. It cannot see the
questions file, the answers, or the site files, and it cannot reach the real internet. See
[harness/README.md](harness/README.md).

```bash
bash harness/build_images.sh && python harness/make_tasks.py
OPENAI_API_KEY=... harbor run -c harness/codex-job.yaml
```

## Checks

```bash
python tools/check_links.py web     # every href/src resolves (a few deliberate dead links excepted)
python tools/check_svg.py web       # every generated image is valid SVG
node tools/smoke_test.js            # end-to-end checks of paywall, logins, forms, cart, search (needs Playwright and the server running)
python -m othernet.evalgen          # regenerate and verify the eval questions
node tools/verify_interactive.js    # replay the interactive eval questions in a browser
```

## How it's built

```
othernet/
  world/     the simulation: calendar, geography, people, companies, history, politics,
             markets, sport, weather, tides, news stories, products, culture
  engine/    site/page writer, SVG image generators, maps, paywall, webrings, links
  sites/     one module per site; each has build(web, site)
  build.py   builds every site in order, then the search index, directory and archive
  serve.py   proxy / *.localhost / Host-header server
```

All randomness is seeded by name, so the build is deterministic, and adding a site does not
change any other site's content. The "present day" in Averra is **Loomday, 17 Gale 412 CR**.
