# Generated migration for finance_type and collection_day on FinanceGroup

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_loanhistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='financegroup',
            name='collection_day',
            field=models.CharField(
                choices=[
                    ('monday', 'Monday'),
                    ('tuesday', 'Tuesday'),
                    ('wednesday', 'Wednesday'),
                    ('thursday', 'Thursday'),
                    ('friday', 'Friday'),
                    ('saturday', 'Saturday'),
                    ('sunday', 'Sunday'),
                ],
                default='monday',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='financegroup',
            name='finance_type',
            field=models.CharField(
                choices=[('daily', 'Daily'), ('weekly', 'Weekly')],
                default='daily',
                max_length=10,
            ),
        ),
    ]
