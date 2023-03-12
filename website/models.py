from django.db import models



class MainPage(models.Model):
    title = models.CharField(max_length=200)
    short_descriptions = models.TextField()
    show_app_link = models.BooleanField()
    seo_block = models.OneToOneField('SeoBlock', on_delete=models.CASCADE)


class AboutUsPage(models.Model):
    title = models.CharField(max_length=200)
    short_description = models.TextField()
    director_photo =  models.ImageField(blank=True, verbose_name='Фото директора', upload_to='galery/')
    seo_block = models.OneToOneField('SeoBlock', on_delete=models.CASCADE)


class ServicesPage(models.Model):
    seo_block = models.OneToOneField('SeoBlock', on_delete=models.CASCADE)


class ContactPage(models.Model):
    title = models.CharField(max_length=200)
    simple_text = models.TextField()
    url = models.URLField()
    full_name = models.CharField(max_length=400)
    location = models.TextField()
    address = models.CharField(max_length=400)
    phone = models.CharField(max_length=200)
    email = models.EmailField(max_length=400)
    link_to_commercial_cite = models.URLField(max_length=400)
    map_code = models.TextField()
    seo_block = models.OneToOneField('SeoBlock', on_delete=models.CASCADE)
    

class SeoBlock(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    keyword = models.TextField()


class SlideBlock(models.Model):
    image = models.ImageField(blank=True, verbose_name='фото', upload_to='galery/')
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)