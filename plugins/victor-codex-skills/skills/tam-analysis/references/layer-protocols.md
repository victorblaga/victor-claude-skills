# Layer Protocols by Business Model

Use this at Step 0 to propose a layer structure adapted to the company's business model. Don't pick a generic structure — different models have different natural decomposition.

The goal: each layer captures one source of value that has its own pool, own mature share, own monetization metric, own pricing power, own maturity timeline. Layers are additive (revenue at maturity = sum across layers, post-overlap-haircut).

## Choosing the Model

Most companies fit cleanly into one of these. When in doubt, pick by where most of today's revenue comes from. Add adjacent-model layers later (e.g., a retailer that's becoming a marketplace gets a retailer-style core layer + a marketplace-style adjacency layer).

| Model | Pick when | Core unit |
|-------|-----------|-----------|
| Retailer | Goods sold to consumers from owned inventory | Stores, sqm, baskets, e-commerce sessions |
| Marketplace / auction | Third-party listings, take-rate revenue | Transactions, GMV, listings |
| SaaS / platform | Recurring software subscriptions, seat or usage based | Seats, subscribers, accounts, API calls |
| Industrial / hardware | Capital goods + service revenue | Installed base, units shipped, service contracts |
| Consumer subscription | Households / individuals paying recurring fee for service | Subscribers, households, ARPU |
| Financial services | Bank, broker, insurance — balance sheet + fee mix | Accounts, AUM, loans, policies |
| Payments | Money-movement, take rate on volume | Transactions, volume, MAUs |

A company can be multi-model. Tesla = industrial (cars) + SaaS (FSD) + utility (energy + storage) + speculative (robotaxi / robotics). Each business model gets its own protocol.

## Retailer

Core decomposition:

1. **Core format × catchment density** — stores at saturation × sales-per-store (or per-sqm) × territory coverage.
2. **Adjacent formats** — e.g., neighborhood / convenience format alongside large-box; warehouse club; outlet.
3. **E-commerce / private label** — direct online channel, own-brand penetration. Often grows the pool, not just shifts it.
4. **Adjacent geographies** — country-by-country, with separate population × per-capita demographics. Don't paste a US revenue / store onto India.
5. **Adjacent categories** — extending into grocery, pharmacy, household goods, services.

Speculative slot candidates: ad networks on first-party shopper data; fulfillment-as-a-service; financial-services arms (BNPL, credit cards); media / content built on captive audience.

Real-world precedent: Costco, Home Depot, Mercadona, Inditex. The thesis usually is store-density-driven; international expansion is the speculative-to-becoming-proven layer.

## Marketplace / Auction

Core decomposition:

1. **Core category × take rate** — transactions or GMV × revenue / transaction.
2. **Adjacent categories** — extending the platform to neighboring inventory types.
3. **Geographies** — different competitive density and listing supply per region.
4. **Service-layer monetization** — financing, logistics, ads, data, escrow, certification.
5. **Subscription / seller-tools** — recurring fee for power sellers, dealer SaaS, etc.

Speculative slot candidates: balance-sheet products (inventory finance, AR factoring); private-label / direct inventory; vertical SaaS for the seller side; data resale to advertisers / insurers / lenders.

Real-world precedent: Copart, Auto Trader, MercadoLibre, Adevinta. Network-effect moats often allow >50% share in the core geography.

## SaaS / Platform

Core decomposition:

1. **Primary endpoint pool** — seats / accounts / API calls in the targeted role or use case.
2. **Adjacent products** — modules cross-sold to the same buyer (e.g., CRM → service cloud → marketing cloud).
3. **Per-seat ARPU uplift** — pricing power within existing accounts; tier mix; usage-based overages.
4. **Asset-backed adjacencies** — data products built on customer telemetry; payments / financial flows running through the platform; marketplaces for plugins / integrations; infrastructure offered to the broader market.

Speculative slot candidates: data-resale products; embedded financial services; LLM / AI-features priced separately; industry-cloud verticalizations.

Real-world precedent: Salesforce, ServiceNow, Snowflake. Watch for the "infrastructure-spun-off-as-a-product" pattern (Stripe → Stripe Atlas / Stripe Capital; Shopify → Shop Pay).

## Industrial / Hardware

Core decomposition:

1. **Installed base × replacement cycle × ASP** — units in service × annual replacement rate × average selling price.
2. **Aftermarket + service** — parts, service contracts, software updates, certified inspection.
3. **Adjacent SKUs** — extending the hardware line into related product categories.
4. **Recurring software / data** — telematics, fleet management, predictive maintenance, optimization software.

Speculative slot candidates: usage-based service (e.g., outcomes-based contracts); marketplaces for used inventory; financing of replacements; data resale (operating-condition telemetry).

Real-world precedent: John Deere, Caterpillar, Rolls-Royce. The aftermarket and software layers often have higher pricing power than core hardware.

