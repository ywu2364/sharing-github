# -*- coding: utf-8 -*-
"""A2Q1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1V5-FID7fdliqJyH2SzBdDKtyPpMMPZv-
"""

!pip install scorecardpy

!gdown "https://drive.google.com/uc?id=1HAItdPa8TP-09OLSQ-Z5z3T_UbMp5mrt"
!unzip "Coursework 2 - Lending Club Data.zip"

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import scorecardpy as sc
import seaborn as sns
from numpy import cov
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression
import copy
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, confusion_matrix, roc_curve
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, make_scorer
from scipy.stats import zscore
# %matplotlib inline

LC_part = pd.read_csv('LCFinal.csv')

# remove loans that hadn't have enough time to default
LC_part = LC_part.loc[LC_part['loan_status'] != 'Current' ]
LC_part = LC_part.loc[LC_part['loan_status'] != 'In Grace Period' ]
LC_part = LC_part.loc[LC_part['loan_status'] != 'Late (16-30 days)' ]
LC_part = LC_part.loc[LC_part['loan_status'] != 'Late (31-120 days)' ]
LC_part = LC_part.loc[LC_part['loan_status'] != 'Default' ]
LC_part.loc[LC_part['loan_status'] == 'Fully Paid', 'loan_status'] = 0
LC_part.loc[LC_part['loan_status'] == 'Charged Off', 'loan_status'] = 1

# drop sparse columns
LC_part.drop(LC_part.iloc[:,129:142],axis=1,inplace=True) # too sparsed
LC_part.drop(LC_part.iloc[:,144:],axis=1,inplace=True) #too sparsed
LC_part = LC_part.drop(columns=['member_id','pymnt_plan','url',
                      'desc','annual_inc_joint','dti_joint',
                      'verification_status_joint','revol_bal_joint',
                      'sec_app_fico_range_low','sec_app_fico_range_high',
                      'sec_app_earliest_cr_line','sec_app_inq_last_6mths',
                      'sec_app_mort_acc','sec_app_open_acc',
                      'sec_app_revol_util','sec_app_open_act_il',
                      'sec_app_num_rev_accts','sec_app_chargeoff_within_12_mths',
                      'sec_app_collections_12_mths_ex_med','sec_app_mths_since_last_major_derog',
                      'hardship_type','hardship_reason',
                      'hardship_status', 'debt_settlement_flag_date',
                      'settlement_status', 'settlement_date',
                      'settlement_amount', 'settlement_percentage',
                      'settlement_term', 'next_pymnt_d',
                      'mths_since_recent_revol_delinq', 'mths_since_recent_inq',
                      'mths_since_recent_bc_dlq', 'issue_d'])

# replace missing value with median if the median value only accounts for less than 5%
mths_since_last_delinq_median = np.nanmedian(LC_part["mths_since_last_delinq"])
LC_part['mths_since_last_delinq'].fillna(value=mths_since_last_delinq_median, inplace=True)

mths_since_last_record_median = np.nanmedian(LC_part["mths_since_last_record"])
LC_part['mths_since_last_record'].fillna(value=mths_since_last_record_median, inplace=True)

mths_since_recent_bc_median = np.nanmedian(LC_part["mths_since_recent_bc"])
LC_part['mths_since_recent_bc'].fillna(value=mths_since_recent_bc_median, inplace=True)

il_util_median = np.nanmedian(LC_part["il_util"])
LC_part['il_util'].fillna(value=il_util_median, inplace=True)


mo_sin_old_il_acct_median = np.nanmedian(LC_part["mo_sin_old_il_acct"])
LC_part['mo_sin_old_il_acct'].fillna(value=mo_sin_old_il_acct_median, inplace=True)

num_tl_120dpd_2m_median = np.nanmedian(LC_part["num_tl_120dpd_2m"])
LC_part['num_tl_120dpd_2m'].fillna(value=num_tl_120dpd_2m_median, inplace=True)

percent_bc_gt_75_median = np.nanmedian(LC_part["percent_bc_gt_75"])
LC_part['percent_bc_gt_75'].fillna(value=percent_bc_gt_75_median, inplace=True)

LC_part['emp_title'] = LC_part.emp_title.astype("category").cat.codes

# mths_since_last_major_derog (too sparsed)
LC_part = LC_part.drop(columns=["mths_since_last_major_derog"])

#term
#LC_part['term'] = LC_part.term.astype("category").cat.codes

