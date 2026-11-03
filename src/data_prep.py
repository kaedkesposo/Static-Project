import pandas as pd
import geopandas as gpd
import numpy as np
import altair as alt

def cols_re(prefix, df):
    """
    Add a prefix to every column name except the first.

    Args:
        prefix: Text to place before each column name, followed by a colon.
        df: DataFrame whose columns will be renamed.

    Returns:
        A new DataFrame with renamed columns and the first column unchanged.
    """
    rename_dict = {col: f"{prefix}: {col}" for col in df.columns[1:]}
    df = df.rename(columns=rename_dict)
    return df

def load_clean_five_essentials():
    """
    Load, prefix, and merge the five 5Essentials datasets.

    Calculate the average of the five 2024 essential scores and categorize
    averages into 20-point intervals.

    Returns:
        A DataFrame containing the five merged 5Essentials datasets.
    """
    ai = cols_re('AI', pd.read_csv('../data/5Essentials/Ambitious Instruction.csv'))
    ct = cols_re('CT', pd.read_csv('../data/5Essentials/Collaborative Teachers.csv'))
    el = cols_re('EL', pd.read_csv('../data/5Essentials/Effective Leaders.csv'))
    invf = cols_re('IF', pd.read_csv('../data/5Essentials/Involved Families.csv'))
    se = cols_re('SE', pd.read_csv('../data/5Essentials/Supportive Environment.csv'))

    fiveE = ai.merge(ct).merge(el).merge(invf).merge(se)

    fiveE['2024 Avg Score'] = (fiveE['AI: 2024 Score'] + 
                           fiveE['CT: 2024 Score'] + 
                           fiveE['EL: 2024 Score'] + 
                           fiveE['IF: 2024 Score'] +
                           fiveE['SE: 2024 Score']) /5

    bins = np.arange(0, 121, 20) 
    labels = [f"{bins[i]} to <{bins[i+1]}" for i in range(len(bins)-1)]

    fiveE['2024 Avg Label'] = pd.cut(fiveE['2024 Avg Score'], bins=bins, labels=labels, right=False)

    return fiveE

def load_clean_enrollment():
    """
    Load and merge annual school enrollment data from 2020 through 2024.

    Drop rows with missing values in each source dataset, retain school IDs
    and enrollment totals, and prefix total columns by year. Convert school
    IDs to integers and retain only schools present in all five datasets.

    Returns:
        A DataFrame containing school IDs and annual enrollment totals.
    """
    enroll_2020 = cols_re('2020',pd.read_csv('../data/demographics/demographics_2020.csv').dropna()[['School ID','Total']])
    enroll_2021 = cols_re('2021', pd.read_csv('../data/demographics/demographics_2021.csv').dropna()[['School ID','Total']])
    enroll_2022 = cols_re('2022', pd.read_csv('../data/demographics/demographics_2022.csv').dropna()[['School ID','Total']])
    enroll_2023 = cols_re('2023', pd.read_csv('../data/demographics/demographics_2023.csv').dropna()[['School ID','Total']])
    enroll_2024 = cols_re('2024', pd.read_csv('../data/demographics/demographics_2024.csv').dropna()[['School ID','Total']])

    for d in [enroll_2020, enroll_2021, enroll_2022, enroll_2023, enroll_2024]:
        d.dropna(subset=['School ID'], inplace=True)
        d['School ID'] = d['School ID'].astype(int)

    enroll = enroll_2020.merge(
        enroll_2021, on = 'School ID'
    ).merge(
        enroll_2022,on='School ID'
    ).merge(
        enroll_2023,on='School ID'
    ).merge(
        enroll_2024,on='School ID'
    )

    return enroll

def calculate_enrollment_change():
    """
    Calculate enrollment percentage changes and classify school trends.

    Convert enrollment totals to numeric values and calculate four annual
    percentage changes plus the overall change from 2020 to 2024. Classify
    schools as consistently declining or growing if at least three annual
    changes follow that direction; otherwise, classify them as mixed.

    Returns:
        A DataFrame containing enrollment totals, annual and overall
        percentage changes, and enrollment trend categories.
    """
    enroll = load_clean_enrollment()

    years = ['2020','2021','2022','2023','2024']
    for yr in years:
        enroll[f'{yr} Total'] = pd.to_numeric(
            enroll[f'{yr}: Total'].astype(str).str.replace(',', ''), errors='coerce'
        )

    for prev, curr in zip(years[:-1], years[1:]):
        enroll[f'chg_{curr}'] = (enroll[f'{curr} Total'] - enroll[f'{prev} Total']) / enroll[f'{prev} Total'] * 100

    enroll['total_chg'] = (enroll['2024 Total'] - enroll['2020 Total']) / enroll['2020 Total'] * 100

    chg_cols = ['chg_2021', 'chg_2022', 'chg_2023', 'chg_2024']

    n_down = (enroll[chg_cols] < 0).sum(axis=1)
    n_up = (enroll[chg_cols] > 0).sum(axis=1)

    enroll['Trend'] = np.select(
        [n_down >= 3, n_up >= 3],
        ['Consistent decline', 'Consistent growth'],
        default='Mixed',
    )

    return enroll
    

