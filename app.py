'''
This is the main file for the application. 
It contains the routes and views for the application.
'''

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from database import opendb, DB_URL
from database import User, Profile, Product
from db_helper import *
from validators import *
from logger import log
from werkzeug.utils import secure_filename
import os
import numpy as np #for algebric calculations
import pandas as pd #essential for data reading,writing etc
import seaborn as sns #visualization library
import plotly.express as px #ploting parameter's
import matplotlib #visualization library.
import matplotlib.pyplot as plt #visualization library.
import sys #for System-specific parameters and functions.
from flask import Flask,session,flash,redirect,render_template,url_for
import warnings
from forecasting import load_model, load_xunique, predict
import joblib

app = Flask(__name__)
app.secret_key  = '()*(#@!@#)'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

def session_add(key, value):
    session[key] = value

def save_file(file):
    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    return path

def load_dataset():
    df=pd.read_csv(r'C:\Users\vibhu\OneDrive\Documents\Desktop\education of data science\job-trend-analysis-using-ai\naukri_com-job_sample.csv')  
    # print(df.columns)
    return df

def load_model():
    return joblib.load('model.joblib')

def predict(data):
    model = load_model()
    return model.predict(data)[0]

def preprocess_dataset(df):
    # all processing code
    pay_split = df['payrate'].str[0:-1].str.split('-', expand=True)
    pay_split[1] =  pay_split[1].str.strip()
    #remove comma 
    pay_split[1] = pay_split[1].str.replace(',', '')
    #remove all character in two condition
    # 1 remove if only character
    # 2 if start in number remove after all character
    pay_split[1] = pay_split[1].str.replace(r'\D.*','')
    pay_split[0] = pd.to_numeric(pay_split[0], errors='coerce')
    pay_split[1] = pd.to_numeric(pay_split[1], errors='coerce')
    pay=pd.concat([pay_split[0], pay_split[1]], axis=1, sort=False)
    pay.rename(columns={0:'min_pay', 1:'max_pay'}, inplace=True )
    df=pd.concat([df, pay], axis=1, sort=False)
    return df

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not validate_email(email):
            flash('Invalid email', 'danger')
            return redirect(url_for('login'))
        if not validate_password(password):
            flash('Invalid password', 'danger')
            return redirect(url_for('login'))
        db = opendb()
        user = db.query(User).filter_by(email=email).first()
        if user is not None and user.verify_password(password):
            session_add('user_id', user.id)
            session_add('user_name', user.name)
            session_add('user_email', user.email)
            session_add('isauth', True)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
            #return redirect(url_for('samplehome')
            return render_template('login.html')
    else:
        return render_template('login.html')
    
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    cpassword = request.form.get('cpassword')
    db = opendb()
    if not validate_username(name):
        flash('Invalid username', 'danger')
        return redirect(url_for('index'))
    if not validate_email(email):
        flash('Invalid email', 'danger')
        return redirect(url_for('index'))
    if not validate_password(password):
        flash('Invalid password', 'danger')
        return redirect(url_for('index'))
    if password != cpassword:
        flash('Passwords do not match', 'danger')
        return redirect(url_for('index'))
    if db.query(User).filter_by(email=email).first() is not None    :
        flash('Email already exists', 'danger')
        return redirect(url_for('index'))
    elif db.query(User).filter_by(name=name).first() is not None:
        flash('Username already exists', 'danger')
        return redirect(url_for('index'))
    else:
        db_save(User(name=name, email=email, password=password))
        flash('User registered successfully', 'success')
        return redirect(url_for('index'))
    return render_template('register_modal.html')

@app.route('/dashboard')
def dashboard():
    if session.get('isauth'):
        return render_template('dashboard.html')
    else:
        return redirect(url_for('index'))

@app.route('/profile/add', methods=['POST'])
def add_profile():
    if session.get('isauth'):
        user_id = session.get('user_id')
        city = request.form.get('city')
        gender = request.form.get('gender')
        avatar = request.files.get('avatar')
        db = opendb()
        if not validate_city(city):
            flash('Invalid city', 'danger')
            return redirect(url_for('dashboard'))
        if not validate_avatar(avatar):
            flash('Invalid avatar file', 'danger')
            return redirect(url_for('dashboard'))
        if db.query(Profile).filter_by(user_id=user_id).first() is not None:
            flash('Profile already exists', 'danger')
            return redirect(url_for('view_profile'))
        else:
            db_save(Profile(user_id = user_id, city=city, gender=gender, avatar=save_file(avatar)))
            flash('Profile added successfully', 'success')
            return redirect(url_for('dashboard'))
    else:
        flash('Please login to continue', 'danger')
        return redirect(url_for('index'))
        
