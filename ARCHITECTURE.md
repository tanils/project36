# Architecture and roadmap

## V1 — High-signal news

Collectors -> deduplication -> scoring -> optional AI enrichment -> ranking -> delivery -> state

## V2 — Official-event verification

Add:
- NSE/BSE announcement ingestion
- Company IR feeds/pages where permitted
- RBI/SEBI/government feeds
- Results calendar
- Corporate actions

Official confirmation should increase confidence and reduce false positives.

## V3 — Trading confirmation

Add a market-data adapter:

event -> affected stocks -> price reaction -> volume -> sector relative strength -> F&O OI -> market regime

The news agent should never convert a news headline directly into a BUY/SELL instruction.

## V4 — Learning

For each event store:
- publication time
- alert time
- event scores
- affected stocks
- price at alert
- 30m / 1d / 3d / 5d / 10d / 20d returns
- max adverse excursion
- max favorable excursion

Then calibrate scores using actual outcomes.

## Source policy

Use public feeds/APIs and sources you are licensed/permitted to access. Do not bypass paywalls, login controls, robots restrictions or anti-bot systems.
