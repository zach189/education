"""Optional notebook presentation; contract arithmetic stays in economics.

Importing this module does not load Matplotlib, IPython, or ipywidgets. Install
liquid-compute[notebook] to use its display helpers. Prices and GPU-hours follow
compute_monthly_economics; these helpers neither forecast nor value contracts.
"""

from collections.abc import Callable, Mapping, Sequence
from typing import TYPE_CHECKING, Literal, TypedDict

from .bridge_financing import BridgeInputs, BridgeSchedule
from .cashflows import MonthlyCashFlow
from .economics import MonthlyEconomics, compute_monthly_economics
from .financing import FinancedCashFlow, FinancingInputs, LoanCashFlow
from .forward_curves import ImpliedRentalBlock, RentalQuote

if TYPE_CHECKING:
    from ipywidgets import VBox
    from matplotlib.figure import Figure

    from .lab_financing import LabInputs
    from .risk_statistics import MonthlyPrice
    from .tenor_trade import ResellerCommitmentRow
    from .workload_costs import UsefulOutputCosts


class _Inputs(TypedDict):
    gpu_count: int
    hours_per_month: float
    rental_usd_per_gpu_hour: float
    customer_usd_per_gpu_hour: float
    utilization_fraction: float


def _results_markdown(result: MonthlyEconomics) -> str:
    margin = (
        "N/A (zero revenue)"
        if result.contribution_margin_fraction is None
        else f"{result.contribution_margin_fraction:.2%}"
    )
    rows = [
        ("Purchased", f"{result.purchased_gpu_hours:,.2f}", "GPU-hours"),
        ("Billed", f"{result.billed_gpu_hours:,.2f}", "GPU-hours"),
        ("Unused", f"{result.unused_gpu_hours:,.2f}", "GPU-hours"),
        ("Revenue", f"{result.revenue_usd:,.2f}", "USD / modeled month"),
        ("Rental expense", f"{result.rental_expense_usd:,.2f}", "USD / modeled month"),
        (
            "Contribution profit",
            f"{result.contribution_profit_usd:,.2f}",
            "USD / modeled month",
        ),
        ("Margin", margin, "% of revenue"),
        (
            "Break-even utilization",
            f"{result.break_even_utilization_fraction:.2%}",
            "billed / purchased hours",
        ),
    ]
    return "| Result | Value | Unit |\n|---|---:|---|\n" + "\n".join(
        f"| {label} | {value} | {unit} |" for label, value, unit in rows
    )


def show_monthly_results(result: MonthlyEconomics) -> None:
    """Display a monthly result with USD, GPU-hour, and percentage labels.

    Requires IPython, not widgets. Display rounding never changes the result.
    Zero-revenue margin displays as N/A rather than a misleading zero percent.
    """
    from IPython.display import Markdown, display

    display(Markdown(_results_markdown(result)))


def _profit_figure(inputs: _Inputs) -> "Figure":
    import matplotlib.pyplot as plt
    from matplotlib.ticker import StrMethodFormatter

    current = compute_monthly_economics(**inputs)
    percentages = list(range(101))
    profits = []
    for percent in percentages:
        scenario = inputs.copy()
        scenario["utilization_fraction"] = percent / 100
        profits.append(compute_monthly_economics(**scenario).contribution_profit_usd)
    fig, ax = plt.subplots(figsize=(8, 4.2), layout="constrained")
    ax.plot(
        percentages,
        profits,
        color="#245a81",
        linewidth=2.5,
        label="Contribution profit",
    )
    ax.axhline(0, color="#555555", linewidth=1)
    ax.scatter(
        inputs["utilization_fraction"] * 100,
        current.contribution_profit_usd,
        s=75,
        color="#c66a21",
        zorder=4,
        label="Current assumptions",
    )
    threshold = current.break_even_utilization_fraction * 100
    if threshold <= 100:
        ax.axvline(
            threshold,
            color="#555555",
            linestyle="--",
            label=f"Break-even: {threshold:.2f}%",
        )
        ax.scatter(threshold, 0, marker="D", color="#555555", zorder=3)
    else:
        ax.text(
            0.02,
            0.96,
            f"Break-even: {threshold:.2f}% — outside available capacity",
            transform=ax.transAxes,
            va="top",
            fontsize=10,
        )
    ax.set(
        xlim=(0, 100),
        xlabel="Billed utilization (%)",
        ylabel="Monthly contribution profit ($)",
        title="Unused hours still incur rental expense",
    )
    ax.yaxis.set_major_formatter(StrMethodFormatter("${x:,.0f}"))
    ax.grid(alpha=0.18)
    ax.legend(loc="lower right", fontsize=9)
    return fig


def plot_profit_by_utilization(
    *,
    gpu_count: int,
    hours_per_month: float,
    rental_usd_per_gpu_hour: float,
    customer_usd_per_gpu_hour: float,
    utilization_fraction: float,
) -> "Figure":
    """Display and return a static monthly-profit chart; no widgets required.

    Inputs use the units and validated ranges of compute_monthly_economics.
    Utilization is a fraction in [0, 1]; only axis labels convert to percent.
    Keep the feasible axis at 0–100% and annotate infeasible break-even ratios.
    Requires Matplotlib and IPython. The returned figure is closed from pyplot's
    registry after display to avoid duplicate notebook output and resource leaks.
    """
    import matplotlib.pyplot as plt
    from IPython.display import display

    figure = _profit_figure(
        _Inputs(
            gpu_count=gpu_count,
            hours_per_month=hours_per_month,
            rental_usd_per_gpu_hour=rental_usd_per_gpu_hour,
            customer_usd_per_gpu_hour=customer_usd_per_gpu_hour,
            utilization_fraction=utilization_fraction,
        )
    )
    try:
        display(figure)
    finally:
        plt.close(figure)
    return figure


def explore_monthly_economics(
    *,
    gpu_count: int,
    hours_per_month: float,
    rental_usd_per_gpu_hour: float,
    customer_usd_per_gpu_hour: float,
    utilization_fraction: float,
) -> "VBox | None":
    """Display independent controls, chart, and results together; return the panel.

    Inputs follow compute_monthly_economics, including runtime validation.
    The utilization slider preserves the supplied fraction at initialization;
    dragging uses one-percentage-point steps. Each panel owns its callbacks and
    output, without notebook globals or dependencies on an earlier chart.

    Invalid edits replace the output with a corrective message, not stale data.
    If ipywidgets is missing, display an editable-cell fallback and return None.
    IPython and Matplotlib are required. Frontend rendering support is separate
    from package availability; use editable assumptions if controls do not render.
    """
    inputs = _Inputs(
        gpu_count=gpu_count,
        hours_per_month=hours_per_month,
        rental_usd_per_gpu_hour=rental_usd_per_gpu_hour,
        customer_usd_per_gpu_hour=customer_usd_per_gpu_hour,
        utilization_fraction=utilization_fraction,
    )
    compute_monthly_economics(**inputs)
    try:
        import ipywidgets as widgets
    except ImportError:
        print(
            "Widgets unavailable: edit the assumptions cell and rerun the results and chart."
        )
        return None

    import matplotlib.pyplot as plt
    from IPython.display import clear_output, display

    count_control = widgets.IntText(value=gpu_count, description="GPUs")
    hours_control = widgets.FloatText(value=hours_per_month, description="Hours/GPU")
    rental_control = widgets.FloatText(
        value=rental_usd_per_gpu_hour, description="Rent $/GPU-h"
    )
    customer_control = widgets.FloatText(
        value=customer_usd_per_gpu_hour, description="Sale $/GPU-h"
    )
    usage_control = widgets.FloatSlider(
        value=utilization_fraction,
        min=0,
        max=1,
        step=0.01,
        description="Billed %",
        readout_format=".2%",
        continuous_update=False,
    )
    output = widgets.Output()

    def update(change: object = None) -> None:
        current_inputs = _Inputs(
            gpu_count=count_control.value,
            hours_per_month=hours_control.value,
            rental_usd_per_gpu_hour=rental_control.value,
            customer_usd_per_gpu_hour=customer_control.value,
            utilization_fraction=usage_control.value,
        )
        with output:
            clear_output(wait=True)
            try:
                result = compute_monthly_economics(**current_inputs)
                figure = _profit_figure(current_inputs)
            except (TypeError, ValueError) as error:
                print(f"Check the inputs: {error}")
                return
            try:
                display(figure)
                show_monthly_results(result)
            finally:
                plt.close(figure)

    controls = [
        count_control,
        hours_control,
        rental_control,
        customer_control,
        usage_control,
    ]
    for control in controls:
        control.observe(update, names="value")
    panel = widgets.VBox([*controls, output])
    display(panel)
    update()
    return panel


# Cash-flow lesson display helpers use the same optional dependency boundary.
def show_cash_flow_schedule(schedule: "Sequence[MonthlyCashFlow]") -> None:
    """Show every relative month and both service and cash USD amounts."""
    from IPython.display import Markdown, display

    header = "| Month t | Service revenue | Service expense | Receipts | Payments | Net cash | Cumulative cash |\n|---:|---:|---:|---:|---:|---:|---:|\n"
    rows = [
        f"| {r.month_offset} | "
        + " | ".join(
            f"{v:,.2f}"
            for v in (
                r.service_revenue_usd,
                r.service_rental_expense_usd,
                r.customer_receipts_usd,
                r.supplier_payments_usd,
                r.net_cash_flow_usd,
                r.cumulative_cash_usd,
            )
        )
        + " |"
        for r in schedule
    ]
    display(
        Markdown(
            "**All amounts in USD; t = months from commencement.**\n\n"
            + header
            + "\n".join(rows)
        )
    )


