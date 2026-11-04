import altair as alt
import pandas as pd

import data_prep as prep

def create_chart_1():
    api_dem = prep.load_api_dem()

    points = alt.Chart(api_dem).mark_point(filled=True, opacity=0.5).encode(
    x=alt.X('Low Income %:Q', title='Low-income students at school (%)'),
    y=alt.Y('EffectSize:Q', title='Growth effect size'),
    color=alt.Color('Metric:N', scale=prep.metric_scale(), title='Subject')
    )
    
    trend = points.transform_regression(
        'Low Income %',
        'EffectSize',
        groupby=['Metric']
    ).mark_line()
    
    chart_1 = (points + trend).properties(
        width=450, height=350,
        title=alt.TitleParams(
            text='Academic growth vs. school poverty level',
            subtitle=['Each point is one school. Lines show the linear trend for each subject.']
        )
    )

    return chart_1

def create_chart_2():
    isbe = prep.load_isbe_data()
    api = prep.load_clean_api()
    
    api_isbe = isbe.merge(api, right_on = 'School Code', left_on = 'School ID', how = 'left')
    api_isbe = api_isbe[api_isbe['Metric'].notna()]
    
    sorted_order = ['Exemplary', 'Commendable', 'Targeted', 'Comprehensive', 'Intensive']
    
    
    chart_2 = alt.Chart(api_isbe).mark_boxplot(extent='min-max').encode(
        y=alt.Y('ISBE Accountability Status:N', title='ISBE school designation', sort=sorted_order),
        yOffset='Metric:N',
        x=alt.X('EffectSize:Q', title='Growth effect size',
            scale=alt.Scale(domain=[-1.5, 1.5]),
            axis=alt.Axis(values=[-1.5, -1, -0.5, 0, 0.5, 1, 1.5])),
        color=alt.Color('Metric:N', scale=prep.metric_scale(), title = 'Subject')
    ).properties(
        width=450, height=350,
        title=alt.TitleParams(
            text='Academic growth by ISBE school designation',
            subtitle=['Each box spans the middle 50% of schools (25th to 75th percentile); the white line is the median.',
                      'Thin lines extend to the lowest and highest school. They are not error bars.']
        )
    )
    
    return chart_2

def _heatmap_data():
    five_e = prep.load_clean_five_essentials()[['School ID', '2024 Avg Label']]
    api_dem = prep.load_api_dem()

    df = (five_e.merge(api_dem, on='School ID', how='inner').dropna(subset=['2024 Avg Label']))
    df = prep.add_poverty_quartile(df)
    df = df.dropna(subset=['Poverty quartile'])

    cells = (df.groupby(['2024 Avg Label', 'Poverty quartile', 'Metric'], observed=True)
               .agg(avg_growth=('EffectSize', 'mean'), n=('EffectSize', 'size'))
               .reset_index())
    
    cells['Poverty quartile'] = cells['Poverty quartile'].astype(str)
    cells['2024 Avg Label'] = cells['2024 Avg Label'].astype(str)
    return cells


def create_chart_3():
    cells = _heatmap_data()
    poverty_order = prep.poverty_labels()
    climate_order = sorted(cells['2024 Avg Label'].unique(),
                           key=lambda label: float(label.split(' ')[0]))

    chart_3 = alt.Chart(cells).mark_rect().encode(
        x=alt.X('2024 Avg Label:O', title='5Essentials climate score',
                sort=climate_order,
                axis=alt.Axis(labelAngle=0, labelPadding=6, titlePadding=10)),
        y=alt.Y('Poverty quartile:O', title='Low-income share', sort=poverty_order),
        color=alt.Color('avg_growth:Q', title='Avg growth effect size',
                        scale=prep.diverging_scale(cells['avg_growth'])),
    ).properties(width=260, height=180
    ).facet(column=alt.Column('Metric:N', title=None)
    ).properties(
        title=alt.TitleParams(
            text='Academic growth by school climate and low-income share',
            subtitle=['Each cell is the average growth effect size of schools in that group.',
                      'Gray cells have no schools.'],
            anchor='middle',
            offset=30,
        )
    )

    # Empty cells have no row, so the panel background shows through as gray
    return chart_3.configure_view(fill='#d9d9d9')

