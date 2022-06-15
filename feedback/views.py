from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import CompanyForm,FeedbackForm
import json
import datetime
import graphos

from .fusioncharts import FusionCharts
from .models import Company,Feedback
from django.core.mail import send_mail


data = [
        ['Year', 'Sales', 'Expenses'],
        [2004, 1000, 400],
        [2005, 1170, 460],
        [2006, 660, 1120],
        [2007, 1030, 540]
    ]

def detail(request, company_id):

    try:
        company = Company.objects.get(pk=company_id)
    except Company.DoesNotExist:
        raise Http404("Company does not exist")
    company_list = Company.objects.all()
    context = {
        "company_list": company_list,
        "company": company,

    }
    return render(request,'detail.html',context)


def review(request, company_id):
    if request.POST:
        form = FeedbackForm(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            return HttpResponseRedirect('/thanks')
    else:
        form = FeedbackForm()

    try:
        company = Company.objects.get(pk=company_id)
    except Company.DoesNotExist:
        raise Http404("Company does not exist")
    context = {
        "company": company,
        "form": form,

    }
    return render(request, 'company_reviews.html', context)


def index(request):
    is_employee = request.user.groups.filter(name='Employees').exists()
    is_manager = request.user.groups.filter(name='Managers').exists()

    if is_employee:
        company_list = Company.objects.filter(employee=request.user)
        context = {
            "companies": company_list,
            "is_employee": is_employee,
            "is_manager": is_manager
        }

        return render(request, 'employee_index.html', context)
    elif request.user.is_staff:

        dataSource = {}
        # setting chart cosmetics
        dataSource['chart'] = {
            "caption": "Graph for Companies versus their respective reviews",
            "borderAlpha": "20",
            "canvasBorderAlpha": "0",
            "usePlotGradientColor": "0",
            "xaxisname": "Companies",
            "yaxisname": "Reviews",
            "plotBorderAlpha": "10",
            "showXAxisLine": "1",
            "xAxisLineColor": "#999999",
            "showValues": "0",
            "divlineColor": "#999999",
            "divLineIsDashed": "1",
            "showAlternateHGridColor": "0",
            "exportEnabled": "1"
        }

        reviewsDataSource = {}
        # setting chart cosmetics
        reviewsDataSource['chart'] = {
            "caption": "Number of reviews added",
            "subcaption":"Last Year",
            "borderAlpha": "20",
            "canvasBorderAlpha": "0",
            "usePlotGradientColor": "0",
            "xaxisname": "Months",
            "yaxisname": "Reviews",
            "plotBorderAlpha": "10",
            "showXAxisLine": "1",
            "xAxisLineColor": "#999999",
            "showValues": "0",
            "divlineColor": "#999999",
            "divLineIsDashed": "1",
            "showAlternateHGridColor": "0",
            "exportEnabled": "1"
        }

        reviewsDataSource['data'] = []

        for i in range(1, 13):
            data = {}
            currentMonth = datetime.date(2008, i, 1).strftime('%B')
            data['label'] = currentMonth
            count = 0
            for key in Feedback.objects.all():
                if currentMonth == key.timestamp.strftime("%B"):
                    count = count + 1
            data['value'] = count
            reviewsDataSource['data'].append(data)

        dataSource['data'] = []
        # The data for the chart should be in an array wherein each element of the array is a JSON object as
        # `label` and `value` keys.
        # Iterate through the data in `Country` model and insert in to the `dataSource['data']` list.
        for key in Company.objects.all():
            data = {}
            data['label'] = key.name
            data['value'] = Feedback.objects.filter(company=key).count()
            dataSource['data'].append(data)

        column2D = FusionCharts("column2D", "ex1", "600", "400", "chart-1", "json", dataSource)

        column3D = FusionCharts("column2D", "ex2", "600", "400", "chart-2", "json", reviewsDataSource)

        company_list = Company.objects.all()
        review_list = Feedback.objects.all()
        employees = User.objects.filter(groups__name='Employees')
        managers = User.objects.filter(groups__name='Managers')


        context = {
            "companies": company_list,
            "employees": employees,
            "managers": managers,
            "chart": column2D.render(),
            "chart2": column3D.render(),
            "reviews": review_list,
            "latestReviews": Feedback.objects.order_by('-timestamp')[:5]
        }

        return render(request, 'admin_index.html', context)
    elif is_manager:
        employees = User.objects.filter(groups__name='Employees')
        companies = Company.objects.all()

        context = {
            "employees": employees,
            "companies": companies
        }

        return render(request,'manager_index.html', context)
    else:
        companies = Company.objects.all()

        context = {
            "companies": companies,
        }

        return render(request,'customer_index.html', context)


def thanks(request):
    return render(request,'thank-you.html')

@login_required(login_url='/accounts/login/')
def create_company(request):
    if request.POST:
        form = CompanyForm(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            return HttpResponseRedirect('/thanks')
    else:
        form = CompanyForm()
    return render(request,'create_company.html',{'form':form })

def create_review(request,company_id):
    try:
        company = Company.objects.get(pk=company_id)
    except Company.DoesNotExist:
        raise Http404("Company does not exist")
    if request.POST:
        form = FeedbackForm(request.POST)
        url = '/'
        data = json.dumps(url)

        if form.is_valid():

            instance = form.save(commit=False)
            instance.company = company
            instance.save()
            sendEmployeeEmailOnAddReview(company,form)
            return HttpResponse(data, content_type='application/json')
    else:
        form = FeedbackForm()
    context = {
        "company": company,
        "form": form,

    }

    return render(request,'create_review.html',context)

from django.template.loader import render_to_string

def sendEmployeeEmailOnAddReview(company,form):
    subject, from_email, to = "Tech Greatness.com : A customer has added a review","irungu214@gmail.com", \
                              company.employee.email

    context = {
        "employee": company.employee.get_full_name(),
        "company": company,
        "form": form,
        "first_name": form.cleaned_data['first_name'],
        "last_name": form.cleaned_data['last_name'],
        "comment": form.cleaned_data['comment'],
    }

    msg_plain = render_to_string('add_review_email_template.txt', context)
    msg_html = render_to_string('add_review_email_template.html', context)

    send_mail(subject, msg_plain, from_email, [to], fail_silently=False, html_message=msg_html)










