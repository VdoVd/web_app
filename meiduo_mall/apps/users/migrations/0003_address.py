# Generated by Django 3.2.16 on 2023-01-05 08:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('areas', '0001_initial'),
        ('users', '0002_alter_user_options_alter_user_managers_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('title', models.CharField(max_length=20, verbose_name='地址名称')),
                ('receiver', models.CharField(max_length=20, verbose_name='收货人')),
                ('place', models.CharField(max_length=50, verbose_name='地址')),
                ('mobile', models.CharField(max_length=11, verbose_name='手机')),
                ('tel', models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='固定电话')),
                ('email', models.CharField(blank=True, default='', max_length=30, null=True, verbose_name='电子邮箱')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='逻辑删除')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='city_addresses', to='areas.area', verbose_name='市')),
                ('district', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='district_addresses', to='areas.area', verbose_name='区')),
                ('province', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='province_addresses', to='areas.area', verbose_name='省')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '用户地址',
                'verbose_name_plural': '用户地址',
                'db_table': 'tb_address',
                'ordering': ['-update_time'],
            },
        ),
    ]