def show_payment_comparison(
    schedules: "Mapping[str, Sequence[MonthlyCashFlow]]",
    *,
    annual_discount_rate: float,
    include_supplier_pv: bool = True,
) -> None:
    """Compare service/funding USD amounts, optionally adding supplier-cost PV.

    Set include_supplier_pv=False before teaching valuation; the rate is then
    unused and no discounting is performed.
    """
    from IPython.display import Markdown, display

    from .cashflows import summarize_cash_flow_schedule
    from .discounting import present_value_usd

    summaries = [summarize_cash_flow_schedule(s) for s in schedules.values()]
    values = [
        ("Service revenue", [s.service_revenue_usd for s in summaries]),
        ("Rental expense", [s.service_rental_expense_usd for s in summaries]),
        (
            "Contribution profit (undiscounted)",
            [s.contribution_profit_usd for s in summaries],
        ),
        (
            "Maximum funding (undiscounted)",
            [s.maximum_funding_requirement_usd for s in summaries],
        ),
    ]
    if include_supplier_pv:
        values.append(
            (
                "PV of supplier payments",
                [
                    present_value_usd(
                        [r.supplier_payments_usd for r in schedule],
                        annual_discount_rate=annual_discount_rate,
                    )
                    for schedule in schedules.values()
                ],
            )
        )
    text = (
        "| Measure (USD) | "
        + " | ".join(schedules)
        + " |\n|---|"
        + "---:|" * len(schedules)
        + "\n"
    )
    text += "\n".join(
        "| " + label + " | " + " | ".join(f"{v:,.2f}" for v in numbers) + " |"
        for label, numbers in values
    )
    display(Markdown(text))


def plot_cumulative_cash(
    schedules: "Mapping[str, Sequence[MonthlyCashFlow]]", *, service_months: int
) -> "Figure":
    """Display USD balances after each month's net flows, including t=0 jumps.

    Accept nonempty schedules returned by build_cash_flow_schedule. Mark service
    end and each minimum balance; never discount these cash balances.
    """
    import matplotlib.pyplot as plt
    from IPython.display import display
    from matplotlib.ticker import MaxNLocator, StrMethodFormatter

    from .cashflows import _integer, summarize_cash_flow_schedule

    _integer("service_months", service_months, minimum=1)
    if not schedules or any(not s for s in schedules.values()):
        raise ValueError("at least one nonempty schedule is required")
    summaries = [summarize_cash_flow_schedule(s) for s in schedules.values()]
    fig, ax = plt.subplots(figsize=(8, 4.5), layout="constrained")
    for (label, schedule), summary in zip(schedules.items(), summaries):
        times = [0] + [r.month_offset for r in schedule]
        balances = [0.0] + [r.cumulative_cash_usd for r in schedule]
        (line,) = ax.step(
            times,
            balances,
            where="post",
            label=f"{label} — funding ${summary.maximum_funding_requirement_usd:,.0f}",
            linewidth=2,
        )
        index = balances.index(min(balances))
        ax.scatter(
            times[index], balances[index], marker="D", color=line.get_color(), zorder=3
        )
    ax.axhline(0, color="#555555", linewidth=1)
    ax.axvline(service_months, color="#777777", linestyle="--", label="Service ends")
    ax.set(
        xlabel="Months from commencement (t)",
        ylabel="Cumulative cash before financing (USD)",
        title="Payment timing changes the funding requirement",
    )
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(StrMethodFormatter("${x:,.0f}"))
    ax.legend(loc="best", fontsize=8)
    ax.grid(alpha=0.18)
    try:
        display(fig)
    finally:
        plt.close(fig)
    return fig


def explore_payment_terms(
    *,
    monthly_revenue_usd: float,
    base_monthly_rental_expense_usd: float,
    service_months: int,
    customer_payment_lag_months: int,
    annual_discount_rate: float,
    prepayment_discount_fraction: float,
    supplier_payment_timing: Literal[
        "monthly_in_advance", "monthly_in_arrears"
    ] = "monthly_in_advance",
    customer_terms: Literal["monthly_in_arrears", "upfront"] = "monthly_in_arrears",
) -> "VBox | None":
    """Show independent timing/lag/rate/discount controls, comparison table, and chart.

    Inputs follow build_cash_flow_schedule and discount_factor. Exact fraction
    values are retained. Missing widgets print an editable-cell fallback.
    Optional rates are valuation assumptions, never cash charges.
    Customer upfront collects the full contract at t=0 before supplier payment;
    set lag to zero for this scenario. Timing inputs follow the schedule function.
    """
    from .cashflows import build_cash_flow_schedule
    from .discounting import break_even_prepayment_discount_fraction

    build_cash_flow_schedule(
        monthly_revenue_usd=monthly_revenue_usd,
        base_monthly_rental_expense_usd=base_monthly_rental_expense_usd,
        service_months=service_months,
        customer_payment_lag_months=customer_payment_lag_months,
        customer_terms=customer_terms,
        supplier_terms="upfront",
        prepayment_discount_fraction=prepayment_discount_fraction,
    )
    break_even_prepayment_discount_fraction(
        service_months=service_months,
        annual_discount_rate=annual_discount_rate,
        payment_timing=supplier_payment_timing,
    )
    try:
        import ipywidgets as widgets
    except ImportError:
        print(
            "Widgets unavailable: edit the assumptions and rerun the comparison cells."
        )
        return None
    from IPython.display import clear_output, display

    lag = widgets.IntText(value=customer_payment_lag_months, description="Lag (months)")
    rate = widgets.FloatText(value=annual_discount_rate, description="Annual rate")
    discount = widgets.FloatText(
        value=prepayment_discount_fraction, description="Discount"
    )
    timing = widgets.Dropdown(
        options=[
            ("Month-end", "monthly_in_arrears"),
            ("Month-start", "monthly_in_advance"),
        ],
        value=supplier_payment_timing,
        description="Supplier",
    )
    customer = widgets.Dropdown(
        options=[
            ("Monthly after service", "monthly_in_arrears"),
            ("Full contract upfront", "upfront"),
        ],
        value=customer_terms,
        description="Customer",
    )
    output = widgets.Output()

    def update(change: object = None) -> None:
        with output:
            clear_output(wait=True)
            try:
                threshold = break_even_prepayment_discount_fraction(
                    service_months=service_months,
                    annual_discount_rate=rate.value,
                    payment_timing=timing.value,
                )
                monthly = build_cash_flow_schedule(
                    monthly_revenue_usd=monthly_revenue_usd,
                    base_monthly_rental_expense_usd=base_monthly_rental_expense_usd,
                    service_months=service_months,
                    customer_payment_lag_months=lag.value,
                    customer_terms=customer.value,
                    supplier_terms=timing.value,
                )
                upfront = build_cash_flow_schedule(
                    monthly_revenue_usd=monthly_revenue_usd,
                    base_monthly_rental_expense_usd=base_monthly_rental_expense_usd,
                    service_months=service_months,
                    customer_payment_lag_months=lag.value,
                    customer_terms=customer.value,
                    supplier_terms="upfront",
                    prepayment_discount_fraction=discount.value,
                )
                label = (
                    "Monthly at start"
                    if timing.value == "monthly_in_advance"
                    else "Monthly at end"
                )
                scenarios = {label: monthly, "Supplier upfront": upfront}
                show_payment_comparison(scenarios, annual_discount_rate=rate.value)
                print(f"Break-even prepayment discount: {threshold:.4%}")
                plot_cumulative_cash(scenarios, service_months=service_months)
            except (TypeError, ValueError) as error:
                clear_output(wait=True)
                print(f"Check the inputs: {error}")

    for control in [lag, rate, discount, timing, customer]:
        control.observe(update, names="value")
    panel = widgets.VBox(
        [
            widgets.HTML("Rates are fractions: 0.12 = 12%; discount 0.08 = 8%."),
            lag,
            rate,
            discount,
            timing,
            customer,
            output,
        ]
    )
    display(panel)
    update()
    return panel


def plot_payment_present_value(
    *, payment_usd: float, annual_discount_rate: float, horizon_months: int = 12
) -> "Figure":
    """Plot one positive USD payment at alternative monthly dates, not a schedule.

    The horizontal line is the unchanged contractual amount. The other line
    values that amount at t=0 using a finite, nonnegative effective annual rate.
    Horizon is a positive integer. Validation follows the calculation modules.
    Requires Matplotlib/IPython; closes the displayed figure's pyplot registry.
    """
    import matplotlib.pyplot as plt
    from IPython.display import display
    from matplotlib.ticker import MaxNLocator, StrMethodFormatter

    from .cashflows import _integer
    from .discounting import discount_factor
    from .economics import _positive_number

    amount = _positive_number("payment_usd", payment_usd)
    horizon = _integer("horizon_months", horizon_months, minimum=1)
    months = list(range(horizon + 1))
    values = [
        amount * discount_factor(annual_discount_rate=annual_discount_rate, months=t)
        for t in months
    ]
    fig, ax = plt.subplots(figsize=(8, 4.2), layout="constrained")
    ax.plot(
        months,
        [amount] * len(months),
        linestyle="--",
        color="#777777",
        label="Actual payment (unchanged)",
    )
    ax.plot(
        months,
        values,
        color="#245a81",
        linewidth=2.5,
        label=f"Value today at {annual_discount_rate:.2%} per year",
    )
    ax.scatter([0, horizon], [values[0], values[-1]], color="#245a81", zorder=3)
    ax.annotate(
        f"USD {values[-1]:,.2f} today",
        (horizon, values[-1]),
        xytext=(-8, -14),
        textcoords="offset points",
        ha="right",
        va="top",
        color="#245a81",
    )
    span = max(amount - values[-1], amount * 0.05)
    ax.set(
        xlabel="When the single payment is due (months from today)",
        ylabel="Amount (USD; zoomed scale)",
        ylim=(max(0.0, values[-1] - span * 0.4), amount + span * 0.2),
        title="Same payment, different payment date",
    )
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(StrMethodFormatter("${x:,.0f}"))
    ax.grid(alpha=0.18)
    ax.legend(loc="lower left")
    try:
        display(fig)
    finally:
        plt.close(fig)
    return fig


