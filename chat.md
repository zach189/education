> **Current direction — 2026-09-27:** This file is a historical conversation record. The original linear 13-lesson outline below has been superseded by the [canonical curriculum roadmap](notebooks/README.md). The project is now an independent Liquid Compute compute-finance curriculum and reusable calculator library: three foundation lessons, Financing F1–F9 (priority), Market Risk M1–M7, optional Electives E1–E6, and original transaction Capstone C1. Financing can start after Notebook 2. The OEM deposit bridge is a distinct lesson, and equipment-owning projects remain separate from capacity resellers. Foundation notebooks 1–3 are implemented locally. Notebook 4 / M1 is now “The Tenor Trade: Buying Long, Selling Short”; forwards and swaps move to M2, and the remaining market-risk lessons shift through M7.

# Chat: GPU Compute Financing Notebooks

## User

read and understand this post

https://x.com/gpugene/status/2104186844007248332?s=46

## Assistant

I’ve read the full article, “Let’s talk about trading compute”, on the author’s Substack.

His central argument: an operator should be able to protect against rising GPU rental prices without committing to years of capacity it might not need. He develops that through three distinct examples:

- Protecting a potential launch. A customer might need 2,048 GPUs during months 13–15. A cash-settled call offsets rental prices above a strike, but securing the actual GPUs remains a separate problem.
- Delaying part of the protection payment. A compound option lets the operator pay today for the right to buy that call in month 12. This changes the payment schedule; it doesn’t make protection free.
- Managing an ongoing fleet. A separate five-year simulation compares long commitments, annual renewals, and combinations with calls. Under his assumptions, calls increase average cost slightly while reducing expensive outcomes. The compound option is not one of the simulated strategies.

The key distinction I’ll keep in mind: the launch example and fleet simulation are separate exercises, and the results depend on hypothetical pricing, demand, resale, and hedging assumptions. I understand the structure and am ready to work through it with you.
## User

I'm interested in making a series of jupyter notebooks in python. as a teaching/experimentation tool. I would like to walk through financing of this sort. starting from forward curves to options. what other topics would be useful. how should they build upon each other to teach core ideas in a structured way. I would like ideas to build upon each other. each lesson should be concise we aren't trying to write a huge novel but have something digestible and easily understandable

## Assistant

I’d build this as a sequence of small notebooks following one compute business, with each notebook introducing one new decision.

Keep the same customer, GPU fleet, and contract units throughout. Start with known demand and prices; introduce uncertainty gradually. That makes it clear why each financial tool becomes useful.

A good core sequence would be:
| # | Notebook | Central question | Main experiment |
| --- | --- | --- | --- |
| 1 | The compute business | How does an operator make or lose money? | Change rental price, customer revenue, and utilization. Watch profit and unused capacity change. |
| 2 | Cash flows through time | Why do payment dates matter? | Compare monthly payments with an upfront prepayment. Calculate present value and cash required. |
| 3 | Building a forward curve | What do today’s contract prices imply about different future periods? | Extract implied blocks from one-, three-, and five-year rental quotes, with and without discounting. |
| 4 | Locking a future price | What does a forward actually protect? | Compare floating purchases with a fixed-price forward across several future prices. Separate physical delivery from cash settlement. |
| 5 | An imperfect hedge | What happens when my rental bill differs from the benchmark? | Change location, GPU type, purchased quantity, and index tracking. Measure the remaining exposure. |
| 6 | Uncertain demand and prices | What if I don’t know how much compute I’ll need? | Introduce a few joint price/demand scenarios. Compare committing now with buying later. |
| 7 | Buying price protection with calls | Can I limit expensive outcomes while keeping flexibility? | Add a call to the rental bill. Change strike, premium, and covered quantity. |
| 8 | What should the option cost? | Where does an option premium come from? | Build a two-step binomial model, replicate the payoff, and change volatility and strike. |
| 9 | Waiting before committing: compound options | What if the customer hasn’t signed yet? | Compare buying the call today with paying for the right to buy it later. Track both payment dates and cancellation outcomes. |
| 10 | Comparing purchasing policies | Which combination fits the business’s risks? | Run the same simulated paths through long commitments, annual renewals, mixed purchasing, and calls. |

Three distinctions should be taught explicitly:

