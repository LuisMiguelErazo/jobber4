import pandas as pd
import plotly.express as px
import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import zipfile

# Cargar el archivo CSV desde el archivo zip
with zipfile.ZipFile('map_skills.zip', 'r') as zipf:
    with zipf.open('map_skills.csv') as f:
        df = pd.read_csv(f)

def show_home_page():
    st.title('EarnWise')
    
    # Añadir logotipo
    st.image('logo.png', width=150)

    st.write('''
    Welcome to EarnWise!

    The easiest, fastest and most transparent way to find salary information in your Sector/Industry.

    At this time, we only have information for the United States.

    Help us collect data from other countries by posting your information in the tab "Help Us Grow".
    ''')

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.write("")
    with col2:
        find_insights = st.button('Find your salary insights')
        st.markdown("<h3 style='text-align: center;'>Or</h3>", unsafe_allow_html=True)
        predict_salary = st.button('Predict your salary')
    with col3:
        st.write("")

    return find_insights, predict_salary

def show_salary_insights():
    if st.button('Home'):
        st.session_state.page = "home"
    
    st.subheader('Filters')

    categories = sorted(df['Category'].unique().tolist())
    categories = ['All'] + categories
    category = st.selectbox('Category', categories)

    industries = df['Industry'].unique() if category == 'All' else df[df['Category'] == category]['Industry'].unique()
    industries = ['All'] + sorted(industries.tolist())
    industry = st.selectbox('Industry', industries)

    experiences = df['Experience Level'].unique() if industry == 'All' else df[(df['Category'] == category) & (df['Industry'] == industry)]['Experience Level'].unique()
    experiences = ['All'] + sorted(experiences.tolist())
    experience = st.selectbox('Experience Level', experiences)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(['Map', 'Salary Distribution', 'Salary Insights', 'Key Skills', 'Study Fields', 'Relevant Tools', 'Help Us Grow'])

    def update_map(category, industry, experience):
        filtered_df = df.copy()
        if category != 'All':
            filtered_df = filtered_df[filtered_df['Category'] == category]
        if industry != 'All':
            filtered_df = filtered_df[filtered_df['Industry'] == industry]
        if experience != 'All':
            filtered_df = filtered_df[filtered_df['Experience Level'] == experience]

        state_salary = filtered_df.groupby('State').agg(
            Medium_Salary=('Medium Salary', 'mean')
        ).reset_index()

        fig = px.choropleth(state_salary,
                            locations='State',
                            locationmode='USA-states',
                            color='Medium_Salary',
                            color_continuous_scale='Blues',
                            scope='usa',
                            labels={'Medium_Salary': 'Medium Salary'},
                            hover_data={'State': True, 'Medium_Salary': True})

        fig.update_traces(
            hovertemplate='<b>%{location}</b><br>Medium Salary: $%{z:,.2f}'
        )

        fig.update_layout(title='Medium Salary by State', geo=dict(scope='usa'))
        st.plotly_chart(fig)

    def plot_wordcloud(category, column, soft_skills):
        if category != 'All':
            filtered_df = df[df['Category'] == category]
            text = ' '.join(filtered_df[column].dropna().tolist())
            if text:
                if soft_skills:  
                    freq_dict = {skill.split('. ')[1]: int(skill.split('. ')[0]) for skill in soft_skills}
                    
                    wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='Blues').generate_from_frequencies(freq_dict)
                    plt.figure(figsize=(10, 5))
                    plt.imshow(wordcloud, interpolation='bilinear')
                    plt.axis('off')
                    plt.title(f'Top {column} in {category} Category')
                    st.pyplot(plt)
                else:
                    st.write('No soft skills data available to generate the word cloud')
            else:
                st.write(f'No data available for the selected category and column {column}')
        else:
            st.write('Select a Category to Display Word Cloud')

    def plot_salary_distribution(category, industry):
        filtered_df = df.copy()
        if category != 'All':
            filtered_df = filtered_df[filtered_df['Category'] == category]
        if industry != 'All':
            filtered_df = filtered_df[filtered_df['Industry'] == industry]

        grouped_df = filtered_df.groupby('Experience Level', as_index=False)['Medium Salary'].mean()
        grouped_df = grouped_df.sort_values(by='Medium Salary')

        fig = px.bar(grouped_df, x='Experience Level', y='Medium Salary', color='Medium Salary',
                     color_continuous_scale='Blues', title='Salary Distribution by Experience Level')
        fig.update_traces(texttemplate='$%{y:,.2f}', textposition='outside')

        fig.update_layout(yaxis_tickformat='$,.2f')

        st.plotly_chart(fig)

    def plot_salary_insights(category):
        filtered_df = df.copy()
        if category != 'All':
            filtered_df = filtered_df[filtered_df['Category'] == category]

        fig = px.box(filtered_df, x='Category', y='Medium Salary',
                     title='Salary Insights by Category')

        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>Medium Salary: $%{y:,.2f}<extra></extra>'
        )

        st.plotly_chart(fig)

    def show_list(category, column):
        if category != 'All':
            filtered_df = df[df['Category'] == category]
            items = filtered_df[column].dropna().str.split(',').explode().unique()
            if items.size > 0:
                st.write(f"{column} in {category} Category:")
                for item in items:
                    st.write(f"- {item.strip()}")
            else:
                st.write(f'No data available for the selected category and column {column}')
        else:
            st.write(f'Select a Category to Display {column}')

    with tab1:
        update_map(category, industry, experience)

    with tab2:
        plot_salary_distribution(category, industry)

    with tab3:
        plot_salary_insights(category)

    with tab4:
        soft_skills = ['10. Leadership', '7. Communication', '5. Teamwork']  # Define tu lista de habilidades blandas aquí
        plot_wordcloud(category, 'Soft Skill', soft_skills)

    with tab5:
        show_list(category, 'Study Fields')

    with tab6:
        show_list(category, 'Software Programs')

    with tab7:
        st.header('Help Us Grow')
        with st.form(key='help_us_grow_form'):
            country = st.text_input('Country:')
            state = st.text_input('State:')
            category_input = st.text_input('Category:')
            industry_input = st.text_input('Industry:')
            experience_level = st.text_input('Experience Level:')
            salary = st.text_input('Salary:')

            submit_button = st.form_submit_button(label='Submit')

        if submit_button:
            st.write('Thank you for your submission!')

if 'page' not in st.session_state:
    st.session_state.page = 'home'

if st.session_state.page == 'home':
    find_insights, predict_salary = show_home_page()
    if find_insights:
        st.session_state.page = 'insights'
    elif predict_salary:
        st.write("This feature is coming soon!")
elif st.session_state.page == 'insights':
    show_salary_insights()
