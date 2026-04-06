import pandas as pd
import numpy as np
import os



# Task 3 — Load the cleaned CSV from Task 2 and dig into
# the numbers using Pandas + NumPy. Then save the enriched
# DataFrame as a new CSV for Task 4 to visualise.


CSV_PATH = "data/trends_clean.csv"


def load_and_explore(filepath):
    """
    Loads the CSV and prints some basic info right away.
    Good habit to always check shape + a few rows before doing anything.
    """
    df = pd.read_csv(filepath)

    print(f"Loaded data: {df.shape}")   # (rows, columns)

    print("\nFirst 5 rows:")
    print(df.head(5).to_string(index=False))

    # computing average score and average comments across everything
    avg_score    = df["score"].mean()
    avg_comments = df["num_comments"].mean()

    print(f"\nAverage score   : {avg_score:.2f}")
    print(f"Average comments: {avg_comments:.2f}")

    return df


def numpy_analysis(df):
    """
    A bunch of descriptive stats using NumPy directly.
    Could do this with df.describe() but the task specifically
    asks for NumPy, so pulling out the raw array and working on that.
    """
    scores = df["score"].to_numpy()        # plain numpy array
    comments = df["num_comments"].to_numpy()

    print("\n--- NumPy Stats ---")

    # basic distribution stats for score
    print(f"Mean score   : {np.mean(scores):.2f}")
    print(f"Median score : {np.median(scores):.2f}")
    print(f"Std deviation: {np.std(scores):.2f}")

    # extremes
    print(f"Max score    : {int(np.max(scores))}")
    print(f"Min score    : {int(np.min(scores))}")

    # which category appears most often in our dataset
    # value_counts() returns sorted by frequency already, so .index[0] is the top one
    top_cat   = df["category"].value_counts().index[0]
    top_count = df["category"].value_counts().iloc[0]
    print(f"\nMost stories in: {top_cat} ({top_count} stories)")

    # finding the story with the most comments
    # np.argmax gives the position of the highest value in the array
    most_commented_idx   = np.argmax(comments)
    most_commented_title = df.iloc[most_commented_idx]["title"]
    most_commented_count = int(comments[most_commented_idx])

    print(f"\nMost commented story: \"{most_commented_title}\"")
    print(f"  — {most_commented_count} comments")


def add_new_columns(df):
    """
    Adds two derived columns:
      engagement  — comments per upvote (roughly, how "discussion-heavy" a story is)
      is_popular  — True if the story scored above the dataset average

    Using +1 in the denominator for engagement so we never divide by zero,
    which would blow up for stories with score=0 (unlikely after cleaning but still).
    """
    avg_score = df["score"].mean()

    # engagement: high value = lots of comments relative to its score
    df["engagement"] = df["num_comments"] / (df["score"] + 1)

    # rounding to 4 decimal places just to keep the CSV readable
    df["engagement"] = df["engagement"].round(4)

    # is_popular: simple boolean flag compared to the mean
    df["is_popular"] = df["score"] > avg_score

    print(f"\nNew columns added:")
    print(f"  engagement  — num_comments / (score + 1)")
    print(f"  is_popular  — True if score > {avg_score:.2f} (dataset average)")

    # quick peek at the new columns to make sure they look right
    print("\nSample of new columns (first 5 rows):")
    print(df[["title", "score", "num_comments", "engagement", "is_popular"]].head(5).to_string(index=False))

    return df


def save_result(df):
    """Saves the updated DataFrame to data/trends_analysed.csv."""
    os.makedirs("data", exist_ok=True)      # just in case
    output_path = "data/trends_analysed.csv"

    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\nSaved to {output_path}")
    return output_path


def main():
    print("TrendPulse — Task 3: Analysis with Pandas & NumPy")
    print("=" * 50)

    # make sure the input file actually exists before going further
    if not os.path.exists(CSV_PATH):
        print(f"Error: {CSV_PATH} not found. Did Task 2 run successfully?")
        return

    #  Step 1: load and explore 
    df = load_and_explore(CSV_PATH)

    #  Step 2: NumPy stats 
    numpy_analysis(df)

    #  Step 3: add new columns 
    df = add_new_columns(df)

    #  Step 4: save 
    save_result(df)

    print("\nDone. Task 4 can now load data/trends_analysed.csv for visualisation.")


if __name__ == "__main__":
    main()