# Rental-curve presentation accepts calculated records; no valuation is done here.
def show_rental_quotes(quotes: "Sequence[RentalQuote]") -> None:
    """Display known package rates and visibly missing standard teaching tenors."""
    from IPython.display import Markdown, display

    prices = {q.term_months: q.rental_usd_per_gpu_hour for q in quotes}
    tenors = sorted({12, 36, 60} | prices.keys())
    rows = [
        f"| {t} | {prices[t]:.4f} |" if t in prices else f"| {t} | Not quoted |"
        for t in tenors
    ]
    display(
        Markdown(
            "| Contract length (months) | Flat quote (USD/GPU-hour) |\n|---:|---:|\n"
            + "\n".join(rows)
        )
    )


def plot_rental_periods(quotes: "Sequence[RentalQuote]") -> "Figure":
    """Show same-start delivery periods for validated, nonempty rental quotes."""
    import matplotlib.pyplot as plt
    from IPython.display import display

    fig, ax = plt.subplots(figsize=(8, 3), layout="constrained")
    for i, q in enumerate(quotes):
        ax.barh(i, q.term_months, height=0.5, color="#245a81", alpha=0.8)
        ax.text(
            q.term_months / 2,
            i,
            f"{q.rental_usd_per_gpu_hour:.2f}",
            ha="center",
            va="center",
            color="white",
        )
    ax.set(
        yticks=list(range(len(quotes))),
        yticklabels=[f"{q.term_months}-month package" for q in quotes],
        xlabel="Delivery time (months from commencement)",
        title="Every package starts today\nBar labels: flat quoted rate (USD/GPU-hour)",
    )
    ax.set_xticks([0] + [q.term_months for q in quotes])
    ax.invert_yaxis()
    try:
        display(fig)
    finally:
        plt.close(fig)
    return fig


def _blocks_markdown(scenarios: "Mapping[str, Sequence[ImpliedRentalBlock]]") -> str:
    text = "| Scenario | Delivery months | Implied block rate (USD/GPU-hour) |\n|---|---|---:|\n"
    nonpositive = False
    for label, blocks in scenarios.items():
        for b in blocks:
            rate = b.implied_usd_per_gpu_hour
            shown = 0.0 if abs(rate) < 1e-10 else rate
            text += f"| {label} | {b.start_month_offset + 1}–{b.end_month_offset} | {shown:.4f} |\n"
            nonpositive |= rate <= 1e-10
    if nonpositive:
        text += "\nA zero or negative allocation may reflect package-level discounts. It is not a separately offered price or proof of executable arbitrage."
    return text


def show_implied_blocks(
    scenarios: "Mapping[str, Sequence[ImpliedRentalBlock]]",
) -> None:
    """Display signed block rates with actual boundaries; never invent sub-blocks."""
    from IPython.display import Markdown, display

    display(Markdown(_blocks_markdown(scenarios)))


def show_curve_reconstruction(
    rows: Sequence[tuple[int, float, float]], *, measure: str = "Rate (USD/GPU-hour)"
) -> None:
    """Render precomputed (term months, original, reconstructed) values."""
    from IPython.display import Markdown, display

    text = f"**{measure}**\n\n| Package months | Original | Reconstructed |\n|---:|---:|---:|\n"
    text += "\n".join(
        f"| {t} | {original:,.4f} | {reconstructed:,.4f} |"
        for t, original, reconstructed in rows
    )
    display(Markdown(text))


def _rental_block_figure(blocks: "Sequence[ImpliedRentalBlock]") -> "Figure":
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4), layout="constrained")
    edges = [blocks[0].start_month_offset] + [b.end_month_offset for b in blocks]
    rates = [b.implied_usd_per_gpu_hour for b in blocks]
    ax.stairs(rates, edges, baseline=None, color="#245a81", linewidth=2.5)
    for b in blocks:
        rate = b.implied_usd_per_gpu_hour
        shown = 0.0 if abs(rate) < 1e-10 else rate
        ax.annotate(
            f"{shown:.2f}",
            ((b.start_month_offset + b.end_month_offset) / 2, rate),
            xytext=(0, -10 if shown < 0 else 8),
            textcoords="offset points",
            ha="center",
            va="top" if shown < 0 else "bottom",
        )
    ax.axhline(0, color="#777777", linewidth=1)
    ax.set(
        xticks=edges,
        xlabel="Delivery time (months from commencement)",
        ylabel="Implied block rate (USD/GPU-hour)",
        title="Implied block rates; flat within each block assumed",
    )
    ax.margins(y=0.25)
    ax.grid(alpha=0.15)
    return fig


def explore_rental_quotes(
    quotes: "Sequence[RentalQuote]", *, delivery_hours_per_gpu: Sequence[float]
) -> "VBox | None":
    """Show editable quote controls with ordinary saved table/chart outputs.

    Input validation follows imply_rental_blocks. Controls preserve exact prices;
    a missing tenor gets no invented control or quote. Each instance owns display
    handles and callbacks. Invalid edits replace both outputs with a message.
    Without widgets, still render the complete static baseline and return None.
    """
    import matplotlib.pyplot as plt
    from IPython.display import Markdown, display

    from .forward_curves import RentalQuote, imply_rental_blocks

    source = tuple(quotes)
    hours = tuple(delivery_hours_per_gpu)
    blocks = imply_rental_blocks(source, delivery_hours_per_gpu=hours)
    try:
        import ipywidgets as widgets
    except ImportError:
        show_implied_blocks({"Current menu": blocks})
        fig = _rental_block_figure(blocks)
        try:
            display(fig)
        finally:
            plt.close(fig)
        print("Widgets unavailable: edit the rental menu and rerun this cell.")
        return None
    controls = [
        widgets.FloatText(
            value=q.rental_usd_per_gpu_hour,
            description=f"{q.term_months} months",
            style={"description_width": "initial"},
        )
        for q in source
    ]
    panel = widgets.VBox(controls)
    display(panel)
    table_handle = display(
        Markdown(_blocks_markdown({"Current menu": blocks})), display_id=True
    )
    fig = _rental_block_figure(blocks)
    try:
        chart_handle = display(fig, display_id=True)
    finally:
        plt.close(fig)

    def update(change: object = None) -> None:
        try:
            current = tuple(
                RentalQuote(q.term_months, c.value) for q, c in zip(source, controls)
            )
            updated = imply_rental_blocks(current, delivery_hours_per_gpu=hours)
        except (TypeError, ValueError) as error:
            message = Markdown(f"Check the inputs: {error}")
            table_handle.update(message)
            chart_handle.update(Markdown("Correct the inputs to restore the curve."))
            return
        table_handle.update(Markdown(_blocks_markdown({"Current menu": updated})))
        figure = _rental_block_figure(updated)
        try:
            chart_handle.update(figure)
        finally:
            plt.close(figure)

    for control in controls:
        control.observe(update, names="value")
    return panel


# F1: rendering consumes the financing module's validated calculations.
def show_loan_schedule(schedule: "Sequence[LoanCashFlow]") -> None:
    """Render every monthly debt boundary, including the time-zero draw/fee."""
    from IPython.display import Markdown, display

    text = "All amounts in USD; payments are positive.\n\n| Month t | Opening debt | Draw | Interest | Principal | Fee | Closing debt |\n|---:|---:|---:|---:|---:|---:|---:|\n"
    for r in schedule:
        text += f"| {r.month_offset} | {r.opening_debt_usd:,.2f} | {r.loan_draw_usd:,.2f} | {r.interest_usd:,.2f} | {r.principal_repayment_usd:,.2f} | {r.fee_usd:,.2f} | {r.closing_debt_usd:,.2f} |\n"
    display(Markdown(text))


def show_financing_schedule(schedule: "Sequence[FinancedCashFlow]") -> None:
    """Display procurement and financing movements, then cumulative cash/debt."""
    from IPython.display import Markdown, display

    text = "Cash movements (USD), before owner funding.\n\n| Month t | Supplier | Customer | Loan draw | Interest | Principal | Fee | Net cash |\n|---:|---:|---:|---:|---:|---:|---:|---:|\n"
    for r in schedule:
        text += f"| {r.month_offset} | {r.supplier_payments_usd:,.2f} | {r.customer_receipts_usd:,.2f} | {r.loan_proceeds_usd:,.2f} | {r.interest_usd:,.2f} | {r.principal_repayments_usd:,.2f} | {r.fees_usd:,.2f} | {r.net_cash_flow_usd:,.2f} |\n"
    text += "\nBalances (USD). Negative cash is a funding need, not an assumed overdraft.\n\n| Month t | Cumulative cash | Outstanding debt |\n|---:|---:|---:|\n"
    for r in schedule:
        text += f"| {r.month_offset} | {r.cumulative_cash_usd:,.2f} | {r.closing_debt_usd:,.2f} |\n"
    display(Markdown(text))


