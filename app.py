
# Libraries
import streamlit as st
import time

import pandas as pd 
import numpy as np

import matplotlib.pyplot as plt

from scipy.stats import chi2_contingency, f_oneway
from statsmodels.stats.outliers_influence import variance_inflation_factor

from cleaning import removing_cols, merging_both_df

# ================================================================================================
st.set_page_config(layout='wide')
st.title("Credit Assesment Modeling")

def spinner(text):
	st.text(text)
	return st.spinner(text)

def clean_df(case1, case2):
	# merging both case1 and case2 on PROSPECTID feature
	with spinner("merging frames..."):
		case = merging_both_df(case1, case2, on='PROSPECTID')

	# removing, lowercasing, dropping na's
	with spinner("cleaning..."):
		case = (
	        case
	        .drop(columns=removing_cols(case))
	        .rename(columns=lambda df_ : df_.lower())
	        .set_index("prospectid")
	        .replace(-99999, np.nan)
	        .dropna()

	        .assign(
	            education=lambda df_: (
	                df_.education.replace({
	                    "UNDER GRADUATE" : "UG",
	                    "POST-GRADUATE" : "PG",
	                    "PROFESSIONAL" : "PRO"
	                })
	            )
	        )
	    )


	with spinner("vif calculating..."):
	# differ numerical cols and categorical cals
		categorical_cols = case.describe(include='O').columns
		numerical_cols = case.describe(include='number').columns

		# Variance Inflation Factor
		vif_data = case[numerical_cols]
		columns_to_be_kept = []
		column_index = 0

		for i in range(0, vif_data.shape[1]):
		    vif_value = variance_inflation_factor(vif_data, column_index)
		    # print(column_index, "----", vif_value)

		    if vif_value <= 6:
		        columns_to_be_kept.append(numerical_cols[i])
		        column_index += 1
		        continue

		    vif_data = vif_data.drop([numerical_cols[i]], axis=1)

	with spinner("anova calculating..."):
		# ANOVA
		columns_to_be_kept_anova = []

		for i in columns_to_be_kept:
			a = case[i].to_list()
			b = case['approved_flag'].to_list()

			grp_P1 = [value for value, group in zip(a, b) if group == 'P1']
			grp_P2 = [value for value, group in zip(a, b) if group == 'P2']
			grp_P3 = [value for value, group in zip(a, b) if group == 'P3']
			grp_P4 = [value for value, group in zip(a, b) if group == 'P4']

			f_statistic, p_value = f_oneway(grp_P1, grp_P2, grp_P3, grp_P4)

			if p_value <= 0.05:
			    columns_to_be_kept_anova.append(i)

	return (
	    pd
	    .merge(
	        case[columns_to_be_kept_anova],
	        case[categorical_cols],
	        how='inner',
	        on='prospectid'
	    )
	)

def home():
	if 'case' in st.session_state:
		st.text("Current Selected DataFrame")
		st.dataframe(st.session_state['case'])
		return

	col1, col2 = st.columns(2)

	with col1:
		case1 = st.file_uploader("Put Dataframe 1", key="case1")
	with col2:
		case2 = st.file_uploader("Put Dataframe 2", key="case2")

	submit = st.button("Submit")

	if submit and case1 and case2:

		with spinner("reading data..."):
			case1 = pd.read_excel(case1)
			case2 = pd.read_excel(case2)

		case = clean_df(case1, case2)

		# creating session
		st.session_state['case'] = case

		st.dataframe(case)

	elif submit:
		st.text("Both Input Expected")

def plotting(df, columns=[], number=None):
	rows = len(columns) // 3
	cols = 3

	# plotting
	fig, axes = plt.subplots(rows, cols, figsize=(12,7))
	fig.tight_layout(pad=10)
	index = 0

	if number==True:
		pass

	if number==False:
		# plotting
		for ax in axes:
		    for a in ax:
		        bar = df[columns].iloc[:,index].value_counts().reset_index()
		        a.set_title(columns[index])
		        a.bar(x=bar.iloc[:,0], height=bar.iloc[:,1])
		        a.tick_params(axis='x', labelrotation=90)
		        index += 1

	return fig


def edi():
	if 'case' not in st.session_state:
		st.text("Select DataFrame from /home page")
		return

	st.text("Current Selected DataFrame")
	case = st.session_state['case']

	col1, col2 = st.columns(2)
	with col1:
		slice = st.selectbox("Slice", options=['Only Numericals', 'Only Categorical'])
	with col2:
		pass

	current = None
	if slice == "Only Numericals":
		numerical_cols = case.describe(include='number').columns
		case[numerical_cols]
		current = numerical_cols

	if slice == "Only Categorical":
		categorical_cols = case.describe(include='O').columns
		case[categorical_cols]
		current = categorical_cols

	if st.button("submit"):
		st.pyplot(plotting(case, columns=current, number=False))


# main =============================================================================================

pages = ['Home', 'EDI', 'Models']
page = st.sidebar.radio("/pages",options=pages)
if page == "Home":
	home()

if page == 'EDI':
	edi()