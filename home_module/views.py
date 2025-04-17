from django.shortcuts import render
from django.views.generic import TemplateView
from announcement_module.models import Announcements
from site_settings_module.models import SiteSettings


class IndexView(TemplateView):
    template_name = 'index_page.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        announcements = Announcements.objects.order_by('-created_date')[:4]
        site_settings = SiteSettings.objects.first()
        context['announcements'] = announcements
        context['site_settings'] = site_settings
        return context