- A curve inferred from bundled rental contracts is not necessarily a set of executable forward prices.
- Financial price protection does not itself guarantee physical capacity.
- Probabilities used to describe possible business outcomes are different from the pricing weights used in option replication.

Then extend the series into financing, using the cash flows already built:
| # | Notebook | Central question | Main experiment |
| --- | --- | --- | --- |
| 11 | Prepayment as financing | What discount compensates a buyer for funding the supplier early? | Compare the supplier’s funding benefit with the buyer’s financing cost and delivery exposure. |
| 12 | Debt, liquidity, and default | Can a profitable contract still run out of cash? | Add loan payments, collateral calls, and delayed hedge settlements. Track the maximum funding gap. |
| 13 | Senior and junior claims | How can investors take different parts of the risk? | Split the same project cash flows through a simple waterfall. Show who absorbs losses and receives upside. |

For each notebook, I’d use the same short format:

- One question and a brief business situation.
- One worked example with small, readable numbers.
- A few editable inputs near the top.
- One main chart and a small results table.
- Two “try this” experiments.
- One takeaway and one limitation.

Aim for 10–15 minutes per notebook. Show the important arithmetic directly; hide only repetitive plotting and plumbing.

Most importantly, start with three hand-built scenarios before introducing thousands of simulated paths. The reader should understand exactly why a strategy wins or loses in one scenario before looking at a distribution of results.
## User

do you think that overview is enough to start working

## Assistant

Yes—enough to start building the first notebook. The sequence is clear; we can refine later lessons as the early ones reveal what needs explaining.

I’d settle four small conventions first:

- Audience: comfortable with basic Python, new to derivatives and financing.
- Shared example: one operator renting GPUs and selling compute to a customer, using clearly labeled hypothetical numbers.
- Units: prices in $/GPU-hour, quantities in GPUs, monthly cash flows, and an explicit hours-per-month assumption.
- Notebook standard: runnable from top to bottom, editable assumptions at the top, visible core calculations, and roughly 10–15 minutes per lesson.

For notebook 1, the scope should be deliberately small: rented capacity → customer usage → revenue and rental expense → profit → break-even utilization. No random paths or derivatives yet.

One improvement to the outline: end each lesson with the unresolved problem that motivates the next. For example:

- “This contract looks profitable overall, but requires payment before the customer pays us. How much cash do we need, and what does that financing cost?”

That gives the series a connected story. We have enough direction to build notebook 1 as the reference for the rest; we don’t need to fully specify all 13 upfront.


Sources


---

## Imported direction discussion — 2026-09-27

The following user-supplied discussion records the newer direction. It is preserved verbatim as context, not as independent verification of the industry claims it contains. Specific financing disclosures and facility terms are research leads requiring primary-source verification. The canonical roadmap resolves lesson order and identifiers; the discussion itself is not a competing implementation specification.

the current plan is basically focused on recreating the lessons In that post, which is fine. what other financing topics should we make lessons/education for. search ornn docs and other places for ideas

Yes. I’d broaden this into a compute finance curriculum, with derivatives as one branch. You can start the financing branch immediately after notebook 2; it doesn’t need to wait for options.

I reviewed Ornn’s documentation, CoreWeave financing disclosures, the OCC’s asset-based lending handbook, World Bank project-finance material, and CME’s educational resources. The lesson designs below are my proposed applications of those sources.

The most useful financing sequence would be:
Lesson	Question it answers	Interactive experiment / reusable calculator
1. Financing a compute prepayment	Should we fund an upfront purchase with equity, borrowing, or customer prepayments?	Compare the rental discount with interest, fees, repayment timing, and required equity. Extend notebook 2.
2. What makes an offtake contract financeable?	Why can two contracts with identical headline revenue support different financing?	Change minimum commitments, cancellation rights, customer payment reliability, and service credits. Measure dependable cash available for debt payments.
3. How much debt can this deal support?	What loan amount can the contract’s cash flows repay?	Calculate debt-service coverage and solve for debt capacity. Compare level repayments with repayments shaped around available cash.
4. Financing receivables and collateral	How much can we borrow against eligible assets today?	Apply advance rates, overdue-invoice exclusions, concentration limits, and reserves. Show borrowing availability shrinking under stress.
5. Contract renewal and maturity mismatch	What happens when customer commitments end before our obligations?	Finance five years of exposure with three years of contracted revenue. Change renewal prices, downtime, and replacement-customer demand.
6. GPU ownership, leasing, and residual value	How much does the deal depend on what the hardware is worth later?	Compare purchase and lease cash flows. Stress resale proceeds against remaining debt; distinguish accounting depreciation from resale value.
7. Waterfalls, reserves, and investor returns	Who receives cash first, and who absorbs losses?	Allocate cash to expenses, debt, reserves, and equity. Add a distribution lockout or cash sweep and inspect each investor’s outcome.
8. Deployment delays and staged funding	What if capital is committed before the GPUs generate revenue?	Delay delivery or customer acceptance. Compare drawing the whole loan immediately with staged draws; track interest and additional equity needed.

