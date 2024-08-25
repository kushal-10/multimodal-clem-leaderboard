## REQUIRED OUTPUT ###
# A list of version names -> v1.6, v.6_multimodal, v1.6_quantized, v1.5, v0.9, etc......
# A corresponding DataFrame?

import requests
from datetime import datetime
import pandas as pd
import json
from io import StringIO

from src.leaderboard_utils import process_df
from src.assets.text_content import REPO

def get_versions_data():
    """
    Read and process data from CSV files of all available versions hosted on GitHub. - https://github.com/clembench/clembench-runs

    Returns:
        versions_data:
            -
    """
    base_repo = REPO
    json_url = base_repo + "benchmark_runs.json"
    response = requests.get(json_url)

    # Check if the JSON file request was successful
    if response.status_code != 200:
        print(f"Failed to read JSON file: Status Code: {response.status_code}")
        return None, None, None, None

    json_data = response.json()
    versions = json_data['versions']

    # Sort version names - latest first
    # Convert to a list of ints to compare ambiguities | example - 1.6.5 with 1.6
    int_version_names = []
    for ver in versions:
        version_str = ver['version']
        ver_splits = version_str[1:].split('.')
        ver_splits = [int(v_split) for v_split in ver_splits]
        if ver_splits[0] >= 1 and ver_splits[1] >= 5:
            int_version_names.append(ver_splits)
    sorted_version_names = sorted(int_version_names, reverse=True)

    version_names = []
    for v in sorted_version_names:
        version_str = "v"
        for i in v:
            version_str += str(i) + "."
        version_str = version_str[:-1]
        version_str += "_multimodal"
        version_names.append(version_str)

    print(f"Found {len(version_names)} versions from get_versions_data(): {version_names}.")

    # Get Last updated date of the latest version
    latest_version = version_names[0]
    latest_date = next(
        ver['date'] for ver in versions if ver['version'] == latest_version.split("_")[0]
    )
    formatted_date = datetime.strptime(latest_date, "%Y/%m/%d").strftime("%d %b %Y")

    # Get Versions data
    versions_data = {"latest": latest_version, "date": formatted_date}

    # Collect Dataframes
    dfs = []

    for version in version_names:
        mm_url = f"{base_repo}{version}/results.csv"
        print(mm_url)
        # Multimodal Data
        mm_response = requests.get(mm_url)
        if mm_response.status_code == 200:
            mm_df = pd.read_csv(StringIO(mm_response.text))
            mm_df = process_df(mm_df)
            mm_df = mm_df.sort_values(by=mm_df.columns[1], ascending=False)  # Sort by clemscore column
            versions_data[version] = mm_df
        else:
            print(f"Failed to read multimodal leaderboard CSV file for version: {version}: Status Code: {mm_response.status_code}. Please ignore this message if multimodal results are not available for this version")

    print("INSIDEEE VEr Data")
    print(versions_data)

    return versions_data


if __name__ == "__main__":
    versions_data = get_versions_data()
    print(versions_data.keys())
