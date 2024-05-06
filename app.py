from flask import Flask, render_template, request, redirect, url_for, flash, session,send_file #,Response
from flask_sqlalchemy import SQLAlchemy   #a library/tool tik, to communicate b/w py program & DB
from sqlalchemy.exc import SQLAlchemyError
from flask_mail import Mail, Message
import random
import base64
from io import BytesIO

#from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["DEBUG"] = True


SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="rajeshtata",
    password="haihello123@",
    hostname="rajeshtata.mysql.pythonanywhere-services.com",
    databasename="rajeshtata$signup",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'rajesh123proceed'

db = SQLAlchemy(app)

class Signup(db.Model):

    __tablename__ = "signup"

    email       = db.Column(db.String(50), primary_key=True) #unique=True
    username    = db.Column(db.String(50), nullable=False)
    password    = db.Column(db.String(50), nullable=False)
    OTP = db.Column(db.String(50), nullable=True)


@app.route('/')
def index():
    return render_template("Home.html")

@app.route('/login')
def login():
    return render_template('Login.html',user_email="")

@app.route('/signup')
def signup():
    return render_template('Signup.html',user_name="",email="",password="")

@app.route('/signedup', methods=['POST'])
def signedup():
    if request.method == "POST":
        mail_id     = request.form["email"]
        un          = request.form['username']
        pw          = request.form['password']

        usercheck = Signup.query.filter_by(email=mail_id).first()

        if usercheck:
            flash('Email already Exits!')
            return render_template('Signup.html',user_name=un,email=mail_id,password=pw)
        else:
            session['signup_email']     = mail_id
            session['signup_username']  = un
            session['signup_password']  = pw

            session['count']=0

            return redirect(url_for('sendingmail'))

@app.route('/sendingmail')
def sendingmail():
    email=session['signup_email']

    usercheck = Signup.query.filter_by(email=email).first()

    if usercheck:
        if usercheck.OTP=='Verified':
            flash('Email already verified, Login now')
            return redirect(url_for('login'))
        else:
            flash('OTP sent. Please check your mail')
            return render_template("verify.html", useremail=email)
    else:
        try:
            mail = Mail(app)

            app.config["MAIL_SERVER"]   = 'smtp.gmail.com'
            app.config["MAIL_PORT"]     = 465
            app.config["MAIL_USERNAME"] = '180040080cse@gmail.com'
            app.config["MAIL_PASSWORD"] = 'poohnxnegfysxngk'
            app.config["MAIL_USE_TLS"]  = False
            app.config["MAIL_USE_SSL"]  = True

            mail    = Mail(app)
            otp     = random.randint(1111, 9999)  # random(00000, 99999)
            session['otp'] = otp

            email=session['signup_email']

            msg     = Message('Verify-OTP', sender='180040080cse@gmail.com', recipients=[email])
            link= "https://rajeshtata.pythonanywhere.com/verifying_user?email="+email+"&OTP="+str(otp)
            print("link to verify",link)
            msg.html = """
                                <html>
                                    <body>
                                        <table width="100%" height="100%">
                                            <tr> <td width="100%" height="100%"> <!--bgcolor="#e2e3e7"-->
                                                <table width="600" align="center" style="border:2px solid black; border-radius:10px;" bgcolor="#FAFDBE">  <!-- #ffffff  F1D6FD -->
                                                        <tr style="background-color:#C4FAF7;"><td style="font-size:18px; font-family:Comic Sans MS;">&#9995;&nbsp;Hello...</td></tr>
                                                        <tr style="background-color:#F1D6FD; font-size:17px;" align="center"> <td> <p>You&nbsp;are&nbsp;almost&nbsp;done, just&nbsp;1&nbsp;step&nbsp;away&nbsp;!<br>Your&nbsp;OTP&nbsp;is&nbsp;<b><u style='color:red;'>""" + str(otp) + """</u></b></p>  </td></tr> <!--style="background-color:#F1D6FD;"-->
                                                        <tr align="center"><td style="font-size:18px; font-family:Comic Sans MS;"><button style="background:black; color:white; border-radius: 10px; cursor:pointer"><a href="""+link+""" style="text-decoration:none; color:white;">Click Here</a></button>to verify</td></tr>
                                                    <tr style="background-color:#E7E9E8;border-radius:4px!important"> <td><code><i>Thanks for signing up</i><br>-Tata.Rajesh Chowdary<br>-180040080(CSE)</i></code></td> </tr>
                                                </table>

                                            </td> </tr>
                                        </table>
                                    </body>
                                </html>


                                """
            mail.send(msg)

            newsignup = Signup(username=session['signup_username'], email=email, password=session['signup_password'], OTP=otp)

            try:
                db.session.add(newsignup)
                db.session.commit()
            except:
                #return "<h2>There was a problem while adding to db</h2>"
                return render_template("error.html",message="There was a problem while adding to database")

            count=session['count']
            count=count+1
            session['count']=count

            print('emails sent count:',count)
            if(count>=2):
                flash('New OTP has been sent')

            return render_template("verify.html", useremail=email)

        except:
            return render_template("error.html",message="Technial issues while sending mail")
            #return "<h3>Please Check your internet connection(speed) & Try Again...</h3>"



