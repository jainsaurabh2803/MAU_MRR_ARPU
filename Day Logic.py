import pandas as pd
import numpy as np
import calendar
from datetime import timedelta, date
import datetime
import os, sys
from os import name
from dateutil import relativedelta

tabel1 = pd.read_sql("Day wise logic dumy data.csv")

customers=df.id.unique()
customers = customers.tolist()
plan_type = ['Standard','Basic','Premium']
plan_period = ['quarterly','yearly']

# df.fillna(report_end_date, inplace=True)
df['plan_start_date'] =pd.to_datetime(df['plan_start_date'], format = '%Y-%m-%d').dt.date
df['next_start'] =pd.to_datetime(df['next_start'], format = '%Y-%m-%d').dt.date

report_start_date = date(2021,1,1)
date = date.today()
d = date.replace(day = calendar.monthrange(date.year, date.month)[1])  + relativedelta.relativedelta(months=1)
report_end_date = d
print(report_end_date)

def daterange(calculation_start_date, calculation_end_date):
    for n in range(int((calculation_end_date-calculation_start_date).days)+1):
        yield calculation_start_date + timedelta(n)
        
daily_mrr=[]
for my_date in daterange(report_start_date, report_end_date):	
    for s in customers:
        my_date_df=df[(df['start_date']<=my_date) & (df['end_date1']>=my_date) & (df['store_id']==s)]
        tmrc=my_date_df['daily_price'].sum()
        daily_mrr.append({'date':my_date, 'store_id':s, 'daily_mrr':tmrc})        

        
      
mrr_adf=pd.DataFrame(daily_mrr)
mrr_adf["date"] = pd.to_datetime(mrr_adf["date"])
mrr_adf["month"] = mrr_adf['date'].dt.to_period('M').dt.to_timestamp()
mrr_adf = mrr_adf.replace(0, np.NaN)
mrr_rank_adf = mrr_adf[mrr_adf['daily_mrr']>0].reset_index(drop=True)
mrr_rank_adf['RN'] = mrr_rank_adf.sort_values(['date'], ascending=[False]) \
             .groupby(['id','month']) \
             .cumcount() + 1
mrr_rank_adf = mrr_rank_adf[mrr_rank_adf['RN']==1]

mrr_rank_adf = mrr_rank_adf[['month','daily_mrr','id']].reset_index(drop=True)

mrr_rank_adf.rename(columns = {'daily_mrr':'last_day_mrr'}, inplace = True)
mrr_adf = pd.merge(mrr_adf, mrr_rank_adf,  how='left', left_on=['month','id'], right_on = ['month','id'])

agg_df =  mrr_adf.groupby(["month","id"]).agg(daily_avg=('daily_mrr', np.nanmean), mrr=('daily_mrr', np.nansum), last_day_mrr=('last_day_mrr', np.nanmax))

agg_df=agg_df.sort_values(by=["id","month"])

agg_df['prev_avg']=agg_df.groupby(['id'])['daily_avg'].shift(1)
agg_df['last_month_last_day_mrr']=agg_df.groupby(['id'])['last_day_mrr'].shift(1)

agg_df.reset_index(drop=False, inplace=True)
new_df = agg_df
new_df['prev_mrr']=new_df.groupby(['store_id'])['mrr'].shift(1)

new_df.insert(7,"refereshed_at",datetime.datetime.now())
new_df.insert(8,"start_at",session_start_time)

hourly_data_df  = new_df

hourly_data_df['month']=pd.to_datetime(hourly_data_df['month'].astype(str), format='%Y-%m-%d')

customers=hourly_data_df.store_id.unique()
distinct_customers = customers.tolist()
listTocus = ','.join([str(elem) for elem in distinct_customers])

test_df = hourly_data_df[['id','month','plan_id','plan_period']].drop_duplicates()
test_df['prev_plan']  = test_df.groupby(['id'])['plan_id'].shift(1)
test_df['prev_priod']  = test_df.groupby(['id'])['plan_period'].shift(1)
test_df.rename(columns = {'plan_id':'current_month_plan_id', 'plan_period':'current_month_plan_period'}, inplace = True)

