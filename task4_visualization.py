import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os


# -------------------------------------------------------
# Task 4 — Take the analysed CSV from Task 3 and turn
# the numbers into actual charts. Three individual PNGs
# plus a combined dashboard at the end.
# -------------------------------------------------------

CSV_PATH    = "data/trends_analysed.csv"
OUTPUT_DIR  = "outputs"

# I picked these colours manually so they look good together
# instead of just using matplotlib's default blue for everything
CATEGORY_COLOURS = {
    "technology":    "#4C9BE8",
    "worldnews":     "#E8724C",
    "sports":        "#4CE87A",
    "science":       "#C44CE8",
    "entertainment": "#E8C44C",
}

# colours for the scatter plot popular vs non-popular split
POPULAR_COLOUR     = "#E8724C"
NOTPOPULAR_COLOUR  = "#4C9BE8"


def setup():
    """Load the CSV and make the outputs folder."""
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(
            f"Can't find {CSV_PATH}. Make sure Task 3 ran successfully."
        )

    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df)} rows from {CSV_PATH}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output folder ready: {OUTPUT_DIR}/")

    return df


def shorten_title(title, max_len=50):
    """
    Truncates a title to max_len characters and adds '...' if it was cut.
    Needed so long HN titles don't overflow the y-axis on chart 1.
    """
    if len(title) > max_len:
        return title[:max_len].rstrip() + "..."
    return title


