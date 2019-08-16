
from django.shortcuts import redirect,render
import datetime
from . import views
from .forms import DataForm
import pandas as pd
from .training import train,transform,predict_values,predict_transform
import requests
# from django.core.cache import cache
from django_redis import get_redis_connection
cache= get_redis_connection("default")


def validate_fields(requests):
    try:
        data=upload(requests)
    except:
        return "Please enter valid details"
    date=data['date']
    available_currencies=['CAD', 'HKD', 'ISK', 'PHP', 'DKK', 'HUF', 'CZK', 'AUD', 'RON', 'SEK', 'IDR', 'INR',
                          'BRL', 'RUB', 'HRK', 'JPY', 'THB', 'CHF', 'SGD', 'PLN', 'BGN', 'TRY', 'CNY', 'NOK', 'NZD',
                          'ZAR', 'USD', 'MXN', 'ILS', 'GBP', 'KRW', 'MYR']
    if len(data['base'])!=3:
        return "Please enter valid base currency"
    elif data['base'] not in available_currencies:
        return "Please enter valid currency"

    if len(data['target']) != 3:
        return "Please enter valid target currency"
    elif data['target'] not in available_currencies:
        return "Please enter valid currency"

    try:
        int(data['maxdays'])
    except:
        return "Please enter only numbers"
    try:
        if(int(data['amount']))<=0:
            return "Please enter amount greater than 0"
    except:
        return "Please enter only numbers"
    date_format = '%Y-%m-%d'
    try:
        date_obj = datetime.datetime.strptime(date ,date_format)
    except :
        return "Incorrect data format, should be YYYY-MM-DD"


def process(request):
    
    # Retrieve the data
    data=upload(request)  
    
    #  Get data from the API or from cache
    response = get_data(data)
    
    # Extract the feature variables 
    x_train,y_train=transform(response)
    
    # train the model
    logreg=train_model(x_train,y_train)
    
    # forecast the value from start date to wait date
    get_predicted_array = predict(logreg,data)

    print(get_predicted_array)
    return get_predicted_array

def upload(request):
    data=dict()
    data['base'] = str(request.POST.get('base')).upper()
    data['target'] = str(request.POST.get('target')).upper()
    data['date'] = request.POST.get('date')
    data['maxdays'] = request.POST.get('maxdays')
    data['amount'] = request.POST.get('amount')
    data['req_date'] = data['date']

    if pd.to_datetime(data['date'])> pd.datetime.now():
        data['date']=str(pd.datetime.now().date().strftime('%Y-%m-%d'))
    if pd.to_datetime(data['date'])< pd.to_datetime('1999-03-01'):
        print("less")
        data['date']='2009-03-01'
    return data