def _financing_comparison_markdown(
    scenarios: "Mapping[str, Sequence[FinancedCashFlow]]",
    *,
    annual_discount_rate: float,
) -> str:
    from .discounting import present_value_usd
    from .financing import net_procurement_outflows_usd, summarize_financing_cash_flows

    summaries = [summarize_financing_cash_flows(rows) for rows in scenarios.values()]
    measures = {
        "Total supplier cost": [s.supplier_cost_usd for s in summaries],
        "Total interest and fees": [s.interest_usd + s.fees_usd for s in summaries],
        "Total supplier and financing cost": [s.combined_cost_usd for s in summaries],
        "PV of net procurement-and-financing outflows": [
            present_value_usd(
                net_procurement_outflows_usd(rows),
                annual_discount_rate=annual_discount_rate,
            )
            for rows in scenarios.values()
        ],
        "Initial own cash (t=0)": [s.initial_own_cash_usd for s in summaries],
        "Required initial cash buffer (whole schedule)": [
            s.required_initial_cash_buffer_usd for s in summaries
        ],
    }
    text = (
        f"Amounts in USD; PV uses {annual_discount_rate:.2%} effective annually.\n\n| Measure | "
        + " | ".join(scenarios)
        + " |\n|---|"
        + "---:|" * len(scenarios)
        + "\n"
    )
    for label, values in measures.items():
        text += f"| {label} | " + " | ".join(f"{v:,.2f}" for v in values) + " |\n"
    return text


def show_financing_comparison(
    scenarios: "Mapping[str, Sequence[FinancedCashFlow]]",
    *,
    annual_discount_rate: float,
) -> None:
    """Compare calculated cost, PV and cash needs using one comparison rate."""
    from IPython.display import Markdown, display

    display(
        Markdown(
            _financing_comparison_markdown(
                scenarios, annual_discount_rate=annual_discount_rate
            )
        )
    )


