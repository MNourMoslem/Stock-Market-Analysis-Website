from django.db import models

class Stock(models.Model):
    symbol = models.CharField(max_length=20, default="Unknown")
    brand = models.CharField(max_length=100, default="Unknown")
    industry = models.CharField(max_length=100, default="Unknown")
    country = models.CharField(max_length=100, default="Unknown")
    sector = models.CharField(max_length=100, default="Unknown")
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    market_cap = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)

    def __str__(self):
        return f"{self.symbol} ({self.brand})"

    # Method to update price and market cap based on the latest history entry
    def update_stock_from_history(self):
        last_history = self.history_entries.order_by('-date').first()
        if last_history:
            self.price = last_history.close_price
            self.market_cap = last_history.market_cap
            self.save()

class History(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='history_entries')
    date = models.DateTimeField()
    open_price = models.DecimalField(max_digits=12, decimal_places=2)
    high_price = models.DecimalField(max_digits=12, decimal_places=2)
    low_price = models.DecimalField(max_digits=12, decimal_places=2)
    close_price = models.DecimalField(max_digits=12, decimal_places=2)
    volume = models.BigIntegerField()
    dividends = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    stock_splits = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shares_outstanding = models.BigIntegerField(default=0)
    market_cap = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)

    def __str__(self):
        return f"History Entry for Stock {self.stock.symbol} on {self.date}"

    # Override save method to update the stock's price and market cap after saving the history
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.stock.update_stock_from_history()