@app.route('/validate', methods=["POST"])
def validate():

    otp_email   = session['signup_email']

    validating = Signup.query.filter_by(email=otp_email).first()

    actual_otp = session['otp']
    user_otp   =  request.form['userotp']

    if validating.OTP=='Verified':
        flash('Email already verified, Login to continue..')
        return redirect(url_for('login'))

    elif(int(actual_otp) == int(user_otp) and int(validating.OTP)==int(user_otp) ):
        validating.OTP='Verified'

        try:
            db.session.commit()

            session.pop('signup_username', default=None)
            session.pop('signup_password', default=None)
            session.pop('signup_email', default=None)
            session.pop('otp', default=None)

            flash('Email verified! Login now..')
            return redirect(url_for('login'))

        except:
            return render_template("error.html",message="There was a problem while adding to database")
            #return "<h2>There was a problem while adding to db</h2>"

    else:
        flash("Invalid OTP, try again..")
        return render_template("verify.html", useremail=otp_email)


@app.route('/verifying_user', methods=['GET'])
def verifying_user():
    args = request.args
    verifyinguser = Signup.query.filter_by(email=args.get("email")).first()

    if verifyinguser:
        if  verifyinguser.OTP==args.get("OTP"):
            verifyinguser.OTP='Verified'

            try:
                db.session.commit()
                flash('Email verified! Login now..')
                return redirect(url_for('login'))
            except:
                return "<h2>There was a problem while adding to db</h2>"
        elif verifyinguser.OTP=='Verified':
            flash('Already Verified, Login to continue')
            return redirect(url_for('login'))
        else:
            return "Something went wrong X"
    else:
        return "User NOT found"

@app.route('/login-validate', methods=['POST','GET'])
def loginvalidator():
#    try:
#        if(session['login_active'] == "active"):
#            flash(session['login_email'] is active)

    login_email    = request.form['email']
    login_password = request.form['password']

    print("Step-0")

    loginstatus = Signup.query.filter_by(email=login_email, password=login_password).first()

    if loginstatus:
        if loginstatus.OTP=='Verified':

            session['login_status'] = "active"  #creating a new variable to trackcheck whether user logged in or not before accessing sth
            session['login_email'] = login_email

            return redirect(url_for('home'))

        else:
            flash('Email not verified. Please click your mail & click on verify now')
            return redirect(url_for('login'))
    else:
        flash('Invalid Credentials !')
        return redirect(url_for('login'))

@app.route('/forget-password')
def forgetpassword():
    return render_template("forgetpassword.html");

@app.route('/sending-password', methods=['POST','GET'] )
def sendingpassword():
    user_mail=request.form['email']
    user_data = Signup.query.filter_by(email=user_mail).first()

    password = user_data.password


    try:
        mail = Mail(app)

        app.config["MAIL_SERVER"]   = 'smtp.gmail.com'
        app.config["MAIL_PORT"]     = 465
        app.config["MAIL_USERNAME"] = '180040080cse@gmail.com'
        app.config["MAIL_PASSWORD"] = 'poohnxnegfysxngk'
        app.config["MAIL_USE_TLS"]  = False
        app.config["MAIL_USE_SSL"]  = True

        mail    = Mail(app)


        msg     = Message('Your Password', sender='180040080cse@gmail.com', recipients=[user_mail])
        msg.html = """
                                <html>
                                    <body>
                                        <table width="100%" height="100%">
                                            <tr> <td width="100%" height="100%"> <!--bgcolor="#e2e3e7"-->
                                                <table width="600" align="center" style="border:2px solid black; border-radius:10px;" bgcolor="#FAFDBE">  <!-- #ffffff  F1D6FD -->
                                                         <tr style="font-size:17px;" align="center"> <td> <p>You&nbsp;Password is :<span style="color:red";> """ + (password) + """</span></p> </td> </tr>
                                                       </table>
                                            </td> </tr>
                                        </table>
                                    </body>
                                </html>

                                """
        mail.send(msg)

        flash("Please check your mail for Password")
        return render_template('Login.html', user_email=user_mail)

    except:
        return "<h3>Please Check your internet connection(speed) & Try Again...</h3>"


class Food(db.Model):

    __tablename__ = "food"

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    #image       = db.Column(db.BLOB, nullable=False)  #if blob is placed data is curropted, Text not working, has to do homework alot...
    #filename    = db.Column(db.Text, nullable=False)
    #extension   = db.Column(db.Text, nullable=False)
    name        = db.Column(db.String(50), nullable=False)
    cost        = db.Column(db.Integer, nullable=False)
    trending_status = db.Column(db.String(10), nullable=False)

