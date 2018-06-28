import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import dates
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.arima_model import ARMA 
import statsmodels.api as sm
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.linear_model import LinearRegression
import datetime
from pandas.tools.plotting import lag_plot
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf


df = pd.read_csv('/Users/dweiss89/ds/CLARITY_Export__Dan_2018-06-04_200249.csv')


df['Event Type'].value_counts
df = df[df['Event Type'] == 'EGV']
df.sort_values(by='Timestamp (YYYY-MM-DDThh:mm:ss)',inplace=True)
df['date'] = pd.to_datetime(df['Timestamp (YYYY-MM-DDThh:mm:ss)'])
df['Glucose Value (mg/dL)'] = np.where(df['Glucose Value (mg/dL)'] == 'Low',40,df['Glucose Value (mg/dL)'])
df['Glucose Value (mg/dL)'] = np.where(df['Glucose Value (mg/dL)'] == 'High',400,df['Glucose Value (mg/dL)'])

df['blood sugar'] = pd.to_numeric(df['Glucose Value (mg/dL)'])
df= df[~df['blood sugar'].isnull()]
plt.plot(df['date'],df['blood sugar'])
plt.xticks(rotation='vertical')

health = pd.read_csv('/Users/dweiss89/ds/Health Data.csv',parse_dates=['Start','Finish'])

df['blood sugar'].hist()
result = adfuller(df['blood sugar'],autolag='AIC')
print('ADF Statistic: %f' % result[0])
print('p-value: %f' % result[1])
print('Critical Values:')
for key, value in result[4].items():
	print('\t%s: %.3f' % (key, value))

plot_acf(df['blood sugar'], lags = 50)
plt.savefig('graphics/acf.png')
plot_pacf(df['blood sugar'], lags = 50)
plt.savefig('graphics/pacf.png')
plt.show()

df_weekday = df[df['date'].dt.dayofweek <5]
df_weekend = df[df['date'].dt.dayofweek>=5]
bins = np.arange(0,400,50)
plt.hist(df_weekday['blood sugar'],label='Weekday',bins= bins)
plt.hist(df_weekend['blood sugar'], label = 'Weekend', alpha=.5,bins= bins)
plt.legend()
plt.savefig('graphics/histogram.png')


# merge in health data
health['Steps'] = health['Steps (count)']
health['Flights'] = health['Flights Climbed (count)']
health = health[['Steps','Flights','Finish','Start']]
health = health[health['Start'] != health['Finish']]
health.drop_duplicates(inplace=True)
df['Hour'] = df['date'].dt.floor('H')
df_health = pd.merge(health[['Steps','Flights','Finish']],df[['Hour','date','blood sugar']],
                left_on='Finish',right_on='Hour',validate="1:m")

df_health['blood sugar'] = df_health['blood sugar'].astype(float)
def evaluate_ar_model(data,ar_term):
    for lag in range(1, ar_term + 1):
        data['lag_' + str(lag)] = data['blood sugar'].shift(lag)
    
    train_size = int(len(df_health) * 0.66)
    train, test = df_health[0:train_size], df_health[train_size-2:]

    y_train = train['blood sugar'].values
    X_train = train[['Steps','Flights']].values
    
    model = ARMA(y_train,order=(ar_term,0),exog=X_train)
    res = model.fit()
    const = np.mean(1 - res.arparams)
    test['y_hat'] = const + res.params[1]*test['Steps'] + res.params[2] * test['Flights']
    
    for i in range(1,ar_term + 1):
        test['y_hat'] += test['lag_' + str(i)] * res.params[2+i]

    
    
    return mean_squared_error(test['y_hat'],test['blood sugar'])**0.5
rmse_dict = {}
for i in range(1,10):
    rmse_dict[i] = evaluate_ar_model(df_health,i)

print(rmse_dict)

# 3 lag model produces best outcomes


# make chart showing actual blood sugar on one day. along with health data
hours = dates.HourLocator(interval=4)
minutes = dates.MinuteLocator(interval = 30)
hours_ = dates.DateFormatter('%H:%M')
day = datetime.date(2018,6,1)
oneday = df_health.loc[df_health['date'].dt.date == day]
oneday['time'] = oneday['date'].dt.time
plt.show()
fig = plt.figure()
plt.title('Blood Sugar and Step Count\n6/1/2018', fontsize=22)
ax1 = fig.add_subplot(111)
ax1.set_ylim(0,300)
ax1.plot_date(x=oneday.time, y=oneday['blood sugar'],color='blue', marker='o', label = "Blood Sugar")
ax1.set_ylabel('Blood Sugar (mg/dL)', fontsize=14)
ax1.set_xlabel('Time', fontsize=14)
ax1.axhline(y=80,color='black')
ax1.axhline(y=180,color='black')
ax2 = ax1.twinx()
ax2.plot_date(x=oneday.time, y=oneday['Steps'],color = 'orange', marker='x', label = 'Steps')
ax2.set_ylabel('Steps', fontsize=14)

lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(lines + lines2, labels + labels2, loc=0)
plt.tight_layout()
plt.savefig('Graphics/Historical Chart One Day.png')
# make chart showing actual vs. predicted blood sugar


train_size = int(len(df_health) * 0.66)
train, test = df_health[0:train_size], df_health[train_size-2:]

y_train = train['blood sugar'].values
X_train = train[['Steps','Flights']].values

model = ARMA(y_train,order=(3,0))
res = model.fit()
const = np.mean(1 - res.arparams)
test['y_hat'] = const 
for i in range(1,4):
    test['y_hat'] += test['lag_' + str(i)] * res.params[i]

oneday_pred = test.loc[test['date'].dt.date == day]
oneday_pred['time'] = oneday_pred['date'].dt.time
fig = plt.figure()
plt.title('Blood Sugar Actual and Forecast\n6/1/2018', fontsize=22)
ax1 = fig.add_subplot(111)
ax1.set_ylim(0,300)
ax1.plot_date(x=oneday_pred.time, y=oneday_pred['blood sugar'],color='blue', marker='o', label = "Actual Blood Sugar")
ax1.set_ylabel('Blood Sugar (mg/dL)', fontsize=14)
ax1.set_xlabel('Time', fontsize=14)
ax1.axhline(y=80,color='black')
ax1.axhline(y=180,color='black')
ax2 = ax1.twinx()
ax2.plot_date(x=oneday_pred.time, y=oneday_pred['y_hat'],color='green',alpha=0.5, marker='o', label = "Predicted Blood Sugar")
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(lines + lines2, labels + labels2, loc=0)
ax2.set_ylim(0,300)
plt.tight_layout()

plt.savefig('Graphics/Blood Sugar Actual Forecast.png')


# get rmse after throwing out times with lag greater than 15 min
test['diff'] = test['date'] - test['date'].shift(6)
rmse_data = test.loc[test['diff'] <= datetime.timedelta(minutes=45)]

print(mean_squared_error(rmse_data['y_hat'],rmse_data['blood sugar'])**0.5)
print(mean_absolute_error(rmse_data['y_hat'],rmse_data['blood sugar']))

lr = LinearRegression()
train['diff'] = train['date'] - train['date'].shift(6)
train2 = train.loc[train['diff'] <= datetime.timedelta(minutes=45)]
train2 = train2.loc[~train2['lag_5'].isnull()]
y = train2['blood sugar']
x = train2[['lag_3','lag_4','lag_5']]
rmse_data = rmse_data.loc[~rmse_data['lag_5'].isnull()]
x_test = rmse_data[['lag_3','lag_4','lag_5']]
y_test = rmse_data['blood sugar']
lr.fit(x,y)
lr.score(x_test,y_test)
print(mean_squared_error(lr.predict(x_test),y_test)**0.5)
print(mean_absolute_error(lr.predict(x_test),y_test))
print(lr.coef_)

rmse_data['y_hat'] = lr.predict(x_test)
plt.scatter(rmse_data['y_hat'],rmse_data['blood sugar'])
