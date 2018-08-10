# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect,render_to_response
from django.http import HttpResponse
import json
import re
from restkit import Resource, BasicAuth, request, errors
import requests
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



def homepage(request):
    
    _message = ""

    if request.method == 'POST':
        
        if 'login' in request.POST:

            _username = request.POST['username']
                
            _password = request.POST['password']
            
            auth = BasicAuth(_username, _password)
            
            issuedic =  issues(auth, 1)
            
            if issuedic is None:

                _message = "either your jira username or password is incorrect"
            
            else:
                
                global Auth
                
                Auth = auth
                
                global username
                
                username = _username
                
                global password
                
                password = _password
                
                return redirect('filter')

    context = {'message' : _message }
    
    return render(request, 'myaccount/home.html', context)

def issuehome(request):

    _message = ""
    
    issuedic =  issues(Auth, 2)
    if request.method == 'POST':

        if request.is_ajax():
            # extract your params (also, remember to validate them)
            param =  request.POST.getlist('param[]', None)
            updatvaluelist = []
            for v in param:
                updatevalue = [x.strip() for x in v.split(',') if x != '']
                key = updatevalue[0].encode('utf-8')
                work = updatevalue[1].encode('utf-8')
                bill = updatevalue[2].encode('utf-8')
                clientname = updatevalue[3].encode('utf-8')
                updatvaluelist.append([key,work,bill,clientname])
        
            udpateJira(updatvaluelist)

    if (issuedic is None) or (bool(issuedic) == False) :

        _message = "Please verify your jira credential"
        
        context = {'message' : _message}
    
    else:
        page = request.GET.get('page', 1)
        paginator = Paginator(issuedic.keys(), 100)
        try:
            keys = paginator.page(page)
        except PageNotAnInteger:
            keys = paginator.page(1)
        except EmptyPage:
            keys = paginator.page(paginator.num_pages)
        
        #type of work drop downlist
        twdropdown = ["CFD - Client Specifications", "CFD - Roadmap Acceleration","Cust Dev - Maintenance Acceleration", "Cust Enablement", "Partner Enablement", "RoadMap", "Maintenance", "Admin"]
        #billable dropdownlist
        badropdown = ["Yes","No"]
        #client dropdown(removed unstructured client name)
        clientname_dropdown=["ACE","Athleta","Bakers Footwear Group","Beachbody","Boston Proper","BRP","Burpee","Carolina Biological Supply","Country Curtains","Cuddledown","Current USA","Destination Maternity","Ducati","French Toast","Garden Botanika","Intermix","Klipsch Group","Laura Canada","MarketLive","Matalan","Mizuno","Polaris Sales","RedEnvelope","Roots Canada","Simomo","Sportif","Sundance","Suzuki","The Level Group","Title 9","Touch of Class","Tourneau","Trek","Vitec","Zia","Mall of America","Bluefly","Perrigo","Sigma Beauty","Jelly Belly","K2 Sports","K2 Mountain","Orgill","Pearson VUE","Dani Johnson","Cracker Barrel","Aubuchon Hardware","Bees Lighting","Shindgiz","Sun and Ski","Elisa Illana","Far Bank","Total Home Supply","Pink  Coconut","Full Throttle Parts","Ya Ya","GoRuck","Echidna","Boathouse Sports","Goulet Pens","Super ATV","Seismic Audio","VOLT","LKQ","Lobels","Wolters Kluwer","Brother Canada"]
        context = {'issuedic' :  issuedic,
                    'keys' : keys,
                    'twdropdown': twdropdown,
                    'badropdown' : badropdown,
                    'clientname_dropdown' : clientname_dropdown }

    return render(request, 'myaccount/issuehome.html', context)

def filter(request):
    if request.method == 'POST':
        query = request.POST['advanced-search']
        query = query.replace(" ", "%20")
        global Query
        Query = query
        return redirect('issuehome')

    return render(request, 'myaccount/filter.html')


