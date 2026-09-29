# Liquid Compute teaching project

## Publication and execution update — 2026-09-29

The user authorized running every notebook, saving outputs, adding GitHub package installation in Colab, and publishing to `zach189/education`. All 26 existing notebooks passed fresh-kernel execution locally and have saved outputs. The first code cell installs the package in Colab; local execution reuses `.venv`. All 740 tests, Ruff checks, formatting checks, and mypy passed. Live Colab interaction remains unverified.

**Ready:** notebooks 1–4 (4 is M1), M5 calls and puts, M6 option valuation, and the compute lab financing case study. **WIP:** all other existing lessons, including E1 compound options. C1 remains planned. Release readiness is the user's teaching selection, separate from execution success. See the [notebook index](README.md) for Colab links and the [canonical roadmap](notebooks/README.md) for prerequisites.

Earlier dated execution deferrals below are historical and superseded by this update. Live-presentation checks remain pending where not already recorded as complete.

## Project direction and business boundaries

- The organizing question is: “What decision does Liquid Compute need to help a buyer, operator, or financier make?” Build an independent compute-finance curriculum and reusable calculator library, not a reproduction of one article.
- `notebooks/README.md` is the canonical roadmap. Keep foundation notebooks 1–3, Financing F1–F9, Market Risk M1–M7, Electives E1–E6, and Capstone C1 consistent across documentation. Foundation notebooks 1–3 and F1 are implemented and verified locally. F2–F9 have notebook source, calculators, tests and coherence reviews; execution and release status are recorded in the canonical roadmap. Market-risk and elective implementation is tracked per lesson in the canonical roadmap; the capstone remains planned. Track IDs do not imply notebook files already exist.
- Prioritize financing; F1 can start after Notebook 2, while Notebook 3 is the prerequisite for M1, the tenor trade; forwards and swaps follow as M2. Compound options are an optional elective. The capstone is an original hypothetical transaction viewed by buyer, operator, and financier; real deal assumptions/data must be supplied separately.
- Explicitly distinguish a capacity reseller from a GPU-owning operator/project. Do not assign hardware collateral or resale proceeds to a reseller. For OEM deposits, identify actual contractual/refund rights rather than assuming delivery or existing hardware collateral. Leasing does not automatically transfer ownership.
- Keep the OEM deposit bridge (F2) separate from deployment funding (F5). In F2, the intended repayment source is an order-triggered customer prepayment; distinguish an unconditional payment arriving late from conditions that have not yet been met. A signed offtake is not automatically an unconditional receivable.
- Attribute external methods and examples. Use independent main scenarios; source-specific reproductions belong in clearly cited optional material. Treat industry disclosures in imported planning discussions as research leads, and verify primary sources before repeating specific facility terms as facts.
- Preserve `chat.md` as history, clearly marking superseded direction. Update the canonical roadmap and link other documents to it rather than maintaining conflicting full roadmaps.

## Purpose and teaching style

- Build a concise Python notebook series for readers who know basic Python but are new to compute financing and derivatives. Aim for 10–15 minutes per lesson.
- Write for adult newcomers: use direct business examples, define financial terms when introduced, and explain the reasoning without assuming finance knowledge. Keep the tone professional and approachable. Avoid child-oriented analogies, baby talk and replacing useful terminology with toys, lemonade or cash jars.
- Keep explanations, worked examples, teaching decisions, and displayed charts/controls in notebooks. Put repetitive rendering and widget mechanics in `liquid_compute.education`. Show core arithmetic directly before calling the corresponding calculation function.
- Follow each experiment’s code/results with a short Markdown explanation of what changed, why it happened, and the business takeaway. Keep worked explanations tied to the stated example inputs.
- Treat payment dates as explicit hypothetical contract assumptions, not industry conventions. Distinguish invoice dates from cash settlement.
- Clearly distinguish sourced facts, hypothetical assumptions, and derived calculations. Keep financial units explicit and cite primary sources near supported claims.

## Reusable calculations

- Design stable calculations to become reusable Liquid Compute tools. Place them in a small Python package named `liquid_compute`, separate from the optional `liquid_compute.education` presentation module.
- Keep the existing foundation calculations and extend the package only as implemented lessons require. Do not build speculative pricing frameworks or tool integrations.
- Prefer small, pure functions. Use typed dataclasses for structured results or inputs when helpful, without unnecessary classes or abstraction.
- Fully annotate reusable functions and public interfaces using modern Python syntax compatible with the existing Python 3.10 environment (for example, `float | None` and built-in generic types).
- Make units explicit in names and docstrings: for example, `gpu_count`, `rental_usd_per_gpu_hour`, and `utilization_fraction`.
- Document assumptions and allowable ranges. Type hints do not validate units or values: add runtime checks for invalid types, nonfinite values, and invalid ranges.
- Distinguish contractual cash-flow calculations from model-dependent valuations. Document valuation assumptions when introduced; do not present model outputs as contractually determined amounts or market quotes.
- Notebook 1 calculates monthly contractual revenue and rental expense, not dated cash-flow schedules or valuations. Payment timing belongs to the next lesson.

## Environment and tooling

- Reuse the existing `.venv`; do not create another environment. It currently uses Python 3.10.11.
- Use `pyproject.toml` for packaging and tool configuration. Keep runtime dependencies minimal; notebook display dependencies do not belong in the calculation package's runtime requirements.
- Follow established repository tooling. With no existing tooling, use Ruff for linting/formatting, mypy as the sole type checker, and pytest for meaningful calculation tests.
- Preserve entered input precision when initializing controls. Keep explorers self-contained and independent of notebook globals. Save baseline and worked-experiment outputs for reading like a book. Prediction prompts are optional; do not hide answers or require execution to read the lesson.
- Keep diagnostic code, assertions, and automated boundary checks in the test suite, not in educational notebook cells.
- Test contractual behavior, independently calculated examples, boundaries, invalid inputs, and useful invariants. Also validate notebook format and fresh-kernel execution.
- Keep notebooks in standard format without absolute paths or external data dependencies. Retain editable cells as a fallback for widgets. Support Colab package setup and links as authorized on 2026-09-29. Keep local fresh-kernel execution distinct from live Colab verification.

## Planning documents

- `PLANNING.md` indexes every unfinished lesson and records shared conventions, source research gates, and calculation ownership. Read its overlap boundaries and the specific lesson plan before implementation. `PLAN_04.md` belongs to M1; other track plans use their IDs.
- F1 is implemented: reuse its verified notebook and loan engine instead of generating a second implementation. Its approved scope excludes customer-prepayment financing, which belongs to F2.
- Plan links are not notebook availability. Mark a lesson implemented only after its tests, fresh-kernel execution and local presentation checks pass. Keep shared calculations under the owner identified in the planning index; later lessons should reuse them.

## Historical implementation verification scope (2026-09-28; superseded)

The user explicitly requested creating all financing notebooks without running them or requesting repeated execution permissions. For this pass, validate calculation and plotting helpers through headless tests, and check notebook schema, syntax and teaching structure statically. Do not execute notebook cells indirectly through tests. F2 executed once before this instruction; its later edits and F3–F9 are not execution-verified. Fresh-kernel execution, saved outputs for F3–F9 and live Jupyter checks remain deferred, not failed or completed. Preserve this distinction in status reporting. The earlier full acceptance gates apply when notebook execution is authorized again.

The same no-execution verification scope continues for the user-requested M1–M7 and E1–E6 implementation pass. Implement and review each against its individual spec before proceeding; exclude C1. Do not substitute notebook-cell execution in tests for kernel execution.
