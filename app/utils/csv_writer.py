import csv

def write_csv(file_path, rows):
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "email", "created_at", "updated_at", "is_deleted"])
        writer.writerows(rows)