# -------------------------------------------------------
# Chart 1 — Top 10 stories by score (horizontal bar)
# -------------------------------------------------------
def chart1_top_stories(df):
    """Horizontal bar chart of the 10 highest-scoring stories."""

    # sort descending and take the top 10
    top10 = df.nlargest(10, "score").copy()

    # shorten titles so they fit nicely on the y-axis
    top10["short_title"] = top10["title"].apply(shorten_title)

    # reversing so the highest bar appears at the top of the chart
    top10 = top10.iloc[::-1]

    fig, ax = plt.subplots(figsize=(12, 6))

    # using a colour gradient from light to deep blue
    colours = plt.cm.Blues(np.linspace(0.4, 0.9, len(top10)))

    bars = ax.barh(top10["short_title"], top10["score"], color=colours, edgecolor="white", linewidth=0.6)

    # add the actual score number at the end of each bar
    for bar, score in zip(bars, top10["score"]):
        ax.text(
            bar.get_width() + 10,
            bar.get_y() + bar.get_height() / 2,
            str(score),
            va="center", ha="left",
            fontsize=9, color="#333333"
        )

    ax.set_title("Top 10 Stories by Score", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Score (upvotes)", fontsize=11)
    ax.set_ylabel("Story Title", fontsize=11)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(0, top10["score"].max() * 1.12)   # a bit of extra room for the labels

    plt.tight_layout()

    # always savefig before show (or instead of show when running headless)
    path = os.path.join(OUTPUT_DIR, "chart1_top_stories.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Saved: {path}")


# -------------------------------------------------------
# Chart 2 — Stories per category (vertical bar)
# -------------------------------------------------------
def chart2_categories(df):
    """Bar chart showing story count per category."""

    counts = df["category"].value_counts().sort_index()

    # pull colours in the same order as the sorted categories
    bar_colours = [CATEGORY_COLOURS.get(cat, "#999999") for cat in counts.index]

    fig, ax = plt.subplots(figsize=(8, 5))

    bars = ax.bar(counts.index, counts.values, color=bar_colours, edgecolor="white", linewidth=0.8, width=0.6)

    # stick the count on top of each bar
    for bar, val in zip(bars, counts.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.3,
            str(val),
            ha="center", va="bottom",
            fontsize=10, fontweight="bold", color="#333333"
        )

    ax.set_title("Stories per Category", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Category", fontsize=11)
    ax.set_ylabel("Number of Stories", fontsize=11)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylim(0, counts.max() + 4)

    plt.tight_layout()

    path = os.path.join(OUTPUT_DIR, "chart2_categories.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Saved: {path}")


# -------------------------------------------------------
# Chart 3 — Score vs Comments scatter (coloured by popularity)
# -------------------------------------------------------
def chart3_scatter(df):
    """
    Scatter plot: score on x, num_comments on y.
    Popular stories (above average score) get a different colour
    so you can see at a glance which ones drive more discussion.
    """

    popular     = df[df["is_popular"] == True]
    not_popular = df[df["is_popular"] == False]

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.scatter(
        not_popular["score"], not_popular["num_comments"],
        color=NOTPOPULAR_COLOUR, alpha=0.7, edgecolors="white",
        linewidth=0.5, s=70, label="Below average score"
    )
    ax.scatter(
        popular["score"], popular["num_comments"],
        color=POPULAR_COLOUR, alpha=0.85, edgecolors="white",
        linewidth=0.5, s=90, label="Above average score (popular)"
    )

    # draw a vertical dashed line at the average score so it's obvious where the split is
    avg_score = df["score"].mean()
    ax.axvline(avg_score, color="#888888", linestyle="--", linewidth=1, alpha=0.7)
    ax.text(avg_score + 5, ax.get_ylim()[1] * 0.95, f"avg = {avg_score:.0f}",
            color="#888888", fontsize=8)

    ax.set_title("Score vs Number of Comments", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Score (upvotes)", fontsize=11)
    ax.set_ylabel("Number of Comments", fontsize=11)
    ax.legend(fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()

    path = os.path.join(OUTPUT_DIR, "chart3_scatter.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Saved: {path}")


# -------------------------------------------------------
# Bonus — Dashboard: all 3 charts in one figure
# -------------------------------------------------------
def dashboard(df):
    """
    Combines the three charts into one dashboard figure.
    Using a 2x2 grid and leaving the 4th cell empty — looks cleaner
    than squishing everything into 1x3 which makes each chart tiny.
    """

    fig = plt.figure(figsize=(18, 11))
    fig.suptitle("TrendPulse Dashboard", fontsize=20, fontweight="bold", y=1.01)

    # --- panel 1: top 10 horizontal bar (top-left, spans full width of first row) ---
    ax1 = fig.add_subplot(2, 2, (1, 2))   # merging cells 1 and 2 so it gets more room

    top10 = df.nlargest(10, "score").copy()
    top10["short_title"] = top10["title"].apply(shorten_title)
    top10 = top10.iloc[::-1]
    colours = plt.cm.Blues(np.linspace(0.4, 0.9, len(top10)))
    ax1.barh(top10["short_title"], top10["score"], color=colours, edgecolor="white")
    ax1.set_title("Top 10 Stories by Score", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Score")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # --- panel 2: category bar (bottom-left) ---
    ax2 = fig.add_subplot(2, 2, 3)

    counts = df["category"].value_counts().sort_index()
    bar_colours = [CATEGORY_COLOURS.get(cat, "#999999") for cat in counts.index]
    ax2.bar(counts.index, counts.values, color=bar_colours, edgecolor="white", width=0.6)
    ax2.set_title("Stories per Category", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Category")
    ax2.set_ylabel("Count")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    # --- panel 3: scatter (bottom-right) ---
    ax3 = fig.add_subplot(2, 2, 4)

    popular     = df[df["is_popular"] == True]
    not_popular = df[df["is_popular"] == False]
    ax3.scatter(not_popular["score"], not_popular["num_comments"],
                color=NOTPOPULAR_COLOUR, alpha=0.7, s=55, label="Below avg")
    ax3.scatter(popular["score"], popular["num_comments"],
                color=POPULAR_COLOUR, alpha=0.85, s=70, label="Popular")
    ax3.set_title("Score vs Comments", fontsize=12, fontweight="bold")
    ax3.set_xlabel("Score")
    ax3.set_ylabel("Comments")
    ax3.legend(fontsize=8)
    ax3.spines["top"].set_visible(False)
    ax3.spines["right"].set_visible(False)

    plt.tight_layout()

    path = os.path.join(OUTPUT_DIR, "dashboard.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Saved: {path}")


def main():
    print("TrendPulse — Task 4: Visualisations")
    print("=" * 40)

    df = setup()

    print("\nGenerating charts...")
    chart1_top_stories(df)
    chart2_categories(df)
    chart3_scatter(df)

    print("\nGenerating dashboard (bonus)...")
    dashboard(df)

    print("\nAll done! Check the outputs/ folder for your charts.")
    print(f"  outputs/chart1_top_stories.png")
    print(f"  outputs/chart2_categories.png")
    print(f"  outputs/chart3_scatter.png")
    print(f"  outputs/dashboard.png")


if __name__ == "__main__":
    main()