@app.route('/profile/edit', methods=['POST'])
def edit_profile():
    if session.get('isauth'):
        profile = db_get_by_field(Profile, user_id=session.get('user_id'))
        if profile is not None:
            profile.city = request.form.get('city')
            profile.gender = request.form.get('gender')
            avatar = request.files.get('avatar')
            if avatar is not None:
                profile.avatar = save_file(avatar)
            db_save(profile)
            flash('Profile updated successfully', 'success')
            return redirect(url_for('dashboard'))
    else:
        flash('Please login to continue', 'danger')
        return redirect(url_for('index'))    

@app.route('/profile')
def view_profile():
    if session.get('isauth'):
        profile = db_get_by_field(Profile, user_id=session.get('user_id'))
        if profile is not None:
            return render_template('profile.html', profile=profile)
        else:
            flash(f'<a class="text-danger" href="#" data-bs-toggle="modal" data-bs-target="#profileModal">Create a profile</a>', 'danger')
            return redirect(url_for('dashboard'))
    else:
        flash('Please login to continue', 'danger')
        return redirect(url_for('index'))
    
@app.route('/analysis/1')
def analysis1():
    df=load_dataset()
    count_missing = df.isnull().sum()
    percent_missing =  count_missing* 100 / df.shape[0]
    missing_value_df = pd.DataFrame({'count_missing': count_missing,
                                 'percent_missing': percent_missing})

    missing_value_df.style.background_gradient(cmap='Spectral')

    unique_df = unique_df = pd.DataFrame([[df[i].nunique()]for i in df.columns], columns=['Unique Values'], index=df.columns)
    unique_df.style.background_gradient(cmap='magma')
    nrow,ncol=df.shape
    info1 = f'There are {nrow} rows and {ncol} colunms in the dataset'
   

    # filter and find unique() cities from data set
    df.joblocation_address = df.joblocation_address.str.upper()
    new_location =df.joblocation_address.str.strip().str.split(",", expand = True)[0].str.split(" ", expand = True)[0].value_counts().reset_index()
    new_location.columns = ["Location", "Job_Opportunities"]
    new_location = new_location[:10]
    new_location.style.background_gradient(cmap = "PuOr") 

    #Dataset Summary statistics 
    df.describe(include = ['object']).T

    categorical = [var for var in df.columns if df[var].dtype=='O']

    count_missing = df[categorical].isnull().sum()
    percent_missing =  count_missing* 100 / df.shape[0]
    missing_value_df = pd.DataFrame({'count_missing': count_missing,
                                 'percent_missing': percent_missing})

    missing_value_df.style.background_gradient(cmap='tab20b')

    # check missing values in numerical variables
    numerical = [var for var in df.columns if df[var].dtype!='O']

    count_missing = df[numerical].isnull().sum()
    percent_missing =  count_missing* 100 / df.shape[0]
    missing_value_df = pd.DataFrame({'count_missing': count_missing,
                                    'percent_missing': percent_missing})

    missing_value_df.style.background_gradient(cmap='coolwarm')

    #display the company names..highest to lowest
    com_Category = df.company.str.lstrip().str.rstrip().value_counts().reset_index()
    com_Category.columns = ["Company", " Number of Company"]
    com_Category = com_Category[:10]
    com_Category.style.background_gradient(cmap = "tab20c")

    #diplay the jobtitle.
    Category = df.jobtitle.str.lstrip().str.rstrip().value_counts().reset_index()
    Category.columns = ["jobtitle", " Number of Jobtitle"]
    Category = Category[:10]
    Category.style.background_gradient(cmap = "Greens")

    # display the skills
    skills_Category = df.skills.str.lstrip().str.rstrip().value_counts().reset_index()
    skills_Category.columns = ["Skills", " Number of Skills"]
    skills_Category = skills_Category[:10]
    skills_Category.style.background_gradient(cmap = "hot")

    return render_template('analysis1.html',title='Analysis for values',
                           data=missing_value_df.to_html(),
                           unique_data = unique_df.to_html(), 
                           info1 = info1,
                           columns = df.columns.to_list(),
                           new_location = new_location.to_html())