These have direct grounding in actual financing practice:

    CoreWeave describes asset-level debt supported by take-or-pay customer contracts. Its disclosures also describe borrowing limits tied to GPU infrastructure value and customer credit quality. That gives us a concrete basis for lessons 2–4.
    A particularly useful case study: CoreWeave’s August 2026 facility has an approximately five-year maturity against customer contracts averaging approximately three years. That is a real example of lenders underwriting renewal risk, directly relevant to lesson 5.
    The World Bank’s project-finance material connects debt coverage with reserve accounts, cash sweeps, and restrictions on distributions. The OCC handbook explains borrowing bases and repayment priorities. These provide foundations for lessons 3, 4, and 7.
    CoreWeave describes delayed-draw financing intended to align funding with infrastructure deployment, providing a starting point for lesson 8.

Ornn suggests several useful additions to the market-risk branch. Its docs cover more than forward curves: GPU benchmarks, realized volatility, rented-capacity utilization, wholesale power, and workload costs.
Lesson	Teaching question	Experiment
Choosing the right benchmark	Does the index actually track the exposure in this contract?	Compare a hypothetical provider’s rental prices with a GPU benchmark and measure the remaining mismatch. Ornn explicitly distinguishes its index from an individual provider quote.
Measuring risk from data	How much do our conclusions depend on the historical window?	Change lookback periods and compare volatility estimates. Keep market rented-capacity utilization separate from technical GPU utilization and a customer’s billable usage.
Power cost and compute margin	Can an operator’s margin deteriorate even when GPU rental prices are stable?	Translate power consumption into $/GPU-hour, then shock electricity prices. Ornn’s power data provides a source for later real-data exercises; wholesale prices are only part of a delivered electricity bill.
Cost per useful output	Can compute become cheaper per unit while the customer’s total bill rises?	Separate unit price, workload intensity, and workload mix. Ornn’s workload-cost methodology explicitly separates these effects.

Three further structuring lessons stand out:

    A hedge can create a cash crunch. Show a hedge that offsets the eventual economic exposure but requires cash before the offsetting business receipts arrive. Teach futures margin first, then separately specify any hypothetical OTC collateral terms. CME’s daily settlement explanation is a useful foundation.
    Minimum revenue plus shared upside. Compare fixed rent, floating rent, and a floor plus participation above a threshold. Shipping provides concrete examples: TEN publishes charter arrangements with minimum rates and profit-sharing provisions. The compute version would be our adaptation.
    Hedging financing costs. Add floating-rate debt, then compare an unhedged loan with a fixed-rate hedge. This connects operating cash flows to interest-rate exposure. CME provides a borrower-focused example.

For Liquid Compute, I’d prioritize prepayment financing → financeable offtake → debt capacity → renewal risk → waterfalls. Those could become useful deal calculators relatively quickly.

One structural change matters: retain the current capacity reseller for contract-financing lessons, and introduce a separate GPU-owning operator for equipment debt and residual value. Otherwise, the notebooks could accidentally attribute hardware collateral or resale proceeds to a business that only owns rental rights.
so that should replace the other finance section? should we remove stuff from the original outline we had to make it less of a copy of that guys substack post

Yes—replace the original three-lesson finance section with the expanded financing track. It separates topics that were previously bundled too tightly.

I’d also reorganize the derivatives track around Liquid Compute’s business questions. Forward curves, forwards, and options are foundational concepts worth keeping. The parts most closely tied to the post are its particular customer story, numbers, compound-option example, and five-year simulation.

