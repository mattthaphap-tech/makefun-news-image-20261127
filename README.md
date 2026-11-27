# Friday 27 November 2026 — 35 stories, 7 regions

[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/mattthaphap-tech/makefun-news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/mattthaphap-tech/makefun-news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)

Entry for the [make.fun news-image-20261127 bounty](https://make.fun/bounty/news-image-20261127):
a one-day front page — **35 stories, 7 regions, all from Friday 27 November 2026**.

![Friday 27 November 2026 front page](entry.png)

## What's inside

- **3 leads:** EU summit picks de Cos as next ECB chief · Gaza toll rises despite ceasefire · Asian shares rally on Friday
- **10 minis:** NZ final count — coalition one seat short · Black Friday sales open · Nvidia reportedly halts chip shipments to four SE Asian countries · Drone violates Latvian airspace, NATO jets scrambled · Thanksgiving storm leaves 961,000 without power · Delimitation Bill — Lok Sabha seats may rise by half · Zelenskyy warns Russia preparing new mass strike · US markets reopen for shortened Black Friday session · College football Black Friday — 13 FBS games · India–NZ 2nd Test begins at Christchurch
- **22 briefs:** Finland signs border closure extension · F1 Qatar GP practice opens · Chandrayaan-5/LUPEX rover prototype · Tripura civic polls · Tamil Nadu paternity leave · India–UAE defence equipment · Peerzada Sayeed dies at 73 · M1–StarHub merger · Singapore median income S$6,021 · Laos leaves UN development list · Canada tariff talks into January · Atiku, Obi, Makinde meet Monday · Plateau mass burial · Kwara jailbreak · Pension backlog cleared · Fake emergency calls 57m · INEC/NSA riot act · NHI deterring investors · ActionSA–ANC Ekurhuleni deal · Mahama hands over aircraft · GoldBod 5,000 jobs · AU briefing on South Sudan

**Regions:** EUROPE 3 · UKRAINE WAR 1 · MIDDLE EAST 2 · ASIA 12 · OCEANIA 1 · AMERICAS 5 · AFRICA 11.

## Date discipline

Every story happened, or was first reported, on Friday 27 November 2026.
Stories from 22–26 Nov (Kuwait drone attack, Bangkok refinery explosion, UK
net migration, Kyiv missile strike, Pete Edochie dies at 79, COP31, the
birthright ruling, Putin's Arctic strategy, Development Road talks…) were
checked and deliberately left out — see the date-check box on the page and
the full list in [`research.md`](research.md).

## How it was built

The front page is drawn entirely in code (`build_27nov.py`, Python + PIL):
dark ink on light paper, no map, legible at 390px. `main.py` copies the
rendered `entry.png` (1024×1024 RGB, ≤1 MiB) to `/output/entry.png` with
size + sha256 verification. Rebuild with:

```sh
python3 build_27nov.py
```
