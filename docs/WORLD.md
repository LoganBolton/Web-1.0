# The world of Averra (spoilers)

This is the guide for people writing evals. Agents should not see it.

## Basics

* **Today** is Loomday, 17 Gale 412 CR.
* **Calendar:** 10 months of 36 days (Rime, Thaw, Loam, Bloom, Blaze, Crest, Sheaf, Gale, Mire,
  Dusk) then 5 Hollowdays. Week: Anvilday, Kettleday, Loomday, Plowday, Hearthday, Stillday.
* **Date formats:** Veyl `412·08·17`; Saltmarch `17/8/412`; Kethren `17.8.1292 HR` (HR = CR + 880);
  Pellucid `Gale 17, 412`; Oddavar counts years of the Flame (FR = CR + 1400, never stated).
* **Money:** crown (cr, 100 pennets), tally (tl, **12 bits**), mark (mk), lume (lm), sked (sk).
  Daily exchange rates are simulated for all of 412 (`world/econ.py`).
* **Units:** ell (a bit over a metre, 40 thumbs), league (4,000 ells), weight (wt, ~0.5 kg),
  measure (~a cup, 16 spoons), fenwick (unit of power), degrees Harl (like Celsius).
* **Two moons:** Ossa (29.25 days) and Pith (7 days 11 hours, retrograde).
* **Weave vocabulary:** loom = computer, slate = handheld, ribbon = program or file, reed = bit,
  weave = a million reeds, lantern = link, crumb = cookie, loom-letter = email.

## Nations

| | Capital | Head | Domain |
|---|---|---|---|
| Concordat of Veyl | Ostmere | First Warden Maelis Ondraker | .vey |
| Saltmarch Republic | Brineholt | Tidemaster Oriel Casswater | .slt |
| Kethren Holds | Harrowdeep | High Holdwarden Harrow Dagna | .khr |
| Pellucid Isles | Lanternport | Chancellor-Senator Iselle Marovane | .pel |
| Oddavar | Vesk | Hierarch Skeld Varrakin | .odd |

Tended domains: `.ves` commerce, `.fol` folk/personal, `.hal` learning, `.gld` guilds, `.wir` news.

## Storylines of 412

**Tarrow Canal affair.** 4 Thaw: Gildmere Works wins the 1.84 bn cr widening contract over a
cheaper Keelwright/Silverrun bid. 20 Bloom: Courier reveals CEO Osric Gildmere is married to
Maud Ashford, the minister's sister (first edition said "cousin"). 30 Crest: Registry shows Sallow
Fen Holdings (sole director Maud Ashford) held 12% of Gildmere, bought 12 Dusk 409, sold 18 Blaze
412. 11 Gale: Ashford testifies (Assembly Record). No-confidence vote scheduled 26 Gale. Rumour
(Tallow Boards Back Room): the Guild engineer on the bid panel, Hemming Lockwright, was a Gildmere
protégé; confirmed only by the deleted gildmere.ves staff page in Stillframe.

**Deepshaft 9.** Collapse 22 Crest at Cinderfell. Courier said 14 trapped (corrected), Tidings 17,
Crier "dozens", truth 16 (two Slatebrook Haulage contractors off the shift list). All rescued 28
Crest, led by Greystone Magna. Moot ruling MR 1292/31 (9 Gale): 4.2 m mk fine, three ignored
warnings. The refuge lamp is in the Museum of the Deep Halls (lent by Cinder Asta).

**Slate 7.** Announced 3 Sheaf, on sale 1 Gale (1,299 / 1,549 cr). VC-7A charger recall 14 Gale,
affected batches end 0800–1600, 212 reports. Weave OS 7.0.2 throttles VC-7A.

**Cresselle Conjecture.** Aubrel's proof 30 Dusk 411; Flint finds a gap (Bloom); revised proof 5
Gale; Numerary status "Under review". Quorum's most-voted answer wrongly says proven.

**Pith crossing.** 3 Mire 412, 21:14 Lanternport, 41 minutes. Harthwick 21:20. Not visible from
Brineholt or Vesk.

**Storm Petrel.** 7–9 Gale. Gust 27 leagues/hour at Northmole, 3,400 homes lost power. Harbour
Line reopened 12 Gale 07:10, Stair funicular still closed. Nell Hedgecote's Saltspire show
cancelled. Pip the cat lost in Keelwater, now at Keelwater Rescue (Whiskerhaven).

**Quenby clock hand.** Stolen 8 Loam; turned up as Hollowmarket lot 4471 ("gilded pointer"),
spotted by Wenna Larkfield via the stamp Q.C. 331; withdrawn.

**Harthwick Lighthouse.** Changed 1 Sheaf from 2 flashes/9 s to 3 flashes/12 s. The Commonplace
(revised 402) and Quorum's accepted answer are stale.

**Smaller threads.** The green hat (Anouk Belvaine) at Pearl & Pith with Jago Tidewright; the
@drovers_help_desk scam on Chatter; the Copper Kettle gift card scam on the Noticeboard (real
balance 3.00 cr); the RT 17 key (Ossa Watcher hidden page, Noticeboard lost and found); Lanthorn's
Lamp update; the Skylark airship (1 Crest); Fathom's Ninth Trench expansion (14 Mire, not 3 Mire).

## Credentials and puzzles

* Courier: `athenaeum` / `NINEFORDS-412` (on athenaeum.hal/weave-resources/). `courier_share` /
  `kittiwake7` is recognised but suspended. Three free articles, tracked in localStorage.
* Tallow Boards Back Room: reader `member`, password `wicket` (rules thread + pets thread).
* Ossa Watcher hidden page: `/x/the-ledger/`, linked only in an HTML comment.

## Deliberate dead ends

`gildmere.ves` (gone; Stillframe only), `snip.ves/gw`, `snip.ves/old1`, `snip.ves/tt`
(tramways page that moved), Lanthorn cannot see behind search boxes or scripts, and the Synod's
pilgrim page accepts no number.