@app.route('/corelation')
def co_relation():
    df = load_dataset()
    print(df.columns)
    
    # split method to split payrate min to max

    pay_split = df['payrate'].str[0:-1].str.split('-', expand=True)

    #remove space in left and right
    pay_split[0] =  pay_split[0].str.strip()

    #remove comma 
    pay_split[0] = pay_split[0].str.replace(',', '')

    #remove all character in two condition
    # 1 remove if only character
    # 2 if start in number remove after all character
    pay_split[0] = pay_split[0].str.replace(r'\D.*', '')

    #remove space in left and right 
    pay_split[1] =  pay_split[1].str.strip()

    #remove comma 
    pay_split[1] = pay_split[1].str.replace(',', '')

    #remove all character in two condition
    # 1 remove if only character
    # 2 if start in number remove after all character
    pay_split[1] = pay_split[1].str.replace(r'\D.*','')

    pay_split[0] = pd.to_numeric(pay_split[0], errors='coerce')
    pay_split[1] = pd.to_numeric(pay_split[1], errors='coerce')

    pay=pd.concat([pay_split[0], pay_split[1]], axis=1, sort=False)

    # rename the columns into min payrate and max payrate.
    pay.rename(columns={0:'min_pay', 1:'max_pay'}, inplace=True )

    # min and max payarte store the value in the dataframe.

    df=pd.concat([df, pay], axis=1, sort=False)

    df['avg_payrate']=(df['min_pay'].values + df['max_pay'].values)/2

    # spliting the experience into min experience to max experience.

    experience_split = df['experience'].str[0:-1].str.split('-', expand=True)

    #remove space in left and right 
    experience_split[0] =  experience_split[0].str.strip()

    #remove comma 
    experience_split[0] = experience_split[0].str.replace('yr', '')

    #remove all character in two condition
    # 1 remove if only character
    # 2 if start in number remove after all character
    experience_split[0] = experience_split[0].str.replace(r'yr', '')

    #remove space in left and right 
    experience_split[1] =  experience_split[1].str.strip()

    #remove comma 
    experience_split[1] = experience_split[1].str.replace('yr', '')

    #remove all character in two condition
    # 1 remove if only character
    # 2 if start in number remove after all character
    experience_split[1] = experience_split[1].str.replace(r'yr', '')

    experience_split[0] = pd.to_numeric(experience_split[0], errors='coerce')
    experience_split[1] = pd.to_numeric(experience_split[1], errors='coerce')

    experience=pd.concat([experience_split[0], experience_split[1]], axis=1, sort=False)

    # rename the cloumns to min and max experience

    experience.rename(columns={0:'min_experience', 1:'max_experience'}, inplace=True)
    
    # store the min and max experience in the dataframe.

    df=pd.concat([df, experience], axis=1, sort=False)

    # Display average payrate and average experience.
    # min experience and max experience define the average experience.
    # min payrate and max payrate define the average payrate.

    df['avg_payrate']=(df['min_pay'].values + df['max_pay'].values)/2
    df['avg_experience']=(df['min_experience'].values + df['max_experience'].values)/2

    df['postdate'].dtypes
    df['postdate'] = pd.to_datetime(df['postdate'])
    df['Year'] = df['postdate'].dt.year

    df['avg_experience']=(df['min_experience'].values + df['max_experience'].values)/2
    fig1 = px.scatter_3d(df, x='avg_payrate', y='avg_experience', z='Year', color='avg_payrate', hover_data=['jobtitle'], title='3D Scatter Plot', width=800, height=600)

    fig2 =px.histogram(df, x='min_experience', y='min_pay', title='Relation between min_exp and min_pay', color_discrete_sequence=px.colors.sequential.RdBu, width=800, height=500, opacity=0.8, color='min_pay', hover_data=['min_experience', 'min_pay'], labels={'min_exp':'min_exp', 'min_pay':'min_pay'}, template='plotly_dark')

    fig3 =px.area(df, x='max_experience', y='max_pay', title='Relation between max_exp and max_pay', color_discrete_sequence=px.colors.sequential.RdBu, width=800, height=500,color='max_pay', hover_data=['max_experience', 'max_pay'], labels={'max_exp':'max_exp', 'max_pay':'max_pay'}, template='plotly_dark')

    fig4 = px.scatter(x='avg_experience', y='avg_payrate', data_frame=df, color='avg_payrate', title='Relation between avg_exp and avg_payrate', color_continuous_scale=px.colors.sequential.RdBu, width=800, height=500, opacity=0.8, hover_data=['avg_experience', 'avg_payrate'], labels={'avg_exp':'avg_exp', 'avg_payrate':'avg_payrate'}, template='plotly_dark')

    fig5 = px.scatter_3d(df, x='min_experience', y='max_experience', z='min_pay', color='min_pay', title='Relation between min_exp, max_exp and min_pay', color_continuous_scale=px.colors.sequential.RdBu, width=800, height=500, opacity=0.8, hover_data=['min_experience', 'max_experience', 'min_pay'], labels={'min_exp':'min_exp', 'max_exp':'max_exp', 'min_pay':'min_pay'}, template='plotly_dark')


    return render_template('corelation.html',
                            fig1=fig1.to_html(),
                            fig2=fig2.to_html(),
                            fig3=fig3.to_html(),
                            fig4=fig4.to_html(),
                            fig5=fig5.to_html())