def issues(auth, select):
    if select == 1:

        issueQuery = 'issuekey%20=PPB-8003'
    
    else:
    
        issueQuery = Query
    
    issueQuery = 'https://jira.kibocommerce.com/rest/api/latest/search/?jql='+issueQuery+'&maxResults=1000'
    issueInfo= jiraConnection(issueQuery, auth)
    
    if issueInfo is None:
    
        return None

    issuedic = {}
    
    for issue in issueInfo['issues']:
        
        if issue['fields']['customfield_12302'] == None:
        
            EpicLink = ""
            if issue['fields']['customfield_10410'] == None:
                EpicLink = "N/A"
            else:
                EpicLink =issue['fields']['customfield_10410']
            
            Typeofwork = ""
            
            if issue['fields']['customfield_12302'] == None:
                Typeofwork = "None"
            else:
                Typeofwork =issue['fields']['customfield_12302']['value'].encode('utf-8')

            Billable = ""
            if issue['fields']['customfield_10111'] == None:
                Billable = "None"
            else:
                Billable = issue['fields']['customfield_10111']['value'].encode('utf-8')

            Clientname = ""
            if issue['fields']['customfield_11711'] == None:
                Clientname = "None"
            else:
                Clientname = issue['fields']['customfield_11711']['value'].encode('utf-8')

            issuedic2 = {issue['key'].encode('utf-8'):[issue['fields']['summary'].encode('utf-8'),EpicLink,Typeofwork,Billable,Clientname]}

            issuedic.update(issuedic2)

    return issuedic

#connect to Jira API
def jiraConnection(query,auth):
    
    try:
        resource = Resource(query, filters=[auth])
        
        response = resource.get(headers = {'Content-Type' : 'application/json'})

    except errors.Unauthorized:
        
        print("Error::Incorrect Username/Pwd combination, please resubmit. If you think you type in the right credential, please try log in from broswer first. It might caused by Jira captcha validation")

        return None
    
    if response.status_int == 200:
        
        """ issue is the JSON representation of the issue """
        issue = json.loads(response.body_string())
        
        return issue
    
    else:
        
        return None

def udpateJira(updatvaluelist):
    
    
    headers = {'Content-Type': 'application/json'}

    for k in updatvaluelist:
        
        data = ''
        if(k[1] == "None" ):
            if(k[2] == "None"):
                data = '{"fields":{"customfield_11711":{"value":"'+k[3]+'"}}}'
            
            elif(k[3] == "None"):
                data = '{"fields":{"customfield_10111":{"value":"'+k[2]+'"}}}'
            
            else:
                data =  '{"fields":{"customfield_10111":{"value":"'+k[2]+'"},"customfield_11711":{"value":"'+k[3]+'"}}}'
        
        elif(k[2] == "None"):
            if(k[1] == "None"):
                data = '{"fields":{"customfield_11711":{"value":"'+k[3]+'"}}}'
            
            elif(k[3] == "None") :
                data = '{"fields":{"customfield_12302":{"value":"'+k[1]+'"}}}'
            else:
                data =  '{"fields":{"customfield_12302":{"value":"'+k[1]+'"},"customfield_11711":{"value":"'+k[3]+'"}}}'
        
        elif(k[3] == "None"):
            if(k[1] == "None") :
                data = '{"fields":{"customfield_10111":{"value":"'+k[2]+'"}}}'

            elif(k[2] == "None") :
                data = '{"fields":{"customfield_12302":{"value":"'+k[1]+'"}}}'
            else:
                data = '{"fields":{"customfield_12302":{"value":"'+k[1]+'"},"customfield_10111":{"value":"'+k[2]+'"}}}'
        else:
        
            data = '{"fields":{"customfield_12302":{"value":"'+k[1]+'"},"customfield_10111":{"value":"'+k[2]+'"},"customfield_11711":{"value":"'+k[3]+'"}}}'


        requests.put('https://jira.kibocommerce.com/rest/api/2/issue/'+k[0], headers=headers, data=data, auth=(username,password ))


    x = "update succsefull"

    return x

def handler404(request):
    
    return render(request, 'exception/404.html', status=404)

def handler500(request):
    
    return render(request, 'exception/500.html', status=500)