Here’s how I’d revise the original outline:
Original material	Change
Compute economics and cash-flow timing	Keep as the shared foundation.
Forward-curve construction	Keep. Attribute Ornn’s method; use the post’s numbers as a cited verification example, with an independent main scenario.
Forwards and basis risk	Keep. Teach both buyer and seller exposures.
Uncertain demand and prices	Broaden. Include customer cancellation, unused capacity, renewal gaps, and delivery delays.
Calls	Expand to buyer caps and supplier floors. Introduce calls and puts through the risks each party faces.
Option pricing	Keep after payoffs are understood. Clearly state the assumptions needed to obtain a model price.
Compound options	Move to an optional advanced lesson. They don’t need to anchor the core curriculum.
Five-year purchasing simulation	Replace with an original capstone. Compare structures for a specific LC deal using calculations developed throughout the series.
Original three financing lessons	Replace with the expanded financing track.

The resulting structure could be:
Part	Sequence
Shared foundation	Compute economics → cash-flow timing and present value → term quotes and implied curves
Financing a deal	Prepayments → financeable offtake → debt capacity → receivables and collateral → renewal risk → hardware residuals → waterfalls → deployment delays
Managing market risk	Forwards and swaps → benchmark and basis risk → price/quantity uncertainty → calls and puts → option valuation → collateral liquidity
Advanced electives	Compound options, floors with shared upside, power exposure, interest-rate hedging
Capstone	Structure and stress-test a compute transaction from buyer, operator, and financier perspectives

The strongest way to make it your own is to change the organizing question: “What decision does Liquid Compute need to help someone make?”

For example, “How much could we lend against this contract?” naturally leads to coverage ratios, customer risk, reserves, and repayment schedules. That gives the series an independent purpose while preserving useful, properly attributed material from the post.
does the new structure cover things like an oem deposit funding. where i have offtake but that prepayment doesn't come in until the gpus are ordered but the gpu order requires a deposit so there is a funding mismatch.

Yes, but it deserves an explicit lesson: “Funding the gap between an OEM deposit and customer prepayment.” It sits between prepayment financing and deployment funding.

Your example has a specific sequence:

    You sign an offtake agreement.
    The OEM requires a deposit to accept the GPU order.
    The customer’s prepayment becomes payable only after the order is placed.
    You need temporary funding to get from step 2 to step 3.

That creates a bridge-financing problem. The intended repayment source is the customer prepayment, rather than years of operating revenue.

The notebook could explore:
Input or event	What the reader learns
OEM deposit amount and date	How much cash must be available initially
Customer prepayment amount and expected receipt date	Whether it covers the bridge and how long funding is needed
Interest, fees, and existing cash	Total financing cost and required equity
Customer payment delay	Additional interest and liquidity needs
Customer payment conditions remain unmet	Why a signed offtake is not the same as an unconditional receivable
OEM cancellation or deposit refund	What cash might be recovered if the transaction fails

The crucial teaching distinction is between a timing mismatch and an unresolved payment condition. If the customer owes the prepayment once an accepted order is documented, that differs from payment still depending on financing approval, delivery, or acceptance testing.

I’d revise the financing sequence to:

Prepayment economics → OEM deposit bridge → financeable offtake → debt capacity → deployment funding.

Keep the OEM bridge and deployment lessons separate: the first funds an order-triggered payment gap; the second funds the longer period until equipment is delivered, accepted, and earning revenue.


## Notebook 3 implementation direction update — 2026-09-27

The accepted implementation uses a concise core with one independent menu, overlap diagram, interactive block chart, reconstruction table, and three fixed experiments. Discounting and the source-menu reproduction are optional. The user selected the market-risk path for Notebook 4, “The Tenor Trade: Buying Long, Selling Short,” now M1. Existing market-risk lessons shift to M2–M7. This later decision supersedes the earlier direct transition from Notebook 3 to forwards and swaps; financing remains accessible after Notebook 2.


## Direction update — 2026-09-29

The user requested publication to `https://github.com/zach189/education.git`, a README with Colab links and Ready/WIP sections, package installation at the beginning of each notebook, and execution of all notebooks with outputs saved. This supersedes earlier no-execution and deferred-Colab-setup instructions. Ready includes notebooks 1–4 and the options lessons M5, M6, and E1. The canonical roadmap tracks the resulting verification status.