def _absenteeism_data():
    api_dem = prep.load_api_dem()
    absenteeism = prep.load_chronic_absenteeism_data()

    df = absenteeism.merge(api_dem, on='School Code')
    df = prep.add_poverty_quartile(df)
    df = df[['Metric', 'EffectSize', 'Chronic Absence Rate (%)', 'Poverty quartile']]
    df = df.dropna(subset=['Poverty quartile']).copy()
    df['Poverty quartile'] = df['Poverty quartile'].astype(str)
    return df


def create_chart_4():
    df = _absenteeism_data()
    poverty_order = prep.poverty_labels()

    points = alt.Chart(df).mark_point(
        filled=True, opacity=0.6, stroke='white', strokeWidth=0.5
    ).encode(
        x=alt.X('Chronic Absence Rate (%):Q', title='Chronic absenteeism rate (%)'),
        y=alt.Y('EffectSize:Q', title='Growth effect size'),
        color=alt.Color('Poverty quartile:N', title='Low-income share',
                sort=poverty_order, scale=prep.poverty_scale(poverty_order),
                legend=alt.Legend(orient='none', direction='horizontal',
                  titleAnchor='middle', columns=4,
                  legendX=95, legendY=360)),
    )

    trends = points.transform_regression(
        'Chronic Absence Rate (%)', 'EffectSize',
        groupby=['Poverty quartile'], extent=[0, 100]
    ).mark_line(size=3, opacity=1)

    chart_4 = (points + trends).properties(
        width=300, height=300
    ).facet(
        column=alt.Column('Metric:N', title=None)
    ).properties(
        title=alt.TitleParams(
            text='Academic growth and chronic absenteeism, by school low-income share',
            subtitle=['Each point is one school. Lines show the linear trend within each low-income group.',
                      'Lines span the full axis, so read them cautiously where a group has few schools.'],
            anchor='middle',
            offset=30,
        )
    )

    return chart_4

def _map_data():
    community_areas = prep.load_community_areas()
    api_dem = prep.load_api_dem()

    regional = (api_dem.groupby(['Community Area', 'Metric'])['EffectSize']
                .mean().reset_index())
    regional['Community Area'] = regional['Community Area'].str.upper().str.strip()
    regional = regional[regional['Metric'] == 'ELA']

    ela_shapes = community_areas.merge(
        regional, left_on='community', right_on='Community Area', how='inner'
    )
    return community_areas, ela_shapes, regional['EffectSize']


def _label_layers(community_areas):
    pts = community_areas.geometry.representative_point()
    centers = pd.DataFrame({
        'community': community_areas['community'],
        'lon': pts.x,
        'lat': pts.y,
    })

    anchors = pd.DataFrame({
        'community': ['OHARE', 'AUSTIN', 'ENGLEWOOD', 'LOOP', 'HYDE PARK', 'ROGERS PARK'],
        'name':      ["O'Hare", 'Austin', 'Englewood', 'The Loop', 'Hyde Park', 'Rogers Park'],
        'label_lon': [-87.98,   -87.98,   -87.86,      -87.46,     -87.46,      -87.46],
        'label_lat': [41.99,     41.89,    41.76,       41.88,      41.79,       42.00],
        'side':      ['west',   'west',   'west',      'east',     'east',      'east'],
    })
    labels = anchors.merge(centers, on='community')

    lines = alt.Chart(labels).mark_rule(color='#444', strokeWidth=1).encode(
        longitude='lon:Q', latitude='lat:Q',
        longitude2='label_lon:Q', latitude2='label_lat:Q',
    )
    dots = alt.Chart(labels).mark_circle(color='#222', size=25).encode(
        longitude='lon:Q', latitude='lat:Q'
    )

    def text_for(side, align, dx):
        return alt.Chart(labels[labels['side'] == side]).mark_text(
            fontSize=11, fontWeight='bold', align=align, dx=dx
        ).encode(longitude='label_lon:Q', latitude='label_lat:Q', text='name:N')

    return [lines, dots, text_for('west', 'right', -4), text_for('east', 'left', 4)]


