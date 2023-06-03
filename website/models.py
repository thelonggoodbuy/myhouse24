from django.db import models



class MainPage(models.Model):
    title = models.CharField(max_length=200)
    short_descriptions = models.TextField()
    show_app_link = models.BooleanField()
    seo_block = models.OneToOneField('SeoBlock', on_delete=models.CASCADE, blank=True, null=True, related_name='main_page')


class AboutUsPage(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    director_photo =  models.ImageField(blank=True, verbose_name='Фото директора', upload_to='galery/')
    addition_title = models.CharField(max_length=200, blank=True, null=True)
    addition_short_description = models.TextField(blank=True, null=True)
    seo_block = models.OneToOneField('SeoBlock', on_delete=models.CASCADE, blank=True, null=True)

class Document(models.Model):
    TARGET_CHOICES = (
        ('about_us', 'о нас'),
        )
    file = models.FileField(verbose_name='Файл', upload_to='document/')
    target = models.CharField(max_length=200, choices=TARGET_CHOICES)
    title = models.CharField(max_length=200, null=True, blank=True)


class ServicesPage(models.Model):
    seo_block = models.OneToOneField('SeoBlock', on_delete=models.CASCADE, blank=True, null=True)


class ContactPage(models.Model):
    title = models.CharField(max_length=200)
    simple_text = models.TextField()
    full_name = models.CharField(max_length=400)
    location = models.TextField()
    address = models.CharField(max_length=400)
    phone = models.CharField(max_length=200)
    email = models.EmailField(max_length=400)
    link_to_commercial_cite = models.URLField(max_length=400)
    map_code = models.TextField()
    seo_block = models.OneToOneField('SeoBlock', on_delete=models.CASCADE, null=True, blank=True)
    

class TariffPage(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    seo_block = models.OneToOneField('SeoBlock', on_delete=models.CASCADE, blank=True, null=True)


class SeoBlock(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    keyword = models.TextField()


class SlideBlock(models.Model):
    TARGET_CHOICES = (
        ('main_page_slider', 'Главная страница слайдер'),
        ('main_page_around', 'Главная страница рядом с нами'),
        ('about_us_galery', 'О нас, галерея'),
        ('about_us_addition_galery', 'О нас, дополнительная галерея'),
        ('services', 'Услуги'),
        ('tariff', 'Тариф'),
    )

    image = models.ImageField(blank=True, verbose_name='фото', upload_to='galery/')
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    target = models.CharField(max_length=200, choices=TARGET_CHOICES)