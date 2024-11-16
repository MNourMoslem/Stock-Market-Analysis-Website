from django.db import models

class Sector(models.Model):
    name = models.CharField(max_length=50, default="Unknown")

    def __str__(self):
        return self.name

class Country(models.Model):
    name = models.CharField(max_length=70, default="Unknown")

    def __str__(self):
        return self.name

class Industry(models.Model):
    name = models.CharField(max_length=60, default="Unknown")
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name="industry_sector")

    def __str__(self):
        return self.name

class Stock(models.Model):
    symbol = models.CharField(max_length=20, default="Unknown")
    brand = models.CharField(max_length=100, default="Unknown")
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, related_name="stock_industry")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="stock_country")
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    market_cap = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, default=0)

    def __str__(self):
        return f"{self.symbol} ({self.brand})"

    def update_stock_from_history(self):
        last_history = self.history_entries.order_by('-date').first()
        if last_history:
            self.price = last_history.close_price
            self.market_cap = last_history.market_cap
            self.save()

class History(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='history_entries')
    date = models.DateTimeField(null=True, blank=True)
    open_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    high_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    low_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    close_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    volume = models.BigIntegerField(null=True, blank=True)
    dividends = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    stock_splits = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shares_outstanding = models.BigIntegerField(default=0, null=True, blank=True)
    market_cap = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)

    def __str__(self):
        return f"History Entry for Stock {self.stock.symbol} on {self.date}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.stock.update_stock_from_history()
