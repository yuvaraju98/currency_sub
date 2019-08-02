from django.shortcuts import redirect,render
from .forms import DataForm
from .tasks import process,validate_fields
from .charts import LineChart



def _form_view(request, template_name='currency/basic2.html', form_class=DataForm,comment='',line_chart=LineChart({'label':0}),table={}):

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            pass
    else:
        form = form_class()
    return render(request, template_name, {'form': DataForm,'comment':comment,'line_chart':line_chart,'rows':table})


def basic(request,comment=''):
    return _form_view(request,comment=comment)

def check(request):
    error_field_message = validate_fields(request)
    if (error_field_message):
        return _form_view(request,comment=error_field_message)
    else:
        return upload(request)

def upload(request):
    points=process(request)
    return _form_view(request,comment='',line_chart=LineChart(points),table=points)


def dis(request):
    return render(request, 'currency/chart.html', {
            'line_chart': LineChart([1,2,3]),
        })


