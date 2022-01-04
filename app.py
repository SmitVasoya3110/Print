#sudo iptables -I INPUT -p tcp --dport 5000 -j ACCEPT 
#run below command for accepting traffic
import os
import subprocess
from flask import Flask, jsonify, request, session
from flask import *
from flask_restful import Api
from flask_jwt import JWT, jwt_required, current_identity
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from flask_cors import CORS
from flask_mail import Mail, Message
import PyPDF2 as pypdf
from werkzeug.utils import secure_filename
from  werkzeug.security import generate_password_hash, check_password_hash
import threading
from db import mysql
# from flask_mysqldb import MySQL
import time
from datetime import datetime


# importing resources file
from resources.customerResource import *



app=Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'ssmmiitt007@gmail.com'
app.config['MAIL_PASSWORD'] = 'SP@88665'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


app.config['JWT_SECRET_KEY'] = '@#PMRg(|w^yC'  # Change this!
jwt = JWTManager(app)
api = Api(app)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'xeroxdb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
# mysql2 = MySQL(app)
mysql.init_app(app)

@app.route('/') 
def get():
    return jsonify([{'message' : "Please use correct url"}])

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

welcome_message = "Welcome to Online Printing. You have successfully registered with us.\nThank you..."


def A4_BC(num:int):
    if 1<=num <= 3:
        cost = 3
        return cost
    if 3<= num < 30:
        cost = 3 + (num - 3)*0.3
        return cost
    if 30<=num<100:
        cost = (29*0.3) + (num-29)*0.2
        return cost
    if num >= 100:
        cost = (99*0.2) + (num-99)*0.1
        return cost


def A3_BC(num:int):
    if 1<=num <= 3:
        cost = 3
        return cost
    if 3<= num < 30:
        cost = 4 + (num - 3)*0.6
        return cost
    if 30<=num<100:
        cost = (29*0.6) + (num-29)*0.4
        return cost
    if num >= 100:
        cost = (99*0.4) + (num-99)*0.2
        return cost


def A4_C(num:int):
    if 1<=num <= 3:
        cost = 3
        return cost
    if 3<= num < 30:
        cost = 2 + (num - 3)*0.8
        return cost
    if 30<=num<100:
        cost = (29*0.6) + (num-29)*0.6
        return cost
    if num >= 100:
        cost = (99*0.4) + (num-99)*0.
        return cost


def A3_C(num:int):
    if num == 1:
        cost = 3
        return cost
    if 2<= num < 30:
        cost = 3 + (num - 1)*0.3
        return cost
    if 30<=num<100:
        cost = (19*1.6) + (num-29)*1.2
        return cost
    if num >= 100:
        cost = (99*1.2) + (num-99)*0.8
        return cost

