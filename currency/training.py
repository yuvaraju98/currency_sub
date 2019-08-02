
import pandas as pd
from sklearn.linear_model import LinearRegression

def train(x,y):
    logreg = LinearRegression()
    logreg.fit(x, y)
    return logreg


def transform(values):
    x_train = {'day': [], 'month': [], 'dayname': [],'base':[]}
    x_result = list()
    for x, y in values.T.iteritems():
        x_train['day'].append(pd.to_datetime(y['date']).day)
        x_train['month'].append(pd.to_datetime(y['date']).month)
        x_train['dayname'].append(pd.to_datetime(y['date']).day_name())
        x_result.append(y['target']/y['base'])
    df = pd.DataFrame(pd.get_dummies(x_train['dayname']))
    df['day'] = x_train['day']
    df['month'] = x_train['month']
    return df,x_result


def predict_transform(values):
    df = pd.DataFrame(pd.get_dummies(pd.to_datetime(values['date']).day_name()))
    df['day'] = pd.to_datetime(values['date']).day
    df['month'] = pd.to_datetime(values['date']).month
    return df


def predict_values(logreg,p):
    if 'Saturday' not in p.columns and 'Sunday' not in p.columns:
        res=logreg.predict(p)
        return float(res[0])
    else:
        return -1