def load_clean_demographics():
    """
    Load school demographics and create majority-group indicators.

    Remove entirely empty rows, convert school IDs to integers, and convert
    English learner, IEP, and low-income percentages to numeric values on
    a 0–100 scale. Create indicators equal to 1 when the corresponding
    percentage exceeds 50 and 0 otherwise.

    Returns:
        A DataFrame containing demographic data and majority indicators.
    """
    
    demographics = pd.read_csv('../data/2026-27-demographics-lep-iep-low-income-20th-day-report (1).csv')
    demographics = demographics.dropna(how="all")
    demographics["School ID"] = demographics["School ID"].astype(int)

    majority_columns = {
        "State English Learners %": "EL majority",
        "Students with IEPs %": "IEP majority",
        "Low Income %": "LI majority",
    }

    for percent_column, majority_column in majority_columns.items():
        demographics[percent_column] = (
            demographics[percent_column]
            .str.rstrip("%")
            .astype(float)
        )
        demographics[majority_column] = (
            demographics[percent_column] > 50
        ).astype(int)

    return demographics

def load_clean_api():
    api = pd.read_csv('../data/API_StudentGrowth_SY2024_Present.csv')

    api = api[(api['Student Group'] == 'All Students')]

    api[" Student Count "] = (
        api[" Student Count "]
        .str.replace(",", "", regex=False)
        .astype(int)
    )

    api["School Code"] = pd.to_numeric(api["School Code"], errors="coerce")

    api = api.dropna(subset=["School Code"])
    api["School Code"] = api["School Code"].astype(int)
    api['Metric'] = api['Metric'].str.replace('Student Growth', '').str.strip()
    return api.loc[api["School Year"] == "2023-2024"].copy()

def load_isbe_data():
    isbe = pd.read_csv('../data/ISBE Designation - Sheet1.csv')
    isbe = isbe[isbe['ISBE Accountability Status'].notna()]
    return isbe

def load_chronic_absenteeism_data():
    chronic_absenteeism = pd.read_csv('../data/Chronic_Absence_SY2022_Present.csv')
    chronic_absenteeism = chronic_absenteeism[(chronic_absenteeism['Category'] == 'ALL') & 
                                                        (chronic_absenteeism['School Year'] == '2023-2024')]
    chronic_absenteeism = chronic_absenteeism[['School Code','Chronic Absence Rate (%)']].copy()
    return chronic_absenteeism

def load_api_dem():
    api = load_clean_api()
    demographics = load_clean_demographics()
    api_dem = api.merge(demographics, left_on='School Code', right_on='School ID', how='left')
    
    return api_dem

def load_community_areas():
    return gpd.read_file('../data/community_area_boundaries.geojson')


def metric_scale():
    """Navy for ELA, burnt orange for Math. Use in every chart that colors by Metric."""
    return alt.Scale(domain=['ELA', 'Mathematics'], range=['#1d4f91', '#c0562b'])

def diverging_scale(values):
    limit = float(abs(values).max())
    return alt.Scale(
        domain=[-limit, -limit / 2, 0, limit / 2, limit],
        range=['#8c510a', '#d8b365', '#f7f7f7', '#5ab4ac', '#01665e'],
    )

def poverty_scale(order):
    """Sequential ramp for poverty quartile (lowest -> highest). Lightest step is still mid-tone."""
    return alt.Scale(domain=list(order), range=['#8fd3bf', '#4fb0a5', '#2a8a93', '#16607a'])

def poverty_labels():
    return ['Fewest low-income students', 'Lower-middle', 'Upper-middle', 'Most low-income students']

def add_poverty_quartile(df):
    demographics = load_clean_demographics()
    schools = demographics[['School ID', 'Low Income %']].drop_duplicates().dropna()
    _, bins = pd.qcut(schools['Low Income %'], 4, retbins=True)

    bins = bins.astype(float)
    bins[0], bins[-1] = -np.inf, np.inf

    df = df.copy()
    df['Poverty quartile'] = pd.cut(df['Low Income %'], bins=bins, labels=poverty_labels())
    return df