months=pd.to_datetime(hourly_data_df['month'].astype(str), format='%Y-%m-%d').drop_duplicates()
months = months.tolist()
final_df = pd.DataFrame(list(product(id,months,plan_type,plan_period)), columns=['id','month','plan_id','plan_period'])

hourly_data_df = pd.merge(final_df, hourly_data_df,  how='left', left_on=['id','month','plan_id','plan_period'], right_on = ['id','month','plan_id','plan_period'])

hourly_data_df1 = hourly_data_df[['id','mrr','month']]
agg_df= hourly_data_df1[hourly_data_df1['mrr']>0].copy()
agg_df['first_month'] = agg_df.groupby(['store_id'])['month'].transform('first')
agg_df = agg_df.drop(['mrr','month'], axis=1)
agg_df = agg_df.drop_duplicates()
hourly_data_df2=pd.merge(hourly_data_df,agg_df, on='id', how='left')
hourly_data_df2 = pd.merge(hourly_data_df2,test_df , how='left', left_on=['id','month'], right_on = ['id','month'])
hourly_data_df2.fillna(0,inplace=True)
hourly_data_df2

def mrr_tag(row):
    
    if((row['month']==row['first_month']) and round(row['last_day_mrr']) >0):
        tag='new'
        
    elif((row['prev_plan']==row['current_month_plan_id']) and (row['prev_priod']==row['current_month_plan_period']) and round(row['last_day_mrr'])>0):
        tag='retained'
        
    elif(row['plan_id']!=0 and row['prev_plan']==0 and (row['month']!=row['first_month']) and round(row['last_day_mrr']) >0):
        tag='reactivated'
        
    elif((row['plan_id']==row['prev_plan']) and (row['plan_period']==row['prev_priod']) and row['current_month_plan_id']==0 and round(row['last_day_mrr']) == 0   ):
        tag='churned'

    elif( (row['plan_id']==row['prev_plan']) and (row['plan_period']!=row['prev_priod']) and (row['prev_plan']==row['current_month_plan_id']) and (row['prev_priod']!=row['current_month_plan_period']) and round(row['last_day_mrr']) >0 ):
        tag='migrated_within_same_plan'        

    elif( (row['plan_id']==row['prev_plan']) and (row['plan_period']==row['prev_priod']) and round(row['last_day_mrr'])==0 ):
        tag='migrated_out'          

    elif( (row['plan_id']!=row['prev_plan']) and (row['current_month_plan_id']==row['plan_id']) and row['last_day_mrr']>0 and row['prev_plan']=='Lite' and  row['plan_id']=='Premium'):
        tag='expansion'         

    elif( (row['plan_id']!=row['prev_plan']) and (row['current_month_plan_id']==row['plan_id']) and row['last_day_mrr']>0 and row['prev_plan']=='Lite' and  row['plan_id']=='Platinum'):
        tag='expansion'                 

    elif( (row['plan_id']!=row['prev_plan']) and (row['current_month_plan_id']==row['plan_id']) and row['last_day_mrr']>0 and row['prev_plan']=='Premium' and  row['plan_id']=='Platinum'):
        tag='expansion'  

    elif( (row['plan_id']!=row['prev_plan']) and (row['current_month_plan_id']==row['plan_id']) and row['last_day_mrr']>0 and row['prev_plan']=='Platinum' and  row['plan_id']=='Premium'):
        tag='contraction'       

    elif( (row['plan_id']!=row['prev_plan']) and (row['current_month_plan_id']==row['plan_id']) and row['last_day_mrr']>0 and row['prev_plan']=='Platinum' and  row['plan_id']=='Lite'):
        tag='contraction'  

    elif( (row['plan_id']!=row['prev_plan']) and (row['current_month_plan_id']==row['plan_id']) and row['last_day_mrr']>0 and row['prev_plan']=='Premium' and  row['plan_id']=='Lite'):
        tag='contraction'         
                          
    else:
        tag='undefined'
    return 

  
hourly_data_df2['mrr_tag'] = hourly_data_df2.apply(mrr_tag,axis=1)
hourly_data_df2 = hourly_data_df2[hourly_data_df2['mrr_tag']!='undefined']


