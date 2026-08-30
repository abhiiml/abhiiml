import os
import requests
import xml.etree.ElementTree as ET

TOKEN = os.environ.get("ACCESS_TOKEN")
USER = os.environ.get("USER_NAME", "abhiiml")

if not TOKEN:
    raise SystemExit("ACCESS_TOKEN is missing.")

HEADERS = {"Authorization": f"Bearer {TOKEN}"}

QUERY = """
query($login:String!) {
  user(login:$login) {
    repositories(first:100, ownerAffiliations:OWNER) {
      totalCount
      nodes { stargazerCount }
    }
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
      }
    }
  }
}
"""


def github_data():
    r = requests.post(
        "https://api.github.com/graphql",
        json={"query": QUERY, "variables": {"login": USER}},
        headers=HEADERS,
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]["user"]


def replace(root, element_id, value):
    for el in root.iter():
        if el.get("id") == element_id:
            el.text = str(value)
            return


def update_svg(filename, data):
    tree = ET.parse(filename)
    root = tree.getroot()
    ET.register_namespace("", "http://www.w3.org/2000/svg")

    replace(root, "repo_data", data["repositories"]["totalCount"])
    replace(root, "star_data", sum(n["stargazerCount"] for n in data["repositories"]["nodes"]))
    replace(root, "follower_data", data["followers"]["totalCount"])
    replace(root, "commit_data", data["contributionsCollection"]["totalCommitContributions"])
    replace(
        root,
        "contrib_data",
        data["contributionsCollection"]["contributionCalendar"]["totalContributions"],
    )

    tree.write(filename, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    data = github_data()
    update_svg("dark_mode.svg", data)
    update_svg("light_mode.svg", data)
    print("Profile SVG statistics updated for", USER)