## Consumer Subscription

Core decomposition:

1. **Households × penetration × ARPU** — addressable households × steady-state subscriber penetration × revenue per subscriber.
2. **Adjacent demographics** — international, lower-tier markets, age cohorts.
3. **Adjacent products** — companion services, tiers, family / multi-user expansions.
4. **Ancillary monetization** — advertising on subscriber base, partnerships, transactional revenue.

Speculative slot candidates: data / advertising layer; live commerce; financial services for engaged user base; B2B / partnership channels.

Real-world precedent: Netflix, Spotify, Disney+. International-mix economics differ sharply from home market — separate layer per major region.

## Financial Services

Core decomposition:

1. **Addressable wallet × take rate** — total customer balance / lending capacity × revenue rate (NIM, fee rate, commission rate).
2. **Adjacent products** — cross-sell of related products to the existing relationship (savings → lending → wealth → insurance).
3. **Balance-sheet products** — own-book lending or insurance underwriting; growth limited by capital.
4. **Geographic expansion** — separate prudential regimes, different competitive density.

Speculative slot candidates: embedded-finance offered to non-bank distributors; data / scoring products; B2B treasury products; crypto / digital-asset rails.

Real-world precedent: JPMorgan, Visa+MA on the payments side, Nubank. Be careful — balance-sheet growth rate is constrained by capital, ROE matters more than top-line.

## Payments

Core decomposition:

1. **Core flows × take rate** — addressable volume × take rate in bps.
2. **Adjacent flows** — B2B, cross-border, payouts, push-to-card, account-to-account.
3. **Value-added services** — fraud, identity, dispute management, ads, loyalty, lending against flow.
4. **Data monetization** — issuer-side, merchant-side analytics; resale to advertisers / lenders.

Speculative slot candidates: stablecoin / programmable-money rails; embedded-credit; identity / KYC sold standalone; AI-driven fraud-as-a-service.

Real-world precedent: Visa, Mastercard, Adyen, Stripe. Take rate compression is the dominant bear mechanism — separate today's mix from forward mix.

## Multi-Model Companies

When the company spans models, build separate layer trees per model and concatenate. Examples:

- **Amazon-style retailer + marketplace + infrastructure**: retail-core + marketplace adjacency + ad-network adjacency + cloud-infrastructure speculative-becoming-proven.
- **Tesla-style industrial + SaaS + utility + robotics**: vehicle-industrial + FSD-SaaS + energy-utility + robotaxi-speculative + humanoid-speculative.
- **Bank turning into platform**: financial-services core + adjacent fintech products + embedded-finance speculative.

Each layer keeps its own protocol. Don't blend the share / monetization / pricing logic across models.

## Per-Layer Maturity Calibration

Different layers mature at different speeds. Calibration anchors:

| Layer character | Typical maturity horizon |
|-----------------|--------------------------|
| Saturated domestic retail format | Y10-Y15 |
| Domestic SaaS in a defined market | Y10-Y15 |
| International expansion of proven model | Y15-Y25 |
| Category-defining marketplace | Y15-Y25 |
| Adjacent-category extension | Y15-Y25 |
| Infrastructure / utility / network buildout | Y20-Y40 |
| Speculative adjacency just forming | Y25-Y40+ |
| Regulatory-protected category | Y20-Y40 (slow to mature, slow to decline) |

These are starting points. Adjust based on the specific layer's structural drivers.

## Real Pricing Power Calibration (Per Layer)

The most commonly missed input. Express as fading profile in REAL % (0% real = pricing exactly matches inflation). Apply at the multiplication step, not when sizing the pool.

| Pricing power | Examples | Decade 1 / 2 / 3 (real %) |
|---------------|----------|----------------------------|
| High | Narrow-vertical SaaS, dominant marketplace, premium brand, regulated infra | +2.5% / +2% / +1.5% |
| Medium | Most enterprise software, premium retail, regulated infra in competitive geos | +1.5% / +1% / +0.5% |
| Low | Commodity goods retail, mature staples, low-end consumer | ~0% (just inflation) |
| Negative | Commoditizing tech, deflationary categories (e.g., LCD panels, cloud compute over long horizons) | -1% to -3% |

Detail and precedents in `multiplication-protocol.md`.

## Common Mistakes

- **Single layer for a multi-model company.** Amazon-as-just-retail misses AWS. Tesla-as-just-cars misses everything. Always test for multi-model.
- **Geographies as a single layer.** US and EM consumer ARPU differ by an order of magnitude. Separate.
- **Speculative folded into base case at full weight.** The whole point of tagging speculative is to scenario-weight it differently. Conservative in base, generous in bull, zero in bear.
- **No overlap haircut.** Customer who bought books online and buys groceries online is one customer. Don't double-count households across product layers without explicit overlap accounting.
- **Maturity horizon same for every layer.** Different layers mature at different times — that's the whole point of per-layer maturity.
