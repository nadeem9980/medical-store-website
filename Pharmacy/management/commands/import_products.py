import csv
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from ...models import Medicine


class Command(BaseCommand):
    help = "Import products from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv", type=str, required=True, help="The path to the CSV file to import"
        )

    def handle(self, *args, **options):
        csv_path = options["csv"]

        try:
            with open(csv_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                count = 0

                for row in reader:
                    try:
                        expiry_date = None
                        if row.get("expiry_date"):
                            expiry_date = datetime.strptime(
                                row["expiry_date"], "%Y-%m-%d"
                            ).date()

                        product, created = Medicine.objects.update_or_create(
                            name=row["name"],
                            defaults={
                                "details": row.get("details", ""),
                                "link": row.get("link", ""),
                                "group": row.get("group", ""),
                                "brand": row.get("brand", ""),
                                "batch_no": row.get("batch_no", ""),
                                "expiry_date": expiry_date,
                                "created_at": datetime.strptime(
                                    row["created_at"], "%Y-%m-%d %H:%M:%S"
                                ),
                                # "added_by": int(row.get("added_by_id", 1)),
                                "image": row.get("image", ""),
                                "price": float(row.get("price", 0)),
                            },
                        )
                        count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"Processed: {product.name}")
                        )

                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Error processing row {row}: {e}")
                        )

                self.stdout.write(
                    self.style.SUCCESS(f"Successfully imported {count} products.")
                )

        except FileNotFoundError:
            raise CommandError(f"File '{csv_path}' does not exist")
