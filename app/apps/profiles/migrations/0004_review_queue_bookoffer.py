import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_queue_queueuser_bookoffer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=128, verbose_name='password'),
        ),

        migrations.RenameField(model_name='queue', old_name='nome', new_name='name'),
        migrations.AlterField(
            model_name='queue',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),

        migrations.AlterField(
            model_name='queueuser',
            name='position',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='queueuser',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='queue_users',
                to='profiles.user',
            ),
        ),
        migrations.AlterField(
            model_name='queueuser',
            name='queue',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='queue_users',
                to='profiles.queue',
            ),
        ),
        migrations.AlterModelOptions(
            name='queueuser',
            options={'ordering': ['position']},
        ),
        migrations.AddConstraint(
            model_name='queueuser',
            constraint=models.UniqueConstraint(fields=('user', 'queue'), name='unique_user_per_queue'),
        ),
        migrations.AddConstraint(
            model_name='queueuser',
            constraint=models.UniqueConstraint(fields=('queue', 'position'), name='unique_position_per_queue'),
        ),

        migrations.RenameField(
            model_name='bookoffer',
            old_name='queue_user_position',
            new_name='queue_user',
        ),
        migrations.AlterField(
            model_name='bookoffer',
            name='queue_user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='book_offers',
                to='profiles.queueuser',
            ),
        ),
        migrations.AlterField(
            model_name='bookoffer',
            name='sold',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='bookoffer',
            name='price',
            field=models.PositiveIntegerField(),
        ),
        migrations.AddConstraint(
            model_name='bookoffer',
            constraint=models.UniqueConstraint(
                fields=('queue_user',),
                condition=models.Q(('sold', False)),
                name='unique_active_offer_per_queue_user',
            ),
        ),
    ]
