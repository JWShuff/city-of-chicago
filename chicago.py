import csv
import psycopg2
import os

def drop_properties_table():
    return ("DROP TABLE IF EXISTS employees CASCADE;")
    
# Table creation, revisit if varchar fields are broken.
def table_creation_query():
    return ("CREATE TABLE employees (id serial PRIMARY KEY, first_name varchar(255), last_name varchar(255), job_title varchar(60), full_or_part_time varchar, department varchar(255), annual_salary integer);")

def clean_data(csv_row):
    cleaned = {}
    # first_name
    # last_name
    ### data comes in as name row['name'] = "Last,  First MI"
    last_first = csv_row['Name'].split(",")
    first_temp = last_first[1].strip() #this discards Middle Initial
    # first.strip() # in case of any leading whitespace from the last_first split
    first = first_temp.split()
    cleaned['last_name'] = last_first[0]
    cleaned['first_name'] = first[0]
    # cleaned['first_name'] = last_first[1].strip() #JWS tagged in as a kludge
    # job_title
    cleaned['job_title'] =csv_row['Job Titles']
    # full_or_part_time "P/F"
    cleaned['full_or_part_time'] = csv_row['Full or Part-Time']
    # department "str"
    cleaned['department'] = csv_row['Department']
    # annual salary
    ### has to catch hourly vs salary, 
    if csv_row['Salary or Hourly']== 'Hourly':
        hourly_annual = 0
    ### and convert hourly to salary via:
    ### hours_per_week * hourly_rate * 50 to int
        hourly_annual = int(float(csv_row['Typical Hours']) * float(csv_row['Hourly Rate'])* float(50))
        cleaned['annual_salary'] = hourly_annual
    else:
        cleaned['annual_salary'] = int(float(csv_row['Annual Salary']))
    return cleaned


connection = psycopg2.connect(
    f"dbname=chicago_salaries user={os.getlogin()}")
print("Connected!")
cursor = connection.cursor()
cursor.execute(drop_properties_table()) # Might comment this out after the first run
print("Dropped Table!")
cursor.execute(table_creation_query()) # Might comment this out after the first run
print("Created Table")

# Dict Reader to read from CSV:
with open('data/chicago_salaries.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        cleaned_data = clean_data(row)
        cursor.execute("INSERT INTO employees (first_name, last_name, job_title, full_or_part_time, department, annual_salary) VALUES (%s,%s,%s,%s,%s,%s)", (
            cleaned_data['first_name'],
            cleaned_data['last_name'],
            cleaned_data['job_title'],
            cleaned_data['full_or_part_time'],
            cleaned_data['department'],
            cleaned_data['annual_salary'])
        )

connection.commit()
connection.close()