def create_chart_5():
    """Map of average ELA growth by Chicago community area."""
    community_areas, ela_shapes, ela_values = _map_data()

    # Every area in gray; areas with data are painted over it
    background = alt.Chart(community_areas).mark_geoshape(
        fill='#d9d9d9', stroke='white', strokeWidth=0.6
    )

    colored = alt.Chart(ela_shapes).mark_geoshape(
        stroke='white', strokeWidth=0.6
    ).encode(
        color=alt.Color('EffectSize:Q', title='Avg growth effect size',
                        scale=prep.diverging_scale(ela_values),
                        legend=alt.Legend(format='.2f', orient='bottom',
                                          direction='horizontal',
                                          gradientLength=200, offset=-50)),
    )

    chart_5 = alt.layer(background, colored, *_label_layers(community_areas)).properties(
        width=380, height=480, padding={'left': 20, 'right': 60},
        title=alt.TitleParams(
            text='Average ELA academic growth by community area',
            subtitle=['Each area is colored by the average growth effect size of its schools.',
                      'Brown areas fall below zero and teal areas above. Labeled areas are for orientation.'],
            anchor='middle',
            offset=-30,
        ),
    ).project(type='mercator')

    return chart_5

def _enrollment_data():
    """Average growth and school count by enrollment trend, poverty group, and subject."""
    enroll = prep.calculate_enrollment_change()
    api_dem = prep.load_api_dem()

    df = api_dem.merge(enroll[['School ID', 'Trend']], on='School ID')
    df = prep.add_poverty_quartile(df)
    df = df.dropna(subset=['Poverty quartile'])

    summary = (df.groupby(['Trend', 'Poverty quartile', 'Metric'], observed=True)
                 .agg(avg_growth=('EffectSize', 'mean'), n=('EffectSize', 'size'))
                 .reset_index())
    summary['Poverty quartile'] = summary['Poverty quartile'].astype(str)
    return summary

def create_chart_6():
    """Grouped bars of average growth by enrollment trend and poverty group."""
    summary = _enrollment_data()
    poverty_order = prep.poverty_labels()

    chart_6 = alt.Chart(summary).mark_bar().encode(
        x=alt.X('Trend:N',
                sort=['Consistent decline', 'Mixed', 'Consistent growth'],
                title='School enrollment trend',
                axis=alt.Axis(labelAngle=0, titlePadding=10)),
        xOffset=alt.XOffset('Poverty quartile:N', sort=poverty_order),
        y=alt.Y('avg_growth:Q', title='Average growth effect size'),
        color=alt.Color('Poverty quartile:N', title='Low-income share',
                        sort=poverty_order, scale=prep.poverty_scale(poverty_order),
                        legend=alt.Legend(orient='none', direction='horizontal',
                                          titleAnchor='middle', columns=4,
                                          legendX=80, legendY=355)),
    ).properties(width=300, height=300
    ).facet(column=alt.Column('Metric:N', title=None)
    ).properties(
        padding={'right': 190, 'bottom': 60},
        title=alt.TitleParams(
            text='Academic growth by school enrollment trend and low-income share',
            subtitle=['Each bar is the average growth effect size of schools in that group.',
                      'Consistent decline or growth: enrollment fell or rose in at least 3 of 4 years, 2020 to 2024.',
                      'Otherwise the trend is mixed.'],
            anchor='middle',
            offset=20,
        )
    )
    return chart_6
    