@app.route('/comparison')
def co_mparison():
    df = load_dataset()

    
    # split method to split payrate min to max

    pay_split = df['payrate'].str[0:-1].str.split('-', expand=True)

    #remove space in left and right
    pay_split[0] =  pay_split[0].str.strip()

    #remove comma 
    pay_split[0] = pay_split[0].str.replace(',', '')

    #remove all character in two condition
    # 1 remove if only character
    # 2 if start in number remove after all character
    pay_split[0] = pay_split[0].str.replace(r'\D.*', '')

    #remove space in left and right 
    pay_split[1] =  pay_split[1].str.strip()

    #remove comma 
    pay_split[1] = pay_split[1].str.replace(',', '')

    #remove all character in two condition
    # 1 remove if only character
    # 2 if start in number remove after all character
    pay_split[1] = pay_split[1].str.replace(r'\D.*','')

    pay_split[0] = pd.to_numeric(pay_split[0], errors='coerce')
    pay_split[1] = pd.to_numeric(pay_split[1], errors='coerce')

    pay=pd.concat([pay_split[0], pay_split[1]], axis=1, sort=False)

    # rename the columns into min payrate and max payrate.
    pay.rename(columns={0:'min_pay', 1:'max_pay'}, inplace=True )

    # min and max payarte store the value in the dataframe.

    df=pd.concat([df, pay], axis=1, sort=False)

    df['avg_payrate']=(df['min_pay'].values + df['max_pay'].values)/2

    fig7 = px.scatter(df, x='industry', y='max_pay', color='industry', title='Relation between max_pay and industry', color_continuous_scale=px.colors.sequential.RdBu, width=800, height=800, opacity=0.8, hover_data=['max_pay', 'industry'], labels={'max_pay':'max_pay', 'industry':'industry'}, template='plotly_dark')

    fig8 = df[['min_pay','industry']].groupby(["industry"]).median().sort_values(by='min_pay', ascending=False).head(10)
    px.area(df, x='industry', y='min_pay', title='Relation between min_pay and industry', color_discrete_sequence=px.colors.sequential.RdBu, width=800, height=500, hover_data=['min_pay', 'industry'], labels={'min_pay':'min_pay', 'industry':'industry'}, template='plotly_dark')

    fig9 = df[['avg_payrate','skills']].groupby(["skills"]).median().sort_values(by='avg_payrate',
                                                                  ascending=False).head(10)
    px.scatter(df, x='skills', y='avg_payrate', color='skills', title='Relation between avg_payrate and skills', color_continuous_scale=px.colors.sequential.RdBu, width=800, height=800, opacity=0.8, hover_data=['avg_payrate', 'skills'], labels={'avg_payrate':'avg_payrate', 'skills':'skills'}, template='plotly_dark')

    fig10 = df[['avg_payrate','jobtitle']].groupby(["jobtitle"]).median().sort_values(by='avg_payrate',
                                                                        ascending=False).head(10)
    px.sunburst(df, path=['jobtitle'], values='avg_payrate', title='Relation between avg_payrate and jobtitle', width=800, height=800, hover_data=['avg_payrate', 'jobtitle'], labels={'avg_payrate':'avg_payrate', 'jobtitle':'jobtitle'}, template='plotly_dark') 

    return render_template('comparison.html',
                            fig7=fig7.to_html(),
                            fig8=fig8.to_html(),
                            fig9=fig9.to_html(),
                            fig10=fig10.to_html())

@app.route('/forecast', methods=['GET', 'POST'])
def forecast():
    # xunique = load_xunique()
    df = load_dataset()
    comp = df['company'].unique()
    edu = df['education'].unique()
    ind = df['industry'].unique()
    exp = df['experience'].unique()
    loc = df['joblocation_address'].unique()
    title = df['jobtitle'].unique()
    if request.method == "POST":
        company = request.form.get('com')
        education = request.form.get('edu')
        industry = request.form.get('ind')
        experience = request.form.get('exp')
        joblocation_address = request.form.get('loc')
        jobtitle = request.form.get('title')
        # print(company, education, industry, experience, joblocation_address, jobtitle)
        try:
            dfinput = pd.DataFrame({
                'company': [company],
                'education': [education],
                'industry': [industry],
                'experience': [experience],
                'joblocation_address': [joblocation_address],
                'jobtitle': [jobtitle]

            })
            # print(dfinput)
            prediction = predict(dfinput)
            flash('Prediction successful', 'success')
            print(prediction)
            return render_template('forecast.html', comp=comp, edu=edu, ind=ind, exp=exp, loc=loc, title=title, prediction=prediction)
        except Exception as e:
            print(e)
            flash('Please fill all the fields', 'danger')
            return redirect(url_for('forecast'))       
    return render_template('forecast.html', comp=comp, edu=edu, ind=ind, exp=exp, loc=loc, title=title)





if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8000, debug=True)
 