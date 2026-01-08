from django.http import HttpResponse, HttpResponseServerError


def home(request):
    return HttpResponse("OK")


def liveness(request):
    return HttpResponse("OK")


def readiness(request):
    try:
        return HttpResponse("OK")
    except Exception as e:
        return HttpResponseServerError("db: cannot connect to database.")