class Resort(db.Model):
    __tablename__ = "resort"

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name        = db.Column(db.String(50), nullable=False)
    cost        = db.Column(db.Integer, nullable=False)
    trending_status = db.Column(db.String(10), nullable=False)


@app.route('/home')
def home():
    try:
        user_status=session['login_status']

        if(user_status == "active"):
            fdata = Food.query.all()
            frows =len(fdata)

            rdata = Resort.query.all()
            #rrows = len(rdata)

            return render_template("welcome.html",food_data=fdata,food_rows=frows,email=session['login_email'], resort_data=rdata)
        else:
            flash('Please Login')
            return redirect(url_for('login'))
    except:
            flash('Please Login')
            return redirect(url_for('login'))

@app.route('/food')
def food():
    try:
        user_status=session['login_status']

        if(user_status == "active"):
            fdata = Food.query.all()
            return render_template("Food.html",food_data=fdata)
        else:
            flash('Please Login')
            return redirect(url_for('login'))
    except:
            flash('Please Login')
            return redirect(url_for('login'))

@app.route('/resorts')
def resorts():
    try:
        user_status=session['login_status']

        if(user_status == "active"):
            rdata = Resort.query.all()
            return render_template("Resorts.html",resort_data=rdata)
        else:
            flash('Please Login')
            return redirect(url_for('login'))
    except:
            flash('Please Login')
            return redirect(url_for('login'))

@app.route('/admin')
def admin():
    try:
        user_status=session['login_status']

        if(user_status == "active"):
            return render_template("admin.html")
        else:
            flash('Please Login')
            return redirect(url_for('login'))
    except:
            flash('Please Login')
            return redirect(url_for('login'))

@app.route('/help',methods=['POST','GET'])
def help():
    return redirect(url_for('home'))

@app.route('/cart')
def cart():
    try:
        user_status=session['login_status']

        if(user_status == "active"):
            return render_template("cart.html")
        else:
            flash('Please Login')
            return redirect(url_for('login'))
    except:
            flash('Please Login')
            return redirect(url_for('login'))


@app.route('/logout')
def logout():
    try:
        user_status=session['login_status']

        if(user_status == "active"):
            session['login_status']="inactive"
            return render_template("Logout.html")
        else:
            flash('Please Login')
            return redirect(url_for('login'))
    except:
            flash('Please Login')
            return redirect(url_for('login'))




#@app.route('/addfood')
#def addfood():
#    return render_template("addfood.html")



'''def convertToBinaryData(image):
    #with open(filename, 'rb') as file:
    file = open(image, "rb")
    binaryData = file.read()
    return binaryData '''

@app.route('/addingfood',methods=['POST','GET'])
def addingfood():
    name  = request.form['name']
    cost =  request.form['cost']
    trending_status = request.form['trending_status']
    #image =  request.files['image']
    #image.save(image.filename)

    #filename = secure_filename(image.filename)
    #extension = image.mimetype

    addfood = Food(name=name, cost=cost, trending_status=trending_status) #image=binimage | image=image.read(), filename=filename, extension=extension,


    try:
        db.session.add(addfood)
        db.session.commit()
        #flash('Successfully added !')
        return redirect(url_for('food'))

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error
        #return "<h2>There was a problem while adding to db</h2>"



@app.route('/addingresort',methods=['POST','GET'])
def addingresort():
    name  = request.form['name']
    cost =  request.form['cost']
    trending_status = request.form['trending_status']


    addresort = Resort(name=name, cost=cost, trending_status=trending_status)


    try:
        db.session.add(addresort)
        db.session.commit()
        #flash('Successfully added !')
        return redirect(url_for('resorts'))

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error
        #return "<h2>There was a problem while adding to db</h2>"



@app.route('/<int:id>')
def get_img(id):
    img = Food.query.filter_by(id=id).first()
    if not img:
        return "<h1>No image with that id...</h1>"
    #return "<img src='{{ img.image }}' width='200px' height='200px' alt='image'>"
    #return Response(img.image, mimetype=img.extension)
    #image = b64encode(img.image)
    image = base64.b64encode(img.image)
    return render_template('image.html',data=list,image=image)

@app.route('/download')
def download():
    file_data = Food.query.filter_by(id=1).first()
    return send_file(BytesIO(file_data.image),attachment_filename='test.png',as_attachment=True)

@app.route('/users')
def users():
    try:
        u_data = Signup.query.all()
        no_of_rows =len(u_data)
        return render_template("users_data.html",user_data=u_data,rows=no_of_rows)

    except:
        flash('Something went wrong')
        return redirect(url_for('login'))

@app.route('/delete-user', methods=['POST','GET'])
def delete_user():
    try:
        user_email    = request.form['email_to_del']

        del_email = Signup.query.filter_by(email=user_email).first()
        db.session.delete(del_email)
        db.session.commit()
        flash('Deleted')
        return redirect(url_for('users'))

    except:
        flash('Something went wrong')
        return redirect(url_for('users'))



