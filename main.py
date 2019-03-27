from flask import Flask, render_template, request, flash
from wtforms import Form, StringField, validators
from string import Template
import dbconn
import psycopg2

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

class ReusableForm(Form):
    name = StringField('Name:', validators=[validators.required()])
    projectName = StringField('Project Name:', validators=[validators.required()])
    comment = StringField('Summary:', validators=[validators.required()])
    details = StringField('Details:', validators=[validators.required()])


@app.route('/')
def home():
    conn = None
    data = {}
    try:
        # read connection parameters
        conn = dbconn.getconnection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM public.projectdata;')
        data = cur.fetchall()
        for x in range(len(data)):
            data[x] = data[x] + (str("./projects/"+data[x][0].replace(" ", '')), 0)
        # close the communication with the PostgreSQL
        cur.close()
        # Sort by votes
        data.sort(key=lambda v: (v[3][0]-v[3][1]), reverse=True)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return render_template('home.html', dt=data)


@app.route('/projects/<project>')
def showproject(project):
    conn = None
    data = {}
    try:
        # read connection parameters
        conn = dbconn.getconnection()
        cur = conn.cursor()
        query = 'SELECT * FROM public.projectdata WHERE project = \'%s\';' % project
        cur.execute(query)
        data = cur.fetchall()
        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return render_template('projectlayout.html', some_project=project, dt=data)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/create', methods=['GET', 'POST'])
def create():
    form = ReusableForm(request.form)
    if request.method == 'POST':
        name = request.form['name']
        project = request.form['projectName']
        comment = request.form['comment']
        details = request.form['details']
        result = False
        if form.validate():
            conn = None
            try:
                # read connection parameters
                conn = dbconn.getconnection()

                # create a cursor
                cur = conn.cursor()

                data = ("'%s'" % name, "'%s'" % project, "'%s'" % comment, "'%s'" % details)
                query = "INSERT INTO public.projectdata (name, project, comment, projectinfo) VALUES (%s, %s, %s, %s);" % data

                cur.execute(query)
                conn.commit()
                # close the communication with the PostgreSQL
                cur.close()
            except (Exception, psycopg2.DatabaseError) as error:
                if 'duplicate' in str(error):
                    flash("Duplicate Project Name", category='error')
                print(error)
                result = True
            finally:
                if conn is not None:
                    conn.close()
            if not result:
                flash("Project %s added" % project, category='success')
    return render_template('create.html', form=form)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)