#emp_length
#LC_part.emp_length = LC_part.emp_length.astype("category").cat.codes
LC_part.loc[LC_part['emp_length'] == '< 1 year', 'emp_length'] = 1
LC_part.loc[LC_part['emp_length'] == '1 year', 'emp_length'] = 2
LC_part.loc[LC_part['emp_length'] == '2 years', 'emp_length'] = 3
LC_part.loc[LC_part['emp_length'] == '3 years', 'emp_length'] = 4
LC_part.loc[LC_part['emp_length'] == '4 years', 'emp_length'] = 5
LC_part.loc[LC_part['emp_length'] == '5 years', 'emp_length'] = 6
LC_part.loc[LC_part['emp_length'] == '6 years', 'emp_length'] = 7
LC_part.loc[LC_part['emp_length'] == '7 years', 'emp_length'] = 8
LC_part.loc[LC_part['emp_length'] == '8 years', 'emp_length'] = 9
LC_part.loc[LC_part['emp_length'] == '9 years', 'emp_length'] = 10
LC_part.loc[LC_part['emp_length'] == '10+ years', 'emp_length'] = 11

#home_ownership (three levels)

#issue_d (number of levels is small)

# loan_status
#LC_part.loan_status = LC_part.loan_status.astype("category").cat.codes

# purpose
LC_part.purpose = LC_part.purpose.astype("category").cat.codes

# title
#LC_part.title = LC_part.title.astype("category").cat.codes

# zip_code
LC_part.zip_code = LC_part.zip_code.str[:1]

# addr_state
LC_part.addr_state = LC_part.addr_state.astype("category").cat.codes

# earliest_cr_line (only accounts for years)
LC_part.earliest_cr_line = LC_part.earliest_cr_line.str[4:]

# initial_list_status (two levels)
#LC_part.initial_list_status = LC_part.initial_list_status.astype("category").cat.codes



LC_part = LC_part.dropna()
LC_part['loan_status'] = LC_part['loan_status'].astype('int')

# Drop columns by expert judgement
LC_pd = LC_part[['loan_amnt','funded_amnt_inv','home_ownership','annual_inc',
                 'loan_status','purpose','title','dti','delinq_2yrs','term',
                 'earliest_cr_line','fico_range_high','inq_last_6mths','mths_since_last_delinq',
                 'mths_since_last_record','open_acc','pub_rec','revol_bal','revol_util','total_acc',
                 'out_prncp','out_prncp_inv','application_type','int_rate',
                 'total_pymnt','total_rec_prncp','zip_code','emp_title',
                 'recoveries','last_pymnt_amnt','collections_12_mths_ex_med',
                 'acc_now_delinq','tot_coll_amt','open_act_il','open_il_24m',
                 'il_util','open_rv_12m','max_bal_bc','total_rev_hi_lim','inq_fi',
                 'total_cu_tl','inq_last_12m','avg_cur_bal','bc_util',
                 'mo_sin_old_il_acct','mort_acc','num_sats','pct_tl_nvr_dlq','total_bal_ex_mort']]

sns.pairplot(LC.iloc[:,:5], diag_kind="kde")

sns.pairplot(LC.iloc[:,5:11], diag_kind="kde")

sns.pairplot(LC.iloc[:,11:21], diag_kind="kde")

LC_pd.drop(columns=['funded_amnt_inv','open_acc','out_prncp_inv',
                    'il_util','inq_fi','total_bal_ex_mort','total_rev_hi_lim',
                    'mo_sin_old_il_acct', 'title'], inplace=True)
LC_pd.drop(columns=['out_prncp','total_rec_prncp','pct_tl_nvr_dlq','max_bal_bc'],inplace=True)

# check outliers
sns.distplot(LC['loan_amnt'])

sns.distplot(LC_pd['annual_inc'])

sns.distplot(LC['int_rate'])

sns.distplot(LC['dti'])
sns.distplot(LC['mths_since_last_delinq'])
sns.distplot(LC['mths_since_last_record'])
sns.distplot(LC['avg_cur_bal'])

# find interquantiles for annual_inc
    annual_inc_q1 = np.percentile(LC_pd.annual_inc,25,interpolation='midpoint')
    annual_inc_q2 = np.percentile(LC_pd.annual_inc,75,interpolation='midpoint')
    IQR_annual_inc = annual_inc_q2 - annual_inc_q1
    # strim
    lower_annual_inc = np.median(LC_pd.annual_inc)-3*IQR_annual_inc
    upper_annual_inc = np.median(LC_pd.annual_inc)+3*IQR_annual_inc
    LC_pd = LC_pd.loc[(LC_pd['annual_inc'] >= lower_annual_inc) &
                      (LC_pd['annual_inc'] <= upper_annual_inc)]
    

    # find interquantiles for mths_since_last_delinq
    mths_since_last_delinq_q1 = np.percentile(LC_pd.mths_since_last_delinq,25,interpolation='midpoint')
    mths_since_last_delinq_q2 = np.percentile(LC_pd.mths_since_last_delinq,75,interpolation='midpoint')
    IQR_mths_since_last_delinq = mths_since_last_delinq_q2 - mths_since_last_delinq_q1
    # strim
    lower_mths_since_last_delinq = np.median(LC_pd.mths_since_last_delinq)-3*IQR_mths_since_last_delinq
    upper_mths_since_last_delinq = np.median(LC_pd.mths_since_last_delinq)+3*IQR_mths_since_last_delinq
    LC_pd = LC_pd.loc[(LC_pd['mths_since_last_delinq'] >= lower_mths_since_last_delinq) &
                      (LC_pd['mths_since_last_delinq'] <= upper_mths_since_last_delinq)]
    
    # find interquantiles for mths_since_last_record
    mths_since_last_record_q1 = np.percentile(LC_pd.mths_since_last_record,25,interpolation='midpoint')
    mths_since_last_record_q2 = np.percentile(LC_pd.mths_since_last_record,75,interpolation='midpoint')
    IQR_mths_since_last_record = mths_since_last_record_q2 - mths_since_last_record_q1
    # strim
    lower_mths_since_last_record = np.median(LC_pd.mths_since_last_record)-3*IQR_mths_since_last_record
    upper_mths_since_last_record = np.median(LC_pd.mths_since_last_record)+3*IQR_mths_since_last_record
    LC_pd = LC_pd.loc[(LC_pd['mths_since_last_record'] >= lower_mths_since_last_record) &
                      (LC_pd['mths_since_last_record'] <= upper_mths_since_last_record)]
    
    # find interquantiles for avg_cur_bal
    avg_cur_bal_q1 = np.percentile(LC_pd.avg_cur_bal,25,interpolation='midpoint')
    avg_cur_bal_q2 = np.percentile(LC_pd.avg_cur_bal,75,interpolation='midpoint')
    IQR_avg_cur_bal = avg_cur_bal_q2 - avg_cur_bal_q1
    # strim
    lower_avg_cur_bal = np.median(LC_pd.avg_cur_bal)-3*IQR_avg_cur_bal
    upper_avg_cur_bal = np.median(LC_pd.avg_cur_bal)+3*IQR_avg_cur_bal
    LC_pd = LC_pd.loc[(LC_pd['avg_cur_bal'] >= lower_avg_cur_bal) &
                      (LC_pd['avg_cur_bal'] <= upper_avg_cur_bal)]


# find interquantile for int_rate
int_rate_q1 = np.percentile(LC_pd.int_rate,25,interpolation='midpoint')
int_rate_q2 = np.percentile(LC_pd.int_rate,75,interpolation='midpoint')
IQR_int_rate = int_rate_q2 - int_rate_q1
# strim
lower_int_rate = np.median(LC_pd.int_rate)-3*IQR_int_rate
upper_int_rate = np.median(LC_pd.int_rate)+3*IQR_int_rate
LC_pd = LC_pd.loc[(LC_pd['int_rate'] >= lower_int_rate) &
                      (LC_pd['int_rate'] <= upper_int_rate)]

"""Data cleaning for LGD model"""

LC = LC_part
LC_afterfilter = LC[['loan_amnt','funded_amnt_inv','home_ownership','annual_inc',
                 'loan_status','purpose','title','dti','delinq_2yrs', 'emp_length',
                 'earliest_cr_line','fico_range_low','fico_range_high','inq_last_6mths','mths_since_last_delinq',
                 'mths_since_last_record','open_acc','pub_rec','revol_bal','revol_util','total_acc',
                 'out_prncp','out_prncp_inv','application_type', 'int_rate',
                 'total_pymnt','total_rec_prncp','zip_code','emp_title',
                 'recoveries','last_pymnt_amnt','collections_12_mths_ex_med',
                 'acc_now_delinq','tot_coll_amt','open_act_il','open_il_24m',
                 'il_util','open_rv_12m','max_bal_bc','total_rev_hi_lim','inq_fi',
                 'total_cu_tl','inq_last_12m','avg_cur_bal','bc_util', 'total_rec_late_fee',
                 'mo_sin_old_il_acct','mort_acc','num_sats','pct_tl_nvr_dlq','total_bal_ex_mort']]

LC_lgd = LC_afterfilter.loc[LC_part['loan_status'] == 1]

# calculate LGD 
LC_lgd['LGD'] = (LC_lgd.loan_amnt-LC_lgd.total_pymnt-LC_lgd.recoveries-LC_lgd.total_rec_late_fee)/(
        LC_lgd.loan_amnt-LC_lgd.total_pymnt)

LC_lgd.loc[LC_lgd['LGD'] > 1,'LGD'] = 1 
LC_lgd.drop(columns=['funded_amnt_inv','open_acc','out_prncp_inv',
                    'il_util','inq_fi','total_bal_ex_mort','total_rev_hi_lim',
                    'mo_sin_old_il_acct', 'title', 'loan_status','fico_range_low'], inplace=True)
LC_lgd.drop(columns=['out_prncp','total_rec_prncp','pct_tl_nvr_dlq','max_bal_bc'],inplace=True)
LC_lgd.dropna(axis=0,inplace=True)


# outliers
LC_lgd = LC_lgd.loc[(LC_lgd['annual_inc'] >= lower_annual_inc) &
                      (LC_lgd['annual_inc'] <= upper_annual_inc)]
    

LC_lgd = LC_lgd.loc[(LC_lgd['mths_since_last_delinq'] >= lower_mths_since_last_delinq) &
                      (LC_lgd['mths_since_last_delinq'] <= upper_mths_since_last_delinq)]
    
    
LC_lgd = LC_lgd.loc[(LC_lgd['mths_since_last_record'] >= lower_mths_since_last_record) &
                      (LC_lgd['mths_since_last_record'] <= upper_mths_since_last_record)]
    

LC_lgd = LC_lgd.loc[(LC_lgd['avg_cur_bal'] >= lower_avg_cur_bal) &
                      (LC_lgd['avg_cur_bal'] <= upper_avg_cur_bal)]


LC_lgd = LC_lgd.loc[(LC_lgd['int_rate'] >= lower_int_rate) &
                      (LC_lgd['int_rate'] <= upper_int_rate)]

# select all numeric columns
numeric_cols = LC_lgd.select_dtypes(include=[np.number]).columns
numeric_cols = numeric_cols[:-1]

#apply the zscore function to all data
LC_lgd[numeric_cols] = LC_lgd[numeric_cols].apply(zscore)

LC_lgd_temp = copy.copy(LC_lgd)
LC_lgd.loc[LC_lgd_temp['earliest_cr_line'].astype(int) < 1990, 'earliest_cr_line'] = 'early'
LC_lgd.loc[LC_lgd_temp['earliest_cr_line'].astype(int) >= 1990, 'earliest_cr_line'] = 'late' 

LC_lgd.loc[(LC_lgd_temp['zip_code'].astype(int) < 3) | (LC_lgd_temp['zip_code'].astype(int) == 4) |
        ((LC_lgd_temp['zip_code'].astype(int) >= 6) & (LC_lgd_temp['zip_code'].astype(int) <= 8)), 'zip_code'] = 'zip_mid'
LC_lgd.loc[(LC_lgd_temp['zip_code'].astype(int) == 5), 'zip_code'] = 'zip_low'
LC_lgd.loc[(LC_lgd_temp['zip_code'].astype(int) == 3) | (LC_lgd_temp['zip_code'].astype(int) == 9), 'zip_code'] = 'zip_high'

LC_lgd.loc[LC_lgd_temp['emp_length'] <= 7, 'emp_length'] = 'emp_length_mid'
LC_lgd.loc[(LC_lgd_temp['emp_length'] > 7) & (LC_lgd_temp['emp_length'] <= 10), 'emp_length'] = 'emp_length_low'
LC_lgd.loc[LC_lgd_temp['emp_length'] == 11, 'emp_length'] = 'emp_length_hi'

# dummy_variable
LC_lgd = pd.get_dummies(LC_lgd)
LC_lgd.describe()

