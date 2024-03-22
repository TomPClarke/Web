from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from myApp.models import Author, Story
from django.contrib.auth.models import User

import json
from datetime import date, datetime
# Create your views here.

@csrf_exempt
def APILogin(request):
    response = HttpResponse()
    response['Content-Type'] = "text/plain"

    if(request.method != 'POST'):
        response.content = "Only POST requests are allowed for this resource.\n"
        response.status_code = 405 #Wrong request Status Code
        return response


    if(request.method == 'POST'):

        # Have the correct Format
        if request.headers.get('Content-Type') != "application/x-www-form-urlencoded":
            response.content = "Server was expecting \"application/x-www-form-urlencoded\" Content-Type\n"
            response.status_code = 415
            return response

        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username,password=password)

        if(user is not None):
            login(request, user)
            account = Author.objects.get(user=user)
            request.session['user_id'] = account.id
            response.content = (f"Hello, {account.name}. \nYou have been successfully logged in.\n")
            response.status_code = 200 #OK
            response.reason_phrase = 'OK' 
        else:
            response.content = ("No Author matching those credentials could be found.\n")
            response.status_code = 401 #Unauthorised 
    return response

@csrf_exempt
def APILogout(request):
    response = HttpResponse()
    response['Content-Type'] = "text/plain"

    if(request.method != 'POST'):
        response.content = "Only POST requests are allowed for this resource.\n"
        response.status_code = 405 #Wrong request Status Code
        return response

    if(request.method == 'POST'):
        try:
            user_id = request.session.get('user_id')
            account = Author.objects.get(id=user_id)
            logout(request)
            response.content = (f"Goodbye, {account.name}. \nYou have been successfully logged out.\n")
            response.status_code = 200
            response.reason_phrase = 'OK'
        except:
            response.content = (f"You are not logged in.\n")
            response.status_code = 401 #Unauthorised 
    return response

@csrf_exempt
def APIQuery_Story(request):
    response = HttpResponse()
    response['Content-Type'] = "text/plain"

    #Just assume something will go wrong
    response.status_code = 503

    if(request.method == 'GET'):
        try:
            if request.headers.get('Content-Type') != "application/x-www-form-urlencoded":
                response.status_code = 503
                response.content = "Server was expecting \"application/x-www-form-urlencoded\" Content-Type\n"
                return response
            

            story_cat = request.GET.get('story_cat')
            story_region = request.GET.get('story_region')
            story_date_str = request.GET.get('story_date')
            
            stories = Story.objects.all()
            if(story_cat != "*"):
                stories = stories.filter(category=story_cat)
            if(story_region != "*"):
                stories = stories.filter(region=story_region)
            if(story_date_str != "*"):
                story_date = datetime.strptime(story_date_str,"%d/%m/%Y")
                stories = stories.filter(date__gte=story_date)
            stories = stories.values()

            if(not stories):
                response.status_code = 404
            else:
                #Let's create the payload
                data = []
                for x in stories:
                    story = {}
                    story['key'] = x['id']
                    story['headline'] = x['headline']
                    story['story_cat'] = x['category']
                    story['story_region'] = x['region']
                    story['author'] = str(Author.objects.get(id=x['author_id']))
                    story['story_date'] = x['date'].strftime("%d/%m/%Y")
                    story['story_details'] = x['details']
                    data.append(story)
                stories = {'stories' : data}
                response = JsonResponse(stories, safe=False)
                print(stories)
                response.status_code = 200
            return response
        except:
            response.status_code = 503
            response.content = "Service unavailable"
            return response

    elif(request.method == 'POST'):
        try:
            if not(request.user.is_authenticated):
                response.status_code = 503
                response.content = "You must be logged in to post a story.\n"
                return response
            if request.headers.get('Content-Type') != "application/json":
                response.status_code = 503
                response.content = "Server was expecting \"application/json\" Content-Type.\n"
                return response

            data = json.loads(request.body)
            headline = data.get("headline")
            category = data.get("category")
            region = data.get("region")
            details = data.get("details")
            user_id = request.session.get('user_id')
            account = Author.objects.get(id=user_id)

            story = Story(
                headline=headline,
                category=category,
                region=region,
                author=account,
                date=date.today(),
                details=details
            )
            story.save()
            response.status_code = 201 #CREATED
            response.content = "Story Successfully added"
            return response
        except:
            response.status_code = 503
            response.content = "Service unavailable"
            return response
    else:
        #Neither a POST or GET request
        response.content = "Only POST & GET requests are allowed for this resource.\n"
        response.status_code = 503
        return response


@csrf_exempt
def APIDelete_Story(request,key):
    response = HttpResponse()
    response['Content-Type'] = "text/plain"
    response.status_code = 503

    if not(request.user.is_authenticated):
        response.content = "You must be logged in to post a story.\n"
        response.status_code = 503
        return response
    if(request.method != 'DELETE'):
        response.content = "Only DELETE requests are allowed for this resource.\n"
        response.status_code = 503
        return response
    
    if(request.method == 'DELETE'):
        try:
            story = Story.objects.get(id=key)
            story.delete()
            response.status_code = 200
            response.content = f"Sucessfully deleted story: {story}"
            return response
        except Story.DoesNotExist:
            response.status_code = 503
            response.content = f"Story with key #{key} could not be found.\n"
            return response
        


