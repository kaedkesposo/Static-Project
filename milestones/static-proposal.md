# Kaed Esposo

## Description

I want to explore the relationship between school characteristics and academic outcomes in Chicago Public Schools (CPS). My interest in education policy grew through my summer work with an education nonprofit, where I analyzed school-level data.

My goal is to create a suite of visualizations showing how academic outcomes vary alongside student attendance, demographic composition, and school organizational conditions. I am particularly interested in whether schools with higher Academic Progress Indicator scores share certain characteristics, and which schools demonstrate strong academic progress despite facing greater socioeconomic challenges.

Potential visualizations include comparisons across school types, scatterplots examining relationships between academic progress and chronic absenteeism, and trends over time where comparable data is available. 

## Data Sources

### Data Source 1: Chicago Public Schools Metrics

URL: https://www.cps.edu/about/district-data/metrics/

Dataset: API_StudentGrowth_SY2024_Present.xlsx, available through the Academic Progress Indicator report.

Size: 42,134 rows, 12 columns.

This dataset reports student growth in English language arts and mathematics by school, school year, and student group. It is in long format, so each school has multiple rows for different subjects and breakdowns, including grade level, race/ethnicity, economic disadvantage, English learner status, and IEP status. It also includes district totals.

I have reviewed the spreadsheet and its data dictionary. I plan to use the school-wide results to compare academic progress across schools and the subgroup results to explore differences within schools. School codes and school years will be used to connect these records with other CPS datasets.

### Data Source 2: Chicago Public Schools Demographics

URL: https://www.cps.edu/about/district-data/demographics/

Size:
English Learners, Students with IEPs, and Low Income report: 641 rows, 13 columns.
Racial/Ethnic report: 641 rows, 25 columns.

These reports provide school-level demographic information, including the proportions of low-income students, English learners, and students with IEPs, along with student counts and percentages by race/ethnicity. They also include school characteristics such as network, governance, school type, and community area.

I plan to join the reports using School ID and explore how academic progress varies across schools serving different student populations.

### Data Source 3: ISBE Report Card

URL: https://www.isbe.net/pages/illinois-state-report-card-data.aspx

Size: 4,692 rows, 900 columns in the General tab, before filtering to CPS.

This workbook contains several tabs covering different aspects of school performance across Illinois. I plan to use the General tab, which includes school identifiers, school characteristics, and summative designations. I will filter it to CPS school-level records and retain only the relevant columns.

I would use summative designation to compare academic progress and school conditions across schools with different accountability ratings. 

### Data Source 4: UChicago 5Essentials

URL: https://www.5-essentials.org/

Size: 24,128 rows, 6 columns.

5Essentials is a school climate survey that measures five areas: Effective Leaders, Collaborative Teachers, Ambitious Instruction, Involved Families, and Supportive Environment.

I already have school-level data collected through a web scraper during my summer fellowship, so no additional scraping would be needed. The dataset has 24,128 rows and 6 columns, with one row per school per submeasure. It can be reorganized into one row per school with separate columns for the five overall measures.

I plan to use these measures to explore how school organizational conditions relate to academic progress. Because the data was previously scraped rather than obtained through a public bulk download, I would like to confirm whether they meet the assignment’s data-source requirements.

## Questions

1. I noticed that a student two years ago also did their project on Chicago Public Schools. Would it be okay to use the same topic and some of the same data sources if I focus on different questions, or should I choose a different topic?

