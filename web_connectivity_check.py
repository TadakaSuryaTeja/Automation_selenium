import csv
import requests

web_status_dict = {"Website": "Status"}


def main():
    with open("sites.txt", "r") as fr:
        for line in fr:
            website = line.strip()
            status = requests.get(website).status_code

            if status == 200:
                web_status_dict[website] = "Working"
            else:
                web_status_dict[website] = "Error 404"

    print(web_status_dict)

    ## Saves Websites Status Inside a CSV File
    with open("website_status.csv", "w", newline="") as fw:
        csv_writers = csv.writer(fw)
        for key in web_status_dict.keys():
            csv_writers.writerow([key, web_status_dict[key]])


if __name__ == "__main__":
    main()