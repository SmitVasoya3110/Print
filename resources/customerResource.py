import sys
# insert at 1, 0 is the script path (or '' in REPL)
# sys.path.insert(1, '/home/infozium/Documents/ERP/ERP_API')

from models import customerModel
from flask import Flask, jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import ( jwt_required, create_access_token,get_jwt_identity )

class CustomerLogin(Resource):
    def post(self): #add shift
        parser = reqparse.RequestParser()
        parser.add_argument('Email_Id',type=str,required=True,help="Email_Id is required")
        parser.add_argument('Password',type=str,required=True,help="Password is required")
        args = parser.parse_args()
        data=customerModel.CustomerModel.CustomerLogin(args)
        if data:
            return data
        else:
            return {"message":"There is some problem"},500

class RefreshToken(Resource):

    @jwt_required
    def post(self):
        # retrive the user's identity from the refresh token using a Flask-JWT-Extended built-in method
        current_user = get_jwt_identity()
        # return a non-fresh token for the user
        new_token = create_access_token(identity=current_user)
        return {'access_token': new_token}, 200


class customer(Resource):
    def get(self): #search and filter shift
            parser = reqparse.RequestParser()
            parser2=reqparse.RequestParser()
            parser3=reqparse.RequestParser()
            parser3.add_argument('masterEmpDesignation',type=str,default="none")
            parser.add_argument('id',type=str,default="none")
            parser2.add_argument('masterEmpId',type=str,default="none")
            parser.add_argument('CustomerName',type=str,default="none")
            parser.add_argument('Designation',type=str,default="none")
            parser.add_argument('RoleType',type=str,default="none")
            parser.add_argument('row_per_column',type=int,default=10)
            parser.add_argument('page_number',type=int,default=0)
            args = parser.parse_args()
            args2 = parser2.parse_args()
            args3 = parser3.parse_args()
            if args2["masterEmpId"]!= 'none':
                id = args2["masterEmpId"]
                data=customerModel.CustomerModel.getCustomerById(id)
            elif args3["masterEmpDesignation"]!= 'none':
                id = args3["masterEmpDesignation"]
                data=customerModel.CustomerModel.getCustomerByDesignation(id)
            else:
                data=customerModel.CustomerModel.getCustomer(args) 
            if data.status_code == 400 :
                return {'message':'No data found'},400
            return data


    def post(self): #add shift
        parser = reqparse.RequestParser()
        parser.add_argument('FirstName',type=str,required=True,help="FirstName is required")
        parser.add_argument('LastName',type=str,required=True,help="LastName is required")
        parser.add_argument('Email_Id',type=str,required=True,help="Email_Id is required")
        parser.add_argument('Password',type=str,required=True,help="Password is required")
        
        args = parser.parse_args()
        data=customerModel.CustomerModel.addCustomer(args) 
        if data.status_code == 400 :
            return {'message':'No data found'},400
        return data


    def delete(self): #delete shift
        parser = reqparse.RequestParser()
        # parser.add_argument('id',type=str,required=True,help="shift id is required")
        parser.add_argument('id',action='append',required=True,help="id is required")
        args = parser.parse_args()
        data=customerModel.CustomerModel.deleteCustomer(args) 
        if data.status_code == 400 :
            return {'message':'No data found'},400
        return data

    def put(self): #add shift
        parser = reqparse.RequestParser()
        parser.add_argument('id',type=str,required=True,help="id is required")
        parser.add_argument('CustomerName',type=str)
        parser.add_argument('Designation',type=str)
        parser.add_argument('RoleType',type=str)
        parser.add_argument('UserName',type=str)
        parser.add_argument('Password',type=str)

        args = parser.parse_args()
        data=customerModel.CustomerModel.updateCustomer(args) 
        if data.status_code == 400 :
            return {'message':'No data found'},400
        return data