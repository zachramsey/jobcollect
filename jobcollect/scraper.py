import os
import csv
import datetime as dt
import pandas as pd             # type: ignore
from jobspy import scrape_jobs  # type: ignore

DT_FMT = "%y%m%d"
COLUMNS = ["date_posted", "location", "company", "title",
           "job_url", "job_url_direct", "company_url_direct",
           "min_amount", "max_amount", "currency", "interval"]


def terms_to_search(terms: list) -> str:
    assert len(terms) > 0, "No terms provided"
    for i, term in enumerate(terms):
        if " " in term:
            terms[i] = f"\"{term}\""
    if len(terms) == 1:
        return terms[0]
    else:
        return "(" + " OR ".join(terms) + ")"


def terms_to_regex(terms: list) -> str:
    assert len(terms) > 0, "No terms provided"
    for i, term in enumerate(terms):
        if " " in term:
            terms[i] = f"\'{term}\'"
    return "|".join(terms)


def job_scraper(
        proxy: str,
        results_wanted: int,
        hours_old: int,
        locations: list,
        group: str,
        search_include: list,
        search_exclude: list | None = None,
        title_include: list | None = None,
        title_exclude: list | None = None,
        descr_include: list | None = None,
        descr_exclude: list | None = None):
    print("-" * 40)
    print(f">>> {group}\n")
    # Build search string
    search = ""
    search += terms_to_search(search_include)
    if search_exclude is not None and len(search_exclude) > 0:
        search += " NOT " + terms_to_search(search_exclude)

    # Create a timestamped output directory
    if not os.path.exists("output"):
        os.makedirs("output")
    end = dt.datetime.now()
    start = end - dt.timedelta(hours=hours_old)
    path = f"output/{start.strftime(DT_FMT)}_{end.strftime(DT_FMT)}"
    if not os.path.exists(path):
        os.makedirs(path)

    data = []
    for location in locations:
        print(f"Searching {location}...", end="\r")
        jobs = scrape_jobs(
            site_name=["indeed", "linkedin"],
            search_term=search,
            location=location,
            job_type="fulltime",
            results_wanted=results_wanted,
            proxies=proxy,
            linkedin_fetch_description=True,
            hours_old=hours_old,
            enforce_annual_salary=True,
        )
        if jobs is not None and len(jobs) > 0:
            data.append(jobs)
            print(f"Searching {location}... {len(jobs)} jobs found.")
        else:
            print(f"Searching {location}... No jobs found.")
    df = pd.concat(data, ignore_index=True) if data else pd.DataFrame()

    if df.empty:
        print(f"{group}: No jobs found :(")
        return

    # Process data
    n_jobs = len(df)
    print(f"{group}: {n_jobs} jobs found before filtering")

    print("Removing duplicates...", end="\r")
    df.drop_duplicates(subset=["title", "company", "location"], inplace=True)
    removed = n_jobs - len(df)
    n_jobs = len(df)
    print(f"Removing duplicates... {removed} removed.")

    print("Excluding titles...", end="\r")
    if title_exclude is not None and len(title_exclude) > 0:
        pattern = terms_to_regex(title_exclude)
        df = df[~df["title"].str.contains(pattern, case=False, na=False)]
    removed = n_jobs - len(df)
    n_jobs = len(df)
    print(f"Excluding titles... {removed} removed.")

    print("Filtering titles...", end="\r")
    if title_include is not None and len(title_include) > 0:
        pattern = terms_to_regex(title_include)
        df = df[df["title"].str.contains(pattern, case=False, na=False)]
    removed = n_jobs - len(df)
    n_jobs = len(df)
    print(f"Filtering titles... {removed} removed.")

    print("Excluding descriptions...", end="\r")
    if descr_exclude is not None and len(descr_exclude) > 0:
        pattern = terms_to_regex(descr_exclude)
        df = df[~df["description"].str.contains(pattern, case=False, na=False)]
    removed = n_jobs - len(df)
    n_jobs = len(df)
    print(f"Excluding descriptions... {removed} removed.")

    print("Filtering descriptions...", end="\r")
    if descr_include is not None and len(descr_include) > 0:
        pattern = terms_to_regex(descr_include)
        df = df[df["description"].str.contains(pattern, case=False, na=False)]
    removed = n_jobs - len(df)
    n_jobs = len(df)
    print(f"Filtering descriptions... {removed} removed.")

    print("Final formatting...", end="\r")
    df.sort_values(by="date_posted", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    print("Final formatting... Done.")
    print(f"\n>>> {group}: {len(df)} jobs found!")

    # Save to CSV
    filename = os.path.join(path, f"{group}.csv")
    df.to_csv(filename, columns=COLUMNS,
              index=False, quoting=csv.QUOTE_ALL)
    print(f"\nSaved to {filename}\n")

    return df
