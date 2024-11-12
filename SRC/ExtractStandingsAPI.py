import requests, csv

def get_contest_id_by_name(contest_name):
    response = requests.get("https://codeforces.com/api/contest.list")
    contests = response.json().get("result", [])
    for contest in contests:
        if contest_name.lower() in contest["name"].lower():
            return contest["id"]
    print(f"Contest '{contest_name}' not found.")
    return None

def get_contest_standings(contest_name, division):
    contest_id = get_contest_id_by_name(contest_name)
    if contest_id is None:
        return
    url = f"https://codeforces.com/api/contest.standings?contestId={contest_id}&from=1&count=100"
    response = requests.get(url)
    data = response.json()
    if data["status"] != "OK":
        print(f"Failed to retrieve standings for {contest_name}.")
        return
    standings = data["result"]["rows"]
    with open("contest_standings.csv", mode="a", newline='') as file:
        writer = csv.writer(file)
        file.seek(0, 2)
        if file.tell() == 0:
            writer.writerow(["Contest Name", "Division", "Screen Name", "Standing"])
        for row in standings:
            handle = row["party"]["members"][0]["handle"]
            rank = row["rank"]
            writer.writerow([contest_name, division, handle, rank])
    print(f"Contest standings for '{contest_name}' saved to 'contest_standings.csv'.")

def main():
    with open("Contest.csv", mode="r") as file:
        reader = csv.reader(file)
        next(reader)
        for line in reader:
            contest_name, division = line[0], line[1]
            get_contest_standings(contest_name, division)

if __name__ == "__main__":
    main()
