import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import service.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('PIP', 'Pipeline'), ('POW', 'Power line'), ('ELE', 'Electric truss')], max_length=3)),
                ('name', models.CharField(max_length=120)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('geometry', django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=4326)),
            ],
            options={
                'db_table': 'asset',
            },
        ),
        migrations.CreateModel(
            name='Frame',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('index', models.IntegerField()),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
            options={
                'db_table': 'frame',
            },
        ),
        migrations.CreateModel(
            name='Mission',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=120, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('geometry', django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=4326)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='missions', to='service.Asset')),
            ],
            options={
                'db_table': 'mission',
            },
        ),
        migrations.CreateModel(
            name='VideoData',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('file', models.FileField(upload_to='')),
                ('mission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='video', to='service.Mission')),
            ],
            options={
                'db_table': 'video',
            },
        ),
        migrations.CreateModel(
            name='Telemetry',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('time', models.IntegerField(blank=True, null=True)),
                ('roll', models.FloatField(blank=True, null=True)),
                ('pitch', models.FloatField(blank=True, null=True)),
                ('yaw', models.FloatField(blank=True, null=True)),
                ('roll_speed', models.FloatField(blank=True, null=True)),
                ('pitch_speed', models.FloatField(blank=True, null=True)),
                ('yaw_speed', models.FloatField(blank=True, null=True)),
                ('altitude', models.FloatField(blank=True, null=True)),
                ('relative_altitude', models.FloatField(blank=True, null=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('mission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='telemetries', to='service.Mission')),
            ],
            options={
                'db_table': 'telemetry',
            },
        ),
        migrations.CreateModel(
            name='Object',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('INS', 'Insulator')], max_length=3)),
                ('status', models.CharField(choices=[('UNK', 'Unknown')], max_length=3)),
                ('confidence', models.IntegerField()),
                ('x_min', models.IntegerField()),
                ('x_max', models.IntegerField()),
                ('y_min', models.IntegerField()),
                ('y_max', models.IntegerField()),
                ('frame', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='_objects', to='service.Frame')),
            ],
            options={
                'db_table': 'object',
            },
        ),
        migrations.CreateModel(
            name='MissionData',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('UPL', 'Uploaded'), ('PRO', 'Processed')], default='UPL', max_length=3)),
                ('file', models.FileField(upload_to=service.models.upload_to)),
                ('mission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mission_files', to='service.Mission')),
            ],
            options={
                'db_table': 'mission_file',
            },
        ),
        migrations.AddField(
            model_name='frame',
            name='mission',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='frames', to='service.Mission'),
        ),
    ]
