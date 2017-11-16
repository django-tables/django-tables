from django.db import models


class City(models.Model):
    name = models.TextField()
    population = models.IntegerField(null=True)

    class Meta:
        app_label = 'testapp'


class Country(models.Model):
    name = models.TextField()
    population = models.IntegerField()
    capital = models.ForeignKey(City, blank=True, null=True)
    tld = models.TextField(verbose_name='Domain Extension', max_length=2)
    system = models.TextField(blank=True, null=True)
    # tests expect this to be always null!
    null = models.TextField(blank=True, null=True)
    null2 = models.TextField(blank=True, null=True)  # - " -

    def example_domain(self):
        return 'example.%s' % self.tld

    class Meta:
        app_label = 'testapp'
        db_table = 'country'
