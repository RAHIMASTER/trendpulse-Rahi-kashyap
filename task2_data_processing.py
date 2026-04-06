import pandas as pd
import glob
import os



# Task 2 — Load the JSON from Task 1, clean it up,
# and save a tidy CSV ready for analysis in Task 3.



def find_json_file():
    """
    Looks for any trends_*.json file in the data/ folder.
    I'm using glob here instead of hardcoding the date so this
    works no matter when Task 1 was run.
    Returns the path of the most recent file if there are multiple.
    """
    matches = glob.glob("data/trends_*.json")

    if not matches:
        raise FileNotFoundError(
            "No trends JSON file found in data/. Run task1_data_collection.py first."
        )

    # if somehow there are multiple files, grab the latest one by name
    # (the date is baked into the filename so sorting works fine)
    matches.sort()
    return matches[-1]


def load_data(filepath):
    """Loads the JSON file into a DataFrame and prints the row count."""
    df = pd.read_json(filepath, encoding="utf-8")
    print(f"Loaded {len(df)} stories from {filepath}")
    return df


def clean_data(df):
    """
    Runs through all the cleaning steps one by one.
    I'm printing after each step so it's easy to see where rows are going.
    """

    # --- step 1: remove duplicates based on post_id ---
    # HN sometimes surfaces the same story in multiple requests,
    # so this is a real possibility
    before = len(df)
    df = df.drop_duplicates(subset="post_id")
    print(f"\nAfter removing duplicates: {len(df)}")

    # --- step 2: drop rows with missing critical fields ---
    # A story without an ID, title or score is basically useless for analysis
    before = len(df)
    df = df.dropna(subset=["post_id", "title", "score"])
    print(f"After removing nulls: {len(df)}")

    # step 3: fix data types ---
    # score and num_comments should be ints, not floats
    # (Pandas sometimes reads them as float64 if there were any nulls)
    df["score"] = df["score"].astype(int)
    df["num_comments"] = df["num_comments"].fillna(0).astype(int)
    # post_id should also be int — just making sure
    df["post_id"] = df["post_id"].astype(int)

    #  step 4: remove low-quality stories (score < 5) ---
    # Anything below 5 upvotes is basically noise
    df = df[df["score"] >= 5]
    print(f"After removing low scores: {len(df)}")

    #  step 5: clean up whitespace in the title column ---
    # strip leading/trailing spaces; .str.strip() handles it nicely
    df["title"] = df["title"].str.strip()

    return df


def save_csv(df):
    """Saves the cleaned DataFrame to data/trends_clean.csv."""

    # make sure data/ exists (it should from Task 1 but just in case)
    os.makedirs("data", exist_ok=True)

    output_path = "data/trends_clean.csv"

    # index=False so we don't get an ugly unnamed column at the start
    df.to_csv(output_path, index=False, encoding="utf-8")

    print(f"\nSaved {len(df)} rows to {output_path}")
    return output_path


def print_category_summary(df):
    """Prints how many stories ended up in each category."""
    print("\nStories per category:")

    # value_counts gives us counts sorted by frequency, but I'd rather
    # show them in a consistent order so sorting by index instead
    counts = df["category"].value_counts().sort_index()

    for cat, count in counts.items():
        # left-aligning the category name in a 16-char field looks cleaner
        print(f"  {cat:<16} {count}")


def main():
    print("TrendPulse — Task 2: Cleaning & Processing")
    print("=" * 45)

    # --- Step 1: load ---
    try:
        json_path = find_json_file()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    df = load_data(json_path)

    # --- Step 2: clean ---
    df = clean_data(df)

    # quick sanity check on final row count
    print(f"\n{len(df)} stories passed all quality checks.")

    # --- Step 3: save + summary ---
    save_csv(df)
    print_category_summary(df)


if __name__ == "__main__":
    main()
