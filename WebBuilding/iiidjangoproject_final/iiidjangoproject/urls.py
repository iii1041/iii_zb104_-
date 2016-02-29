from django.conf.urls import include, url
from django.contrib import admin
from iiimap.views import viewtag_attr,viewTag,aprioritest,test,textcloud

urlpatterns = [
    # Examples:
    # url(r'^$', 'iiiproject.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
	url(r'^viewtag/$',viewTag),
	url(r'^tagattr/$',viewtag_attr),
	url(r'^testmap/$',viewtag_attr),
	url(r'^testap/$',aprioritest),
	url(r'^test/$',test),
	url(r'^textcloud/$',textcloud),


]