def _financing_cash_figure(
    scenarios: "Mapping[str, Sequence[FinancedCashFlow]]", *, service_months: int
) -> "Figure":
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 4.5), layout="constrained")
    for label, rows in scenarios.items():
        (line,) = ax.step(
            [r.month_offset for r in rows],
            [r.cumulative_cash_usd for r in rows],
            where="post",
            label=label,
        )
        lowest = min(rows, key=lambda r: r.cumulative_cash_usd)
        ax.scatter(
            [lowest.month_offset],
            [lowest.cumulative_cash_usd],
            color=line.get_color(),
            zorder=3,
        )
    ax.axhline(0, color="gray", linewidth=1)
    ax.axvline(service_months, color="gray", linestyle=":", label="Service ends")
    ax.set(
        xlabel="Month boundary t (from commencement)",
        ylabel="Cumulative cash before owner funding (USD)",
        title="Cumulative cash under three payment choices",
    )
    final_month = max(rows[-1].month_offset for rows in scenarios.values())
    ax.set_xticks(
        sorted(
            set(range(0, final_month + 1, max(1, final_month // 12))) | {final_month}
        )
    )
    ax.ticklabel_format(axis="y", style="plain")
    ax.legend(loc="best", fontsize=9)
    ax.grid(alpha=0.15)
    return fig


def explore_prepayment_financing(
    inputs: "FinancingInputs", *, annual_discount_rate: float
) -> "VBox | None":
    """Three exact-valued controls with synchronized widget output and static fallback.

    Inputs are copied. Each explorer owns its controls and display handles.
    Computational validation is delegated to financing, not plotting code.
    """
    import matplotlib.pyplot as plt
    from IPython.display import Markdown, display

    from .financing import compare_prepayment_financing

    source = inputs.copy()
    scenarios = compare_prepayment_financing(**source)
    table = _financing_comparison_markdown(
        scenarios, annual_discount_rate=annual_discount_rate
    )
    try:
        import ipywidgets as widgets
    except ImportError:
        display(Markdown(table))
        fig = _financing_cash_figure(scenarios, service_months=source["service_months"])
        try:
            display(fig)
        finally:
            plt.close(fig)
        print("Widgets unavailable: edit the assumptions and rerun the cells.")
        return None
    controls = [
        widgets.FloatText(
            value=value, description=label, style={"description_width": "initial"}
        )
        for label, value in [
            ("Supplier discount (fraction)", source["prepayment_discount_fraction"]),
            ("Nominal annual loan rate", source["nominal_annual_interest_rate"]),
            ("Financed fraction", source["financed_fraction"]),
        ]
    ]
    output = widgets.Output()
    panel = widgets.VBox([*controls, output])

    def render(current: FinancingInputs) -> None:
        # Sync output data as widget state: ordinary display-id updates from
        # comm callbacks are not reliably routed to notebook outputs by Jupyter.
        import base64
        from io import BytesIO

        try:
            updated = compare_prepayment_financing(**current)
            text = _financing_comparison_markdown(
                updated, annual_discount_rate=annual_discount_rate
            )
        except (TypeError, ValueError) as error:
            output.outputs = (
                {
                    "output_type": "display_data",
                    "data": {
                        "text/markdown": f"Check the inputs: {error}. Correct them to restore the chart."
                    },
                    "metadata": {},
                },
            )
            return
        figure = _financing_cash_figure(
            updated, service_months=source["service_months"]
        )
        try:
            with BytesIO() as buffer:
                figure.savefig(buffer, format="png", dpi=110)
                png = base64.b64encode(buffer.getvalue()).decode("ascii")
        finally:
            plt.close(figure)
        output.outputs = (
            {
                "output_type": "display_data",
                "data": {"text/markdown": text},
                "metadata": {},
            },
            {"output_type": "display_data", "data": {"image/png": png}, "metadata": {}},
        )

    def update(change: object = None) -> None:
        current = source.copy()
        current["prepayment_discount_fraction"] = controls[0].value
        current["nominal_annual_interest_rate"] = controls[1].value
        current["financed_fraction"] = controls[2].value
        render(current)

    for control in controls:
        control.observe(update, names="value")
    render(source)
    display(panel)
    return panel


def plot_financing_cash(
    scenarios: Mapping[str, Sequence[FinancedCashFlow]], *, service_months: int
) -> "Figure":
    """Display an ordinary saved baseline chart independently of live widgets."""
    import matplotlib.pyplot as plt
    from IPython.display import display

    figure = _financing_cash_figure(scenarios, service_months=service_months)
    try:
        display(figure)
    finally:
        plt.close(figure)
    return figure


def _bridge_markdown(scenarios: "Mapping[str, BridgeSchedule]") -> str:
    from .bridge_financing import event_cash_funding_requirement_usd

    lines = [
        "| Scenario | Customer status at horizon | Interest accrued (USD) | Unpaid debt (USD) | Initial cash buffer (USD) | Ending cash before owner funding (USD) |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for name, result in scenarios.items():
        lines.append(
            f"| {name} | {result.customer_status} | "
            f"{sum(r.accrued_interest_usd for r in result.rows):,.2f} | "
            f"{result.outstanding_debt_usd:,.2f} | "
            f"{event_cash_funding_requirement_usd(result.events):,.2f} | "
            f"{result.rows[-1].cumulative_cash_usd:,.2f} |"
        )
    return "\n".join(lines)


def show_bridge_comparison(scenarios: "Mapping[str, BridgeSchedule]") -> None:
    """Display bridge debt separately from settled cash, all in USD."""
    from IPython.display import Markdown, display

    display(Markdown(_bridge_markdown(scenarios)))


def _bridge_figure(result: "BridgeSchedule") -> "Figure":
    import matplotlib.pyplot as plt
    from matplotlib.ticker import StrMethodFormatter

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.3))
    days = [r.day_offset for r in result.rows]
    axes[0].plot(
        days,
        [r.remaining_principal_usd + r.remaining_interest_usd for r in result.rows],
        marker="o",
    )
    axes[0].set_title("Unpaid debt at event boundaries")
    axes[1].step(
        days, [r.cumulative_cash_usd for r in result.rows], where="post", marker="o"
    )
    axes[1].set_title("Cash before owner funding")
    for ax in axes:
        ax.set_xlabel("Day offset (ACT/365 interest)")
        ax.set_ylabel("USD")
        ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        ax.axhline(0, color="gray", linewidth=0.7)
        ax.grid(alpha=0.2)
    fig.tight_layout()
    return fig


def plot_bridge_cash(result: "BridgeSchedule") -> "Figure":
    """Save an ordinary event-boundary debt/cash chart independently of widgets."""
    import matplotlib.pyplot as plt
    from IPython.display import display

    fig = _bridge_figure(result)
    try:
        display(fig)
    finally:
        plt.close(fig)
    return fig


def explore_deposit_bridge(inputs: "BridgeInputs") -> "VBox | None":
    """Independent exact-valued receipt-day/amount controls; editable fallback.

    Only a satisfied-condition scenario with an explicit receipt is explored.
    Errors replace stale outputs; correcting inputs restores chart and table.
    """
    import matplotlib.pyplot as plt
    from IPython.display import display

    from .bridge_financing import build_deposit_bridge_schedule

    source = inputs.copy()
    baseline = build_deposit_bridge_schedule(**source)
    if source["receipt_day"] is None or not source["condition_met"]:
        raise ValueError("explorer requires a satisfied condition and receipt day")
    try:
        import ipywidgets as widgets
    except ImportError:
        show_bridge_comparison({"Editable scenario": baseline})
        plot_bridge_cash(baseline)
        print("Widgets unavailable: edit the assumptions and rerun the cells.")
        return None
    day = widgets.IntText(
        value=source["receipt_day"],
        description="Receipt day",
        style={"description_width": "initial"},
    )
    amount = widgets.FloatText(
        value=source["prepayment_usd"],
        description="Customer cash (USD)",
        style={"description_width": "initial"},
    )
    output = widgets.Output()
    panel = widgets.VBox([day, amount, output])

    def update(change: object = None) -> None:
        import base64
        from io import BytesIO

        current = source.copy()
        current["receipt_day"] = day.value
        current["prepayment_usd"] = amount.value
        try:
            result = build_deposit_bridge_schedule(**current)
        except (TypeError, ValueError) as error:
            output.outputs = (
                {
                    "output_type": "display_data",
                    "data": {
                        "text/markdown": f"Check the inputs: {error}. Correct them to restore the chart."
                    },
                    "metadata": {},
                },
            )
            return
        fig = _bridge_figure(result)
        try:
            with BytesIO() as buffer:
                fig.savefig(buffer, format="png", dpi=110)
                png = base64.b64encode(buffer.getvalue()).decode("ascii")
        finally:
            plt.close(fig)
        output.outputs = (
            {
                "output_type": "display_data",
                "data": {"text/markdown": _bridge_markdown({"Explorer": result})},
                "metadata": {},
            },
            {"output_type": "display_data", "data": {"image/png": png}, "metadata": {}},
        )

    day.observe(update, names="value")
    amount.observe(update, names="value")
    update()
    display(panel)
    return panel


def show_finance_table(
    headers: Sequence[str], rows: Sequence[Sequence[str | float | int | None]]
) -> None:
    """Compact teaching table. Put units in headers; None displays as N/A."""
    from IPython.display import Markdown, display

    def cell(value: str | float | int | None) -> str:
        if value is None:
            return "N/A"
        if isinstance(value, (int, float)):
            return f"{value:,.2f}"
        return value.replace("|", " / ").replace("\n", " ")

    display(
        Markdown(
            "\n".join(
                [
                    "| " + " | ".join(headers) + " |",
                    "| " + " | ".join("---" for _ in headers) + " |",
                    *("| " + " | ".join(cell(v) for v in row) + " |" for row in rows),
                ]
            )
        )
    )


def plot_finance_series(
    scenarios: Mapping[str, Sequence[float]],
    *,
    title: str,
    ylabel: str = "USD",
    xlabel: str = "Month offset (0 = inception)",
    marker_month: int | None = None,
    stacked: bool = False,
    x_values: Sequence[float] | None = None,
    bar: bool = False,
    x_tick_labels: Sequence[str] | None = None,
) -> "Figure":
    """Plot explicit same-index sequences; no financial calculations in rendering.

    Input sequences include their own time-zero entry. For snapshots, callers
    supply axis labels explicitly. Returns a figure; notebooks display it using
    display(). Lazy imports keep calculations free of presentation dependencies.
    """
    import matplotlib.pyplot as plt
    from matplotlib.ticker import StrMethodFormatter

    from .economics import _finite_number

    if not scenarios or len({len(v) for v in scenarios.values()}) != 1:
        raise ValueError("series must be nonempty with equal lengths")
    data = {
        k: [_finite_number("plot value", v) for v in values]
        for k, values in scenarios.items()
    }
    if not next(iter(data.values())):
        raise ValueError("series must contain observations")
    count = len(next(iter(data.values())))
    x = (
        list(range(count))
        if x_values is None
        else [_finite_number("x value", v) for v in x_values]
    )
    if len(x) != count:
        raise ValueError("x values must match each series length")
    if bar and stacked:
        raise ValueError("choose bars or stacked areas, not both")
    if x_tick_labels is not None and (
        len(x_tick_labels) != count
        or any(not isinstance(v, str) for v in x_tick_labels)
    ):
        raise ValueError("tick labels must be strings matching the series length")
    fig, ax = plt.subplots(figsize=(9, 3.8))
    if stacked:
        ax.stackplot(x, *data.values(), labels=list(data))
    elif bar:
        width = 0.8 / len(data)
        for index, (label, values) in enumerate(data.items()):
            positions = [v + (index - (len(data) - 1) / 2) * width for v in x]
            ax.bar(positions, values, width=width, label=label)
    else:
        for label, values in data.items():
            ax.plot(x, values, label=label, marker="o", markersize=3)
    if marker_month is not None:
        ax.axvline(marker_month, color="gray", linestyle="--", label="Contract expires")
    if x_tick_labels is not None:
        ax.set_xticks(x, x_tick_labels)
    ax.axhline(0, color="gray", linewidth=0.7)
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    ax.grid(alpha=0.2)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.close(fig)
    return fig


def explore_finance_series(
    inputs: Mapping[str, float | str],
    calculate: "Callable[[Mapping[str, float | str]], Mapping[str, Sequence[float]]]",
    *,
    title: str,
    xlabel: str = "Month offset (0 = inception)",
    ylabel: str = "USD",
    marker_month: int | None = None,
    stacked: bool = False,
    x_values: Sequence[float] | None = None,
    bar: bool = False,
    x_tick_labels: Sequence[str] | None = None,
    choices: Mapping[str, Sequence[str]] | None = None,
) -> "VBox | None":
    """Independent exact-value controls for an explicit lesson calculation.

    The callback must close over immutable input snapshots, not notebook globals.
    It receives a new input dict; plotting performs no finance arithmetic.
    Integer initial values use integer controls. Errors replace stale plots.
    Static fallback displays the same figure without requiring widget support.
    """
    import matplotlib.pyplot as plt
    from IPython.display import display

    source = dict(inputs)
    options = {name: tuple(values) for name, values in (choices or {}).items()}
    for name, values in options.items():
        if (
            name not in source
            or not values
            or any(not isinstance(v, str) for v in values)
            or source[name] not in values
        ):
            raise ValueError(
                "choice controls require a supplied value from nonempty string options"
            )
    if any(
        isinstance(value, str) and name not in options for name, value in source.items()
    ):
        raise ValueError("text inputs require declared choices")
    axis_values = None if x_values is None else tuple(x_values)
    axis_labels = None if x_tick_labels is None else tuple(x_tick_labels)
    initial = calculate(source.copy())
    figure = plot_finance_series(
        initial,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        marker_month=marker_month,
        stacked=stacked,
        x_values=axis_values,
        bar=bar,
        x_tick_labels=axis_labels,
    )
    try:
        import ipywidgets as widgets
    except ImportError:
        display(figure)
        print("Widgets unavailable: edit the assumptions and rerun the cells.")
        return None
    controls = {}
    for label, value in source.items():
        if label in options:
            control = widgets.Dropdown(
                options=options[label],
                value=value,
                description=label,
                style={"description_width": "initial"},
            )
        else:
            widget_type = (
                widgets.IntText
                if isinstance(value, int) and not isinstance(value, bool)
                else widgets.FloatText
            )
            control = widget_type(
                value=value, description=label, style={"description_width": "initial"}
            )
        controls[label] = control
    output = widgets.Output()
    panel = widgets.VBox([*controls.values(), output])

    def update(change: object = None) -> None:
        import base64
        from io import BytesIO

        try:
            series = calculate(
                {label: control.value for label, control in controls.items()}
            )
            fig = plot_finance_series(
                series,
                title=title,
                xlabel=xlabel,
                ylabel=ylabel,
                marker_month=marker_month,
                stacked=stacked,
                x_values=axis_values,
                bar=bar,
                x_tick_labels=axis_labels,
            )
            with BytesIO() as buffer:
                fig.savefig(buffer, format="png", dpi=110)
                png = base64.b64encode(buffer.getvalue()).decode("ascii")
            plt.close(fig)
        except (TypeError, ValueError) as error:
            output.outputs = (
                {
                    "output_type": "display_data",
                    "data": {
                        "text/markdown": f"Check the inputs: {error}. Correct them to restore the chart."
                    },
                    "metadata": {},
                },
            )
            return
        ending = (
            f"| Series | Final plotted value ({ylabel}) |\n|---|---:|\n"
            + "\n".join(
                f"| {name} | {values[-1]:,.2f} |" for name, values in series.items()
            )
        )
        output.outputs = (
            {
                "output_type": "display_data",
                "data": {"text/markdown": ending},
                "metadata": {},
            },
            {"output_type": "display_data", "data": {"image/png": png}, "metadata": {}},
        )

    for control in controls.values():
        control.observe(update, names="value")
    update()
    display(panel)
    return panel


def plot_observation_window(
    observations: "Sequence[MonthlyPrice]",
    *,
    start_month: int,
    end_month: int,
) -> "Figure":
    """Plot dated prices with missing gaps and highlighted inclusive price window.

    Serial month indices use year*12+month-1. Only returns with both endpoints
    inside the selected window enter the displayed sample count/SD. This helper
    calls risk_statistics, never imputes missing prices, and makes no forecast.
    """
    import matplotlib.pyplot as plt

    from .cashflows import _integer
    from .risk_statistics import monthly_log_returns, sample_volatility

    snapshot = tuple(observations)
    returns = monthly_log_returns(snapshot)
    start = _integer("start_month", start_month)
    end = _integer("end_month", end_month)
    if (
        not snapshot
        or not snapshot[0].month_index <= start <= end <= snapshot[-1].month_index
    ):
        raise ValueError("window must be ordered and within observation dates")
    selected = [
        r.log_change for r in returns if start <= r.start_month and r.end_month <= end
    ]
    result = sample_volatility(selected)
    values = {row.month_index: row.price_usd_per_gpu_hour for row in snapshot}
    months = list(range(snapshot[0].month_index, snapshot[-1].month_index + 1))
    prices = [
        float("nan") if (price := values.get(month)) is None else price
        for month in months
    ]
    figure, ax = plt.subplots(figsize=(8, 4))
    ax.plot(months, prices, marker="o", label="Synthetic observations")
    ax.axvspan(start, end, alpha=0.15, label="Selected price window")
    labels = [f"{m // 12:04d}-{m % 12 + 1:02d}" for m in months]
    ax.set_xticks(months, labels, rotation=30)
    sd = (
        "N/A (insufficient history)"
        if result.sample_sd is None
        else f"{result.sample_sd:.6f}"
    )
    ax.set_title(
        f"Monthly log-change SD {sd}; n={result.count}, omitted={result.omitted_count}"
    )
    ax.set_xlabel("Calendar month; shaded prices define the return window")
    ax.set_ylabel("USD/GPU-hour")
    ax.legend()
    figure.tight_layout()
    plt.close(figure)
    return figure


def explore_observation_window(
    observations: "Sequence[MonthlyPrice]",
    *,
    start_month: int,
    end_month: int,
) -> "VBox | None":
    """Independent start/end controls, exact calendar labels, and static fallback."""
    import base64
    from io import BytesIO

    from IPython.display import display

    snapshot = tuple(observations)
    initial = plot_observation_window(
        snapshot, start_month=start_month, end_month=end_month
    )
    try:
        import ipywidgets as widgets
    except ImportError:
        display(initial)
        return None
    options = [
        (f"{month // 12:04d}-{month % 12 + 1:02d}", month)
        for month in range(snapshot[0].month_index, snapshot[-1].month_index + 1)
    ]
    start = widgets.Dropdown(
        options=options, value=start_month, description="Start month"
    )
    end = widgets.Dropdown(options=options, value=end_month, description="End month")
    output = widgets.Output()
    panel = widgets.VBox([start, end, output])

    def update(change: object = None) -> None:
        try:
            figure = plot_observation_window(
                snapshot, start_month=start.value, end_month=end.value
            )
            with BytesIO() as buffer:
                figure.savefig(buffer, format="png", dpi=110)
                png = base64.b64encode(buffer.getvalue()).decode("ascii")
            output.outputs = (
                {
                    "output_type": "display_data",
                    "data": {"image/png": png},
                    "metadata": {},
                },
            )
        except (TypeError, ValueError) as error:
            output.outputs = (
                {
                    "output_type": "display_data",
                    "data": {
                        "text/markdown": f"Check the window: {error}. Correct the dates to restore the chart."
                    },
                    "metadata": {},
                },
            )

    start.observe(update, names="value")
    end.observe(update, names="value")
    update()
    display(panel)
    return panel


def plot_workload_comparison(results: "Mapping[str, UsefulOutputCosts]") -> "Figure":
    """Separate spend and unit-cost axes; zero-task unit cost labeled N/A."""
    import matplotlib.pyplot as plt

    from .financing import _nonnegative
    from .workload_costs import UsefulOutputCosts

    if not results:
        raise ValueError("at least one workload result required")
    if any(not isinstance(row, UsefulOutputCosts) for row in results.values()):
        raise TypeError("results must contain UsefulOutputCosts records")
    names = list(results)
    costs = [_nonnegative("total cost", row.total_cost_usd) for row in results.values()]
    units = [
        None
        if row.usd_per_task is None
        else _nonnegative("unit cost", row.usd_per_task)
        for row in results.values()
    ]
    figure, axes = plt.subplots(1, 2, figsize=(9, 4))
    axes[0].bar(names, costs)
    axes[0].set_ylabel("Total spend (USD)")
    axes[0].set_title("Budget")
    axes[1].bar(names, [float("nan") if value is None else value for value in units])
    axes[1].set_ylabel("USD per useful task")
    axes[1].set_title("Unit cost at fixed quality")
    for index, value in enumerate(units):
        if value is None:
            axes[1].text(index, 0, "N/A: zero tasks", ha="center", va="bottom")
    figure.tight_layout()
    plt.close(figure)
    return figure


def explore_workload_mix(
    *,
    task_count: float,
    heavy_fraction: float,
    light_gpu_hours_per_task: float,
    heavy_gpu_hours_per_task: float,
    usd_per_gpu_hour: float,
) -> "VBox | None":
    """Independent demand/mix controls with frozen initial baseline and two units."""
    import base64
    from io import BytesIO

    from IPython.display import display

    from .financing import _fraction, _nonnegative
    from .workload_costs import UsefulOutputCosts, useful_output_costs

    def calculate(count: float, fraction: float) -> UsefulOutputCosts:
        count = _nonnegative("task_count", count)
        fraction = _fraction("heavy_fraction", fraction, inclusive=True)
        return useful_output_costs(
            task_counts={"light": count * (1 - fraction), "heavy": count * fraction},
            gpu_hours_per_task={
                "light": light_gpu_hours_per_task,
                "heavy": heavy_gpu_hours_per_task,
            },
            usd_per_gpu_hour=usd_per_gpu_hour,
        )

    baseline = calculate(task_count, heavy_fraction)
    initial = plot_workload_comparison({"Baseline": baseline, "Selected": baseline})
    try:
        import ipywidgets as widgets
    except ImportError:
        display(initial)
        return None
    count = widgets.FloatText(
        value=task_count,
        description="Useful tasks",
        style={"description_width": "initial"},
    )
    fraction = widgets.FloatText(
        value=heavy_fraction,
        description="Heavy fraction",
        style={"description_width": "initial"},
    )
    output = widgets.Output()
    panel = widgets.VBox([count, fraction, output])

    def update(change: object = None) -> None:
        try:
            chosen = calculate(count.value, fraction.value)
            figure = plot_workload_comparison(
                {"Baseline": baseline, "Selected": chosen}
            )
            with BytesIO() as buffer:
                figure.savefig(buffer, format="png", dpi=110)
                png = base64.b64encode(buffer.getvalue()).decode("ascii")
            unit = (
                "N/A (zero tasks)"
                if chosen.usd_per_task is None
                else f"{chosen.usd_per_task:.6f}"
            )
            output.outputs = (
                {
                    "output_type": "display_data",
                    "data": {
                        "text/markdown": f"Selected: {chosen.useful_tasks:,.2f} useful tasks; {chosen.consumed_gpu_hours:,.2f} GPU-hours; "
                        f"USD {chosen.total_cost_usd:,.2f}; USD/task {unit}."
                    },
                    "metadata": {},
                },
                {
                    "output_type": "display_data",
                    "data": {"image/png": png},
                    "metadata": {},
                },
            )
        except (TypeError, ValueError) as error:
            output.outputs = (
                {
                    "output_type": "display_data",
                    "data": {
                        "text/markdown": f"Check the inputs: {error}. Correct them to restore the comparison."
                    },
                    "metadata": {},
                },
            )

    count.observe(update, names="value")
    fraction.observe(update, names="value")
    update()
    display(panel)
    return panel


def plot_tenor_capacity(rows: "Sequence[ResellerCommitmentRow]") -> "Figure":
    """Display monthly purchased, sold and unplaced hours from a built schedule."""
    import matplotlib.pyplot as plt

    months = [r.month_offset for r in rows if r.month_offset]
    periods = [r for r in rows if r.month_offset]
    if not periods:
        raise ValueError("a nonempty service schedule is required")
    fig, ax = plt.subplots(figsize=(9, 3.2))
    contracted = [r.sold_gpu_hours if r.customer_contracted else 0 for r in periods]
    assumed = [r.sold_gpu_hours if not r.customer_contracted else 0 for r in periods]
    ax.bar(months, contracted, label="Contracted sold hours", color="#28608a")
    ax.bar(
        months,
        assumed,
        bottom=contracted,
        label="Scenario-assumed sold hours",
        color="#64a6a2",
    )
    ax.bar(
        months,
        [r.unplaced_gpu_hours for r in periods],
        bottom=[r.sold_gpu_hours for r in periods],
        label="Unplaced hours",
        color="#d8dee6",
    )
    ax.plot(
        months,
        [r.purchased_gpu_hours for r in periods],
        color="#202a38",
        label="Purchased capacity",
        linewidth=1.5,
    )
    ax.set(
        xlabel="Service month",
        ylabel="GPU-hours per month",
        title="Capacity committed versus sold",
    )
    ax.set_ylim(0, max(r.purchased_gpu_hours for r in periods) * 1.12 or 1)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.23), ncol=2)
    fig.tight_layout()
    return fig


