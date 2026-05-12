import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_review_queue_bookoffer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookoffer',
            name='queue_user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='book_offers',
                to='profiles.queueuser',
            ),
        ),
        migrations.AddField(
            model_name='bookoffer',
            name='seller',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='offers_sold',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='bookoffer',
            name='buyer',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='offers_bought',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='bookoffer',
            name='queue',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='offers',
                to='profiles.queue',
            ),
        ),
    ]
