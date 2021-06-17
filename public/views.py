from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.clickjacking import xframe_options_exempt

# Create your views here.
from base.tools import Geoip2Query
from public.models import IPInfo


class IndexView(generic.ListView):
    model = IPInfo
    template_name = 'public/index.html'
    context_object_name = 'ip_info_list'
    geoip_2_query = Geoip2Query()

    @method_decorator(xframe_options_exempt)
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)

    def get_ipaddress(self) -> str:
        request = self.request
        if not request:
            raise RuntimeError(f"无法获取用户IP地址，请在初始化{self.__class__.__name__}的时候添加参数 context={'request': request}")

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(IndexView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        ip = self.get_ipaddress()
        visitor_ip_data = {'ip': ip}
        visitor_ip_data.update(self.geoip_2_query.query_city(ip).raw_dict)
        context['visitor_ip_data'] = visitor_ip_data
        print(context)
        return context

    def get_queryset(self):
        return None