def plot_tenor_heatmap(
    *,
    upstream_commitment_usd: float,
    contracted_revenue_usd: float,
    tail_available_gpu_hours: float,
    future_resale_usd_per_gpu_hour: float,
    placement_fraction: float,
    selling_fee_fraction: float,
    period_label: str = "36-month",
) -> "Figure":
    """Plot whole-deal contribution; financial arithmetic delegates to tenor_trade.

    The marker uses the selected price/placement; the fee changes every grid
    value and the zero-contribution boundary. The first period and fleet stay
    fixed. Undefined/out-of-capacity break-even values are not drawn as a line.
    """
    import matplotlib.pyplot as plt

    from .tenor_trade import tenor_tail_outcome

    fixed = dict(
        upstream_commitment_usd=upstream_commitment_usd,
        contracted_revenue_usd=contracted_revenue_usd,
        tail_available_gpu_hours=tail_available_gpu_hours,
        selling_fee_fraction=selling_fee_fraction,
    )
    chosen = tenor_tail_outcome(
        **fixed,
        future_resale_usd_per_gpu_hour=future_resale_usd_per_gpu_hour,
        placement_fraction=placement_fraction,
    )
    maximum_price = max(12.0, future_resale_usd_per_gpu_hour)
    prices = [maximum_price * i / 48 for i in range(49)]
    placements = [i / 40 for i in range(41)]
    values = [
        [
            tenor_tail_outcome(
                **fixed, future_resale_usd_per_gpu_hour=p, placement_fraction=f
            ).contribution_usd
            for p in prices
        ]
        for f in placements
    ]
    bound = max(1.0, max(abs(v) for row in values for v in row))
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    mesh = ax.pcolormesh(
        prices,
        placements,
        values,
        shading="nearest",
        cmap="RdBu",
        vmin=-bound,
        vmax=bound,
    )
    fig.colorbar(
        mesh, ax=ax, label=f"{period_label} contribution (USD; before overhead)"
    )
    boundary = []
    for price in prices:
        result = tenor_tail_outcome(
            **fixed,
            future_resale_usd_per_gpu_hour=price,
            placement_fraction=placement_fraction,
        )
        f = result.break_even_placement_fraction
        if not result.costs_already_recovered and f is not None and 0 <= f <= 1:
            boundary.append((price, f))
    if boundary:
        ax.plot(
            [p for p, _ in boundary],
            [f for _, f in boundary],
            color="black",
            label=f"Zero {period_label.lower()} contribution",
            linewidth=1.5,
        )
    elif chosen.costs_already_recovered:
        ax.text(
            0.02,
            0.98,
            "Contracted net revenue already covers all costs",
            transform=ax.transAxes,
            va="top",
            bbox=dict(facecolor="white", alpha=0.9),
        )
    else:
        ax.text(
            0.02,
            0.98,
            "No break-even boundary in the displayed range",
            transform=ax.transAxes,
            va="top",
            bbox=dict(facecolor="white", alpha=0.9),
        )
    ax.scatter(
        [future_resale_usd_per_gpu_hour],
        [placement_fraction],
        color="white",
        edgecolors="black",
        label="Selected scenario",
        zorder=4,
        clip_on=False,
    )
    ax.set(
        xlabel="Future resale price (USD/GPU-hour)",
        ylabel="Future placement fraction",
        xlim=(0, maximum_price),
        ylim=(0, 1),
        title=f"{period_label} contribution: USD {chosen.contribution_usd:,.0f} | selling fee {selling_fee_fraction:.1%}",
    )
    ax.legend(loc="lower right")
    fig.tight_layout()
    plt.close(fig)
    return fig