@app.route('/multiple-files-upload', methods=['POST'])
def upload_file():
    print("In Upload API")
    # check if the post request has the file part

    size, typ =  request.form.get('docFormat').split('_')

    if 'files[]' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp

    files = request.files.getlist('files[]')

    errors = {}
    success = False

    num_dict = {'numbers': []}
    total_pages = 0
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(file.mimetype)

            if file.mimetype == "application/pdf":
                npath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(npath)
                with open(npath, 'rb') as fpath:
                    read_pdf = pypdf.PdfFileReader(fpath)
                    num_pages = read_pdf.getNumPages()
                    num_dict['numbers'].append({
                        "file_name": filename,
                        "pages":num_pages})
                    print("NUM DICT +++", num_dict)
                    total_pages += num_pages
                # TODO: Page Counter PDF
            if file.mimetype == "image/jpeg" or file.mimetype == "image/png":
                if 'Total Images' in num_dict.keys():
                    num_dict['Total Images'] += 1
                else: num_dict['Total Images'] = 1
                total_pages += 1
                # TODO: image code
            if filename.rsplit(".")[1] == "doc" or filename.rsplit(".")[1] == "docx":
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                source = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                destination = app.config['UPLOAD_FOLDER']
                output = subprocess.run(
                    ["libreoffice", '--headless', '--convert-to', 'pdf', source, '--outdir', destination])
                print(output)
                new_dest = os.path.splitext(destination + f'/{filename}')[0] + ".pdf"
                with open(new_dest, 'rb') as fpath:
                    read_pdf = pypdf.PdfFileReader(fpath)
                    num_pages = read_pdf.getNumPages()
                    num_dict['numbers'].append({
                        "file_name": filename,
                        "pages": num_pages})
                    total_pages += num_pages
                print("On Going")
            success = True
        else:
            errors[file.filename] = 'File type is not allowed'

    num_dict['Total_Pages'] = total_pages
    if size == "A4" and typ.lower() == 'color':
        num_dict['Total_Cost'] = round(A4_C(total_pages), 2)
    if size == "A4" and typ.lower() == 'bw':
        num_dict['Total_Cost'] = round(A4_BC(total_pages), 2)
    if size == "A3" and typ.lower() == 'color':
        num_dict['Total_Cost'] = round(A3_C(total_pages), 2)
    if size == "A3" and typ.lower() == 'bw':
        num_dict['Total_Cost'] = round(A3_BC(total_pages), 2)

    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = jsonify({"errors":errors, "number":num_dict})
        resp.status_code = 200
        return resp
    if success:
        resp = jsonify({'message': 'Files successfully uploaded', "numbers":num_dict})
        resp.status_code = 200
        return resp
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp

def check_email(email):
    qry = "select Email_Id from customer_master where Email_Id = %s"
    # cur = mysql2.connection.cursor()
    con = mysql.connect()
    cursor = con.cursor()
    cursor.execute(qry, (email,))
    result = cursor.fetchone()
    cursor.close()
    con.close()
    if result:
        return 0
    else: return 1

@app.route('/register', methods=['POST'])
def register():
    @copy_current_request_context
    def send_email(receiver):
        msg = Message('Welcome to Print', sender=app.config['MAIL_USERNAME'], recipients=[receiver])
        print(msg)
        msg.body = welcome_message
        mail.send(msg)
    start = time.perf_counter()
    if request.method == 'POST':
        content_type = request.headers.get('Content-Type')
        print(content_type,"content_type")
        if content_type == 'application/json;charset=UTF-8':
            json_data = request.json
            email = json_data.get('Email_Id', 0)
            first_name = json_data.get('FirstName', 0)
            last_name = json_data.get('LastName', 0)
            password = json_data.get('Password', 0)
            mobile = int(json_data.get('Mobile_Number', 0))
            print(email, first_name, last_name, password, mobile)
            if email and first_name and last_name and password and mobile:
                if check_email(email):
                    now = datetime.now()
                    qry = "insert into customer_master (Email_Id, Password, FirstName, LastName, mobile,status,dateAdded) values (%s,%s,%s,%s,%s,1,%s)"
                    values = (email, password, first_name, last_name, mobile,now)
                    # cur = mysql2.connection.cursor()
                    # cur.execute(qry, values)
                    # mysql2.connection.commit()
                    con = mysql.connect()
                    cursor = con.cursor()
                    # cursor.execute(qry, (email,))
                    cursor.execute(qry, values)
                    con.commit()
                    # result = cursor.fetchone()
                    cursor.close()
                    con.close()
                    # t1 = Process(target=send_email, args=(email,))
                    # t1.start()
                    # # t1.join()
                    # send_email(email)
                    thread = threading.Thread(target=send_email, args=(email,))
                    thread.start()
                    return {"Success": "Inserted Successfully"}
                else:
                    return "Email is already in use....try with other"
            else:
                print("Seconds", time.perf_counter() - start)
                return "Values are missing or not correct"

        else:
            return {"message":'Content-Type not supported!'},500

    return "Server is Up and running"

#EmployeMaster resources
api.add_resource(customer,'/Customer')
api.add_resource(CustomerLogin,'/CustomerLogin')
api.add_resource(RefreshToken,'/RefreshToken')




if __name__ == "__main__":
    app.run(host = "0.0.0.0" ,port=5025, debug=True, threaded=True)