def get_data(data):

    start_date=str(data['date'])
    prev_2M_date = pd.to_datetime(start_date)+pd.DateOffset(months=-2)
    df_dict={'base':[],'date':[],'target':[]}
    
    retrieve_start_date=prev_2M_date
    retrieve_end_date=pd.to_datetime(start_date).date()
    flag=0

    ############################# Deprecated Logic ############################

    # # case where the cache is null ie accessing for the first time
    # if not cache.get('min_date1'):
    #     cache.set('min_date1',str(prev_2M_date.date()))
    # if not cache.get('max_date1'):
    #     cache.set('max_date1',str(start_date))
    #
    # # variable to hold the start and end dates to be retrieved from cache
    # start_cache_date=str(prev_2M_date.date())
    # end_cache_date=start_date
    # print("case--------------------------------------")
    # # case 1  : required min date is greater than the max cached date
    # if pd.to_datetime(prev_2M_date)> pd.to_datetime(str(cache.get('max_date1'), 'utf-8')):
    #     print("case1")
    #
    #     retrieve_start_date=str(prev_2M_date.date())
    #     retrieve_end_date=start_date
    #     cache.set('min_date1',str(prev_2M_date.date()))
    #     cache.set('max_date1',start_date)
    #     flag=1
    #
    # # case 2: required max date is greater than the min cached date
    # elif pd.to_datetime(start_date) < pd.to_datetime(str(cache.get('min_date1'), 'utf-8')):
    #     print("case2")
    #
    #     retrieve_start_date = start_date
    #     retrieve_end_date = str(prev_2M_date.date())
    #     cache.set('min_date1', str(prev_2M_date.date()))
    #     cache.set('max_date1', start_date)
    #     flag=1
    #
    # # case 3:required min date is greater than the min cached date but required max date is less than the cached max date
    # elif (pd.to_datetime(prev_2M_date)> pd.to_datetime(str(cache.get('min_date1'), 'utf-8'))) and not (pd.to_datetime(start_date) < pd.to_datetime(str(cache.get('max_date1'), 'utf-8'))):
    #     print("case3")
    #
    #     start_cache_date=str(pd.to_datetime(prev_2M_date).date())
    #     end_cache_date=cache.get('max_date1')
    #     retrieve_start_date=cache.get('max_date1')
    #     retrieve_end_date=start_date
    #     cache.set('max_date1',start_date)
    #     flag=1
    #
    # # case4 : required min date is less than the cached min date
    # elif pd.to_datetime(prev_2M_date) <= pd.to_datetime(str(cache.get('min_date1'), 'utf-8')) :
    #     print("case4")
    #     start_cache_date=cache.get('min_date1')
    #     end_cache_date=start_date
    #     retrieve_start_date=str(prev_2M_date.date())
    #     retrieve_end_date=cache.get('min_date1')
    #     cache.set('min_date1',str(prev_2M_date.date()))
    #     flag=1
    #
    # start_cache_date = str(start_cache_date, 'utf-8') if isinstance(start_cache_date, bytes) else start_cache_date
    # end_cache_date = str(end_cache_date, 'utf-8') if isinstance(end_cache_date, bytes) else end_cache_date
    #
    # print(start_cache_date,end_cache_date,retrieve_start_date,retrieve_end_date)
    #
    # # loop through the cache start date variable to cached end date variable
    # while pd.to_datetime(start_cache_date)!= pd.to_datetime(end_cache_date):
    #     if pd.to_datetime(start_cache_date).day_name() not in ['Saturday','Sunday']:
    #
    #         # Exsuring the data is in the cache , if not call the api
    #         print("cached date",start_cache_date)
    #         if cache.hgetall(start_cache_date):
    #             df_dict['base'].append(float(cache.hget(start_cache_date,data['base'])))
    #             df_dict['target'].append(float(cache.hget(start_cache_date,data['target'])))
    #             df_dict['date'].append(start_cache_date)
    #             start_cache_date=pd.to_datetime(start_cache_date).date()+pd.DateOffset(1)
    #             start_cache_date=str(start_cache_date.date())
    #             # x = str(x, 'utf-8') if isinstance(x, bytes) else str(x)
    #             # y = str(y, 'utf-8') if isinstance(y, bytes) else str(y)
    #         else:
    #             # If there is missing value in the cache ,break
    #             retrieve_start_date=start_cache_date
    #
    #             flag=1
    #             break
    #     else:
    #         start_cache_date = pd.to_datetime(start_cache_date).date() + pd.DateOffset(1)
    #         start_cache_date = str(start_cache_date.date())
    #
    # retrieve_start_date=str(retrieve_start_date,'utf-8') if isinstance(retrieve_start_date,bytes) else retrieve_start_date
    # retrieve_end_date=str(retrieve_end_date,'utf-8') if isinstance(retrieve_end_date,bytes) else retrieve_end_date
    # # cache.set('min_date1',str(cache.get('min_date1'),'utf-8')) if isinstance(cache.get('min_date1'),bytes) else 0
    # # cache.set('max_date1',str(cache.get('max_date1'),'utf-8')) if isinstance(cache.get('max_date1'),bytes) else 0

    # loop through the cache start date variable to cached end date variable

    # print(retrieve_star/t_date,retrieve_end_date)
    date_list=[]
    while retrieve_start_date.date()!= retrieve_end_date:
        if pd.to_datetime(str(retrieve_start_date)).day_name() not in ['Saturday','Sunday']:

            # Exsuring the data is in the cache , if not call the api
            start_cache_date=str(retrieve_start_date.date())
            # print(pd.to_datetime(str(retrieve_start_date)).day_name(),start_cache_date,cache.hget(start_cache_date,'USD'))
            if cache.hgetall(start_cache_date):
                df_dict['base'].append(float(cache.hget(start_cache_date,data['base'])))
                df_dict['target'].append(float(cache.hget(start_cache_date,data['target'])))
                df_dict['date'].append(start_cache_date)
                retrieve_start_date=retrieve_start_date+pd.DateOffset(1)

            else:
                # If there is missing value in the cache ,break
                date_list.append(str(retrieve_start_date.date()))
                retrieve_start_date = retrieve_start_date + pd.DateOffset(1)
                print(retrieve_start_date,"not present")
                flag=1

        else:
            retrieve_start_date = retrieve_start_date + pd.DateOffset(1)


    # if more data is to be retrieved
    if flag:
        url='https://api.exchangeratesapi.io/history?start_at={}&end_at={}'.format(min(date_list),max(date_list))
        print("request masd-------------------------------------------------",url)
        response=requests.get(url).json()['rates']

        for key,value in response.items():
            # retrieve the values and set it in the cache
            cache.hmset(str(key),value)
            cache.lpush('dates',key)
            df_dict['date'].append(str(key))
            df_dict['base'].append(value[data['base']])
            df_dict['target'].append(value[data['target']])
    df_dict=pd.DataFrame(df_dict)
    return df_dict


def train_model(dependent,independent):
    return train(dependent,independent)


def predict(logreg,data):
    waiting_dates=dict()
    forcast_dict=dict()
    
    # predict for all the dates starting for start date
    for wait_days in range(int(data['maxdays'])+1):
        considered_date=pd.Series(pd.to_datetime(data['req_date'])+pd.DateOffset(wait_days))
        forcast_dict['date']=considered_date.values

        #  Transform as required for input in the model
        transfored_data = predict_transform(forcast_dict)

        # Creating dummy values in the dataframe
        for days in ['Monday','Tuesday','Wednesday','Thursday','Friday']:
            if days not in transfored_data.columns:
                transfored_data[days]=0
        conversion=predict_values(logreg, transfored_data)
        
        #  Ignore the value if date comes out to be saturday or sunday
        if conversion== -1: 
            continue
        # update the dictionaries keys:dates values:amount
        waiting_dates[str(considered_date[0].date())]=predict_values(logreg, transfored_data)*int(data['amount'])

    return waiting_dates



