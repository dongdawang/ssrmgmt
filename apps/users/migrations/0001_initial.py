# Generated by Django 2.0.6 on 2018-10-10 16:28

import datetime
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('node', '0001_initial'),
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('nick_name', models.CharField(default='', max_length=20, verbose_name='昵称')),
                ('birthday', models.DateField(blank=True, null=True, verbose_name='生日')),
                ('gender', models.CharField(choices=[('male', '男'), ('female', '女')], default='male', max_length=6, verbose_name='性别')),
                ('address', models.CharField(default='', max_length=100, verbose_name='地址')),
                ('mobile', models.CharField(blank=True, max_length=11, null=True, verbose_name='手机号')),
                ('profile_photo', models.ImageField(default='image/default.png', upload_to='image/%Y/%m', verbose_name='用户头像')),
                ('coin_nums', models.DecimalField(blank=True, decimal_places=2, default=10, max_digits=10, null=True, verbose_name='硬币数')),
                ('experience', models.PositiveIntegerField(default=0, help_text='用于计算用户等级', validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)], verbose_name='经验')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name_plural': '用户信息',
                'verbose_name': '用户信息',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='时间')),
                ('body', models.TextField(verbose_name='主体')),
            ],
            options={
                'ordering': ('-time',),
                'verbose_name_plural': '系统公告',
            },
        ),
        migrations.CreateModel(
            name='SSRAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expiration_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='SSR有效期')),
                ('port', models.PositiveIntegerField(unique=True, verbose_name='用户端口')),
                ('passwd', models.CharField(blank=True, max_length=30, null=True)),
                ('method', models.CharField(choices=[('aes-256-cfb', 'aes-256-cfb'), ('aes-128-ctr', 'aes-128-ctr'), ('rc4-md5', 'rc4-md5'), ('salsa20', 'salsa20'), ('chacha20', 'chacha20'), ('none', 'none')], max_length=30, null=True, verbose_name='加密方法')),
                ('protocol', models.CharField(choices=[('auth_sha1_v4', 'auth_sha1_v4'), ('auth_aes128_md5', 'auth_aes128_md5'), ('auth_aes128_sha1', 'auth_aes128_sha1'), ('auth_chain_a', 'auth_chain_a'), ('origin', 'origin')], max_length=30, null=True, verbose_name='协议')),
                ('obfs', models.CharField(choices=[('plain', 'plain'), ('http_simple', 'http_simple'), ('http_simple_compatible', 'http_simple_compatible'), ('http_post', 'http_post'), ('tls1.2_ticket_auth', 'tls1.2_ticket_auth')], max_length=30, null=True, verbose_name='混淆方法')),
                ('obfs_enable', models.BooleanField(default=False, verbose_name='是否启用混淆')),
                ('node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='node.Node', verbose_name='关联的节点')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='所有用户')),
            ],
        ),
        migrations.CreateModel(
            name='UserModifyRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modify_type', models.CharField(choices=[('modify_email', '修改邮箱'), ('modify_password', '修改密码'), ('modify_profile_photo', '修改头像')], max_length=25, verbose_name='修改类型')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='添加时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='账号')),
            ],
            options={
                'verbose_name_plural': '账号修改记录',
                'verbose_name': '账号修改记录',
            },
        ),
    ]