def explore_tenor_trade(
    *,
    upstream_commitment_usd: float,
    contracted_revenue_usd: float,
    tail_available_gpu_hours: float,
    future_resale_usd_per_gpu_hour: float,
    placement_fraction: float,
    selling_fee_fraction: float,
    period_label: str = "36-month",
) -> "VBox | None":
    """Three independent exact-value controls with a static heatmap fallback.

    No notebook globals are captured. Invalid edits replace stale results and
    valid edits restore them. The fee applies to first-year and tail revenue.
    """
    import matplotlib.pyplot as plt
    from IPython.display import display

    from .tenor_trade import tenor_tail_outcome

    source = dict(
        upstream_commitment_usd=upstream_commitment_usd,
        contracted_revenue_usd=contracted_revenue_usd,
        tail_available_gpu_hours=tail_available_gpu_hours,
        future_resale_usd_per_gpu_hour=future_resale_usd_per_gpu_hour,
        placement_fraction=placement_fraction,
        selling_fee_fraction=selling_fee_fraction,
    )
    tenor_tail_outcome(**source)
    try:
        import ipywidgets as widgets
    except ImportError:
        fig = plot_tenor_heatmap(**source, period_label=period_label)
        display(fig)
        plt.close(fig)
        print(
            "Widgets unavailable: edit the price, placement and fee inputs and rerun the cells."
        )
        return None
    labels = {
        "future_resale_usd_per_gpu_hour": "Future USD/GPU-hour",
        "placement_fraction": "Placement fraction",
        "selling_fee_fraction": "Selling fee fraction",
    }
    controls = {
        key: widgets.FloatText(
            value=source[key], description=label, style={"description_width": "initial"}
        )
        for key, label in labels.items()
    }
    output = widgets.Output()
    panel = widgets.VBox([*controls.values(), output])

    def update(change: object = None) -> None:
        import base64
        from io import BytesIO

        current = source | {key: c.value for key, c in controls.items()}
        try:
            result = tenor_tail_outcome(**current)
            fig = plot_tenor_heatmap(**current, period_label=period_label)
            try:
                with BytesIO() as buffer:
                    fig.savefig(buffer, format="png", dpi=110)
                    png = base64.b64encode(buffer.getvalue()).decode("ascii")
            finally:
                plt.close(fig)
            price = result.break_even_resale_usd_per_gpu_hour
            placement = result.break_even_placement_fraction
            price_text = (
                "No finite solution" if price is None else f"USD {price:,.4f}/GPU-hour"
            )
            placement_text = (
                "No finite solution" if placement is None else f"{placement:.2%}"
            )
            if placement is not None and not result.placement_attainable:
                placement_text += " — exceeds available capacity"
            note = (
                "Contracted net revenue already covers modeled costs; no future sales required."
                if result.costs_already_recovered
                else "Hurdles include selling fees on modeled revenue."
            )
            readout = (
                f"Contribution: **USD {result.contribution_usd:,.2f}**. "
                f"Break-even price at selected placement: {price_text}. "
                f"Break-even placement at selected price: {placement_text}. {note}"
            )
            output.outputs = (
                {
                    "output_type": "display_data",
                    "data": {"text/markdown": readout},
                    "metadata": {},
                },
                {
                    "output_type": "display_data",
                    "data": {"image/png": png},
                    "metadata": {},
                },
            )
        except (TypeError, ValueError) as error:
            output.outputs = (
                {
                    "output_type": "display_data",
                    "data": {
                        "text/markdown": f"Check the inputs: {error}. Correct them to restore the heatmap."
                    },
                    "metadata": {},
                },
            )

    for c in controls.values():
        c.observe(update, names="value")
    update()
    display(panel)
    return panel


def basis_budget_series(
    *,
    settlement_index_usd_per_gpu_hour: float,
    realized_basis_usd_per_gpu_hour: float,
    budget_basis_usd_per_gpu_hour: float,
    gpu_hours: float,
    strike_usd_per_gpu_hour: float,
) -> dict[str, tuple[float]]:
    """One selected settlement's costs; reject S=I+b below zero, never clamp it."""
    from .economics import _finite_number
    from .hedging import basis_budget_summary

    index = _finite_number("settlement index", settlement_index_usd_per_gpu_hour)
    basis = _finite_number("realized basis", realized_basis_usd_per_gpu_hour)
    result = basis_budget_summary(
        actual_usd_per_gpu_hour=index + basis,
        benchmark_usd_per_gpu_hour=index,
        strike_usd_per_gpu_hour=strike_usd_per_gpu_hour,
        gpu_hours=gpu_hours,
        budget_basis_usd_per_gpu_hour=budget_basis_usd_per_gpu_hour,
    )
    return {
        "Unhedged cost": (result.unhedged_cost_usd,),
        "Hedged cost": (result.net_cost_usd,),
        "Budget deviation": (result.budget_deviation_usd,),
    }


def explore_basis_budget(
    *,
    settlement_index_usd_per_gpu_hour: float,
    realized_basis_usd_per_gpu_hour: float,
    budget_basis_usd_per_gpu_hour: float,
    gpu_hours: float,
    strike_usd_per_gpu_hour: float,
) -> "VBox | None":
    """Independent exact-value I/b/b0 controls; fixed quantity and strike.

    Invalid prices replace stale results; valid edits recover. Without widgets,
    display the same static chart. No notebook globals or hidden scenario state.
    """
    from .economics import _finite_number

    def number(value: float | str) -> float:
        if isinstance(value, str):
            raise TypeError("basis controls require numeric values")
        return _finite_number("control", value)

    def calculate(values: Mapping[str, float | str]) -> Mapping[str, Sequence[float]]:
        return basis_budget_series(
            settlement_index_usd_per_gpu_hour=number(values["Index (USD/GPU-hour)"]),
            realized_basis_usd_per_gpu_hour=number(values["Basis (USD/GPU-hour)"]),
            budget_basis_usd_per_gpu_hour=number(values["Budget basis (USD/GPU-hour)"]),
            gpu_hours=gpu_hours,
            strike_usd_per_gpu_hour=strike_usd_per_gpu_hour,
        )

    return explore_finance_series(
        {
            "Index (USD/GPU-hour)": settlement_index_usd_per_gpu_hour,
            "Basis (USD/GPU-hour)": realized_basis_usd_per_gpu_hour,
            "Budget basis (USD/GPU-hour)": budget_basis_usd_per_gpu_hour,
        },
        calculate,
        title=f"Same {gpu_hours:,.0f} GPU-hours purchased and hedged; K = USD {strike_usd_per_gpu_hour:g}/GPU-hour",
        xlabel="Aligned physical and hedge settlement",
        bar=True,
        x_tick_labels=["Selected scenario"],
    )


def plot_tenor_price_snapshot(
    quotes: Sequence[RentalQuote],
    *,
    on_demand_usd_per_gpu_hour: float,
    source_label: str,
) -> "Figure":
    """Plot supplied published term rates and differences from the longest tenor.

    No interpolation, forward inference, API retrieval or normalization of
    commercial terms. On demand is a separate categorical observation, not a
    zero-month forward. The notebook supplies source/date and comparability limits.
    """
    import matplotlib.pyplot as plt

    from .cashflows import _integer
    from .economics import _positive_number

    demand = _positive_number("on_demand_usd_per_gpu_hour", on_demand_usd_per_gpu_hour)
    if not isinstance(source_label, str):
        raise TypeError("source_label must be a string")
    if not source_label.strip() or not quotes:
        raise ValueError("source label and quotes must be nonempty")
    previous = 0
    labels = ["On\ndemand"]
    prices = [demand]
    for q in quotes:
        if not isinstance(q, RentalQuote):
            raise TypeError("quotes must contain RentalQuote records")
        month = _integer("term_months", q.term_months, minimum=1)
        if month <= previous:
            raise ValueError("tenors must be strictly increasing")
        prices.append(_positive_number("rental rate", q.rental_usd_per_gpu_hour))
        labels.append(f"{month}M")
        previous = month
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    x = list(range(len(prices)))
    axes[0].plot(x, prices, marker="o", color="#176b87")
    axes[0].set_ylim(0, max(prices) * 1.18)
    gaps = [p - prices[-1] for p in prices]
    axes[1].bar(x, gaps, color="#248e89")
    axes[1].axhline(0, color="gray", linewidth=0.8)
    axes[1].set_ylim(min(0.0, min(gaps) * 1.2), max(0.1, max(gaps) * 1.2))
    for ax, values in zip(axes, (prices, gaps)):
        for i, value in enumerate(values):
            ax.annotate(
                f"{value:.2f}",
                (i, value),
                xytext=(0, 7),
                textcoords="offset points",
                ha="center",
            )
        ax.set_xticks(x, labels)
        ax.set_xlabel("Commitment length (categories; not future dates)")
        ax.grid(axis="y", alpha=0.2)
    axes[0].set(title="Published rental price by tenor", ylabel="USD/GPU-hour")
    axes[1].set(
        title=f"Price difference versus {previous}M", ylabel="USD/GPU-hour difference"
    )
    fig.suptitle(source_label, fontsize=11)
    fig.tight_layout()
    plt.close(fig)
    return fig


def plot_lab_case(inputs: "LabInputs", *, view: str) -> "Figure":
    """Case-study views; dollar axes in millions, capacity in million GPU-hours."""
    from dataclasses import replace

    import matplotlib.pyplot as plt

    from .lab_financing import liquidation_stress, model_lab

    result = model_lab(inputs)
    rows = result.months
    months = [r.month for r in rows]
    fig, ax = plt.subplots(figsize=(9, 4.5), layout="constrained")
    if view == "structure":
        ax.set(xlim=(0, 1), ylim=(0, 1))
        ax.axis("off")
        principal = inputs.equipment_usd * inputs.advance_fraction / 1e6
        equity = inputs.equipment_usd / 1e6 - principal
        boxes = [
            (0.16, 0.82, f"Lab equity\nUSD {equity:,.1f}m + extras"),
            (0.82, 0.82, f"Lender\nUSD {principal:,.1f}m draw"),
            (0.49, 0.48, "GPU-owning project\nLab training + external sales"),
            (0.14, 0.13, f"Equipment seller\nUSD {inputs.equipment_usd / 1e6:,.1f}m"),
            (0.83, 0.13, "External customers\nContracted + spot cash"),
        ]
        for x, y, label in boxes:
            ax.text(
                x,
                y,
                label,
                ha="center",
                va="center",
                bbox={"boxstyle": "round,pad=0.6", "fc": "#e8f3f5", "ec": "#286675"},
            )
        for start, end in [
            ((0.20, 0.72), (0.41, 0.57)),
            ((0.77, 0.72), (0.57, 0.57)),
            ((0.42, 0.39), (0.22, 0.23)),
            ((0.76, 0.23), (0.57, 0.39)),
        ]:
            ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->"})
        ax.set_title(
            f"Time-zero extras: fee {result.fee_usd / 1e6:,.1f}m + locked reserve {result.reserve_usd / 1e6:,.1f}m USD\nOperating buffer is separate; debt service paid by project monthly"
        )
    elif view == "capacity":
        ax.stackplot(
            months,
            *[
                [getattr(r, field) / 1e6 for r in rows]
                for field in (
                    "training_gpu_hours",
                    "contracted_gpu_hours",
                    "spot_gpu_hours",
                    "unsold_gpu_hours",
                )
            ],
            labels=["Internal training", "Committed", "Spot sold", "Unsold"],
            alpha=0.85,
        )
        ax.set(
            ylabel="Million usable GPU-hours / month", title="Who uses the equipment?"
        )
        ax.legend(loc="upper left", ncol=2)
    elif view == "cash":
        cash = [r.cfads_usd / 1e6 for r in rows]
        service = [r.debt_service_usd / 1e6 for r in rows]
        ax.plot(months, cash, label="Cash available for debt service")
        ax.plot(months, service, label="Interest + principal")
        ax.fill_between(
            months,
            cash,
            service,
            where=[c < d for c, d in zip(cash, service)],
            color="#cf5b48",
            alpha=0.3,
            label="Period shortfall",
        )
        ax.axhline(0, color="gray", linewidth=0.7)
        ax.set(
            ylabel="USD millions / month",
            title="Training consumes cash; external sales provide it",
        )
        ax.legend()
    elif view == "coverage":
        rates = [0.10, 0.13, 0.16, 0.17, 0.19, 0.22, 0.25]
        shares = [i * (1 - inputs.training_fraction) / 12 for i in range(13)]
        grid = [
            [
                model_lab(
                    replace(inputs, nominal_annual_rate=rate, contracted_fraction=share)
                ).minimum_dscr
                for share in shares
            ]
            for rate in rates
        ]
        values = [[float("nan") if v is None else v for v in row] for row in grid]
        mesh = ax.imshow(
            values, origin="lower", aspect="auto", cmap="RdYlGn", vmin=0, vmax=2
        )
        ax.set_xticks(range(len(shares)), [f"{s:.0%}" for s in shares])
        ax.set_yticks(range(len(rates)), [f"{r:.0%}" for r in rates])
        for y, row in enumerate(values):
            for x, value in enumerate(row):
                ax.text(x, y, f"{value:.1f}", ha="center", va="center", fontsize=8)
        fig.colorbar(mesh, ax=ax, label="Minimum monthly DSCR (×; color capped at 2)")
        ax.set(
            xlabel="Committed share of usable capacity",
            ylabel="Nominal annual loan rate",
            title=f"Coverage at fixed {inputs.training_fraction:.0%} training; target {inputs.minimum_dscr:.2f}×",
        )
    elif view == "collateral":
        dates = list(range(inputs.term_months + 1))
        net = [liquidation_stress(inputs, default_month=t) for t in dates]
        ax.plot(
            dates,
            [r.closing_debt_usd / 1e6 for r in result.loan],
            label="Scheduled closing debt",
        )
        ax.plot(
            dates,
            [v[1] / 1e6 for v in net],
            label="Claim after recovery delay",
            linestyle=":",
        )
        ax.plot(
            dates,
            [
                inputs.equipment_usd
                * inputs.annual_value_retention_fraction ** (t / 12)
                / 1e6
                for t in dates
            ],
            label="Assumed gross resale value",
        )
        ax.plot(dates, [v[0] / 1e6 for v in net], label="Stressed net sale after delay")
        ax.set(
            ylabel="USD millions",
            title="Independent hypothetical defaults at each month; not one cash path",
        )
        ax.legend()
    else:
        plt.close(fig)
        raise ValueError("unknown lab case view")
    if view not in ("structure", "coverage"):
        ax.set_xlabel("Month after purchase")
        ax.grid(alpha=0.2)
    plt.close(fig)
    return fig


def plot_lab_scenarios(scenarios: "Mapping[str, LabInputs]") -> "Figure":
    """Compare required incremental cash; include fees and locked reserve once."""
    import matplotlib.pyplot as plt

    from .lab_financing import model_lab

    fig, ax = plt.subplots(figsize=(9, 4), layout="constrained")
    results = [model_lab(p) for p in scenarios.values()]
    ax.bar(
        list(scenarios), [r.additional_cash_usd / 1e6 for r in results], color="#296b83"
    )
    ax.set(
        ylabel="USD millions beyond equipment equity",
        title="Fees + locked reserve + retained-cash funding deficit",
    )
    ax.tick_params(axis="x", labelsize=9)
    plt.close(fig)
    return fig


def lab_training_explorer(inputs: "LabInputs") -> "VBox":
    """Independent exact-value training control; invalid capacity edits recover."""
    from dataclasses import replace

    import ipywidgets as widgets
    from IPython.display import clear_output, display

    from .lab_financing import minimum_contract_fraction, model_lab

    model_lab(inputs)
    control = widgets.BoundedFloatText(
        value=inputs.training_fraction,
        min=0,
        max=1,
        step=0.01,
        description="Training share:",
        style={"description_width": "initial"},
    )
    output = widgets.Output()

    def update(change: object = None) -> None:
        with output:
            clear_output(wait=True)
            try:
                scenario = replace(inputs, training_fraction=control.value)
                result = model_lab(scenario)
                threshold = minimum_contract_fraction(scenario)
                coverage = (
                    "N/A"
                    if result.minimum_dscr is None
                    else f"{result.minimum_dscr:.2f}×"
                )
                print(
                    f"Minimum DSCR: {coverage}; additional cash: USD {result.additional_cash_usd:,.0f}"
                )
                print(
                    "Required contracted share: "
                    + (
                        "infeasible at this training allocation"
                        if threshold is None
                        else f"{threshold:.2%}"
                    )
                )
                display(plot_lab_case(scenario, view="cash"))
            except (ValueError, TypeError) as exc:
                print(f"Adjust the training share: {exc}")

    control.observe(update, names="value")
    update()
    return widgets.VBox([control, output])
