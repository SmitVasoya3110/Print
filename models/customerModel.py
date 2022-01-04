import sys
# insert at 1, 0 is the script path (or '' in REPL)
#sys.path.insert(1, '/home/infozium/Documents/ERP/ERP_API')
from flask_jwt_extended import ( create_access_token )
from db import mysql
import pymysql
from flask import jsonify
from flask import flash, request
from datetime import datetime
import math
from pytz import timezone
import time



class CustomerModel:

    @classmethod
    def CustomerLogin(self, args):
        try:
            con = mysql.connect()
            cursor = con.cursor(pymysql.cursors.DictCursor)
            sql = """SELECT *
                     FROM `Customer_Master`
                     where Email_Id='"""+str(args['Email_Id'])+"""' and Password='"""+str(args['Password'])+"""' and status='1'
                  """
            # data = (Email_Id, password)
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            con.close()
            if(len(rows) > 0):
                for i in rows:
                    dic1 = {}
                    dic2 = {}
                    dic3 = {}

                    dic1["access_token"] = create_access_token(identity=i['Email_Id'])
                    # dic1["refresh_token"] = create_refresh_token(identity=i[3])

                    dic2["role"] = "Customer"
                    dic2["uuid"] = i['id']

                    dic3["displayName"] = i['FirstName']
                    dic3["email"] = i['Email_Id']
                    dic3["photoURL"] = ""

                    dic2["data"] = dic3

                    dic1["user"] = dic2

                # res = jsonify(dic1)
                # res.status_code = 200
                return dic1

                return res

            return {"message":"Enter Valid Email_Id or Password"},401

        except Exception as e:
            print(e)
            return e
    @classmethod
    def getCustomer(self, args): #search and filter Customer -- MYSQL Table name: Customer_Master
        try:
            if(int(args['row_per_column'])<=0 or int(args['page_number'])<0):
                return {"message":"Value cannot be less than zero"},200
            sql = "SELECT * FROM Customer_Master"
            sql3 = "select count(*) as count from Customer_Master"
            where = ""
            pagination = " LIMIT "+str(args['row_per_column'])+" OFFSET "+str(int(args['page_number'])*int(args['row_per_column']))+";"
            for key, value in args.items():
                if value==None or value=="none" or key =='row_per_column' or key=='page_number':
                    pass              
                else:
                    where += " and " + key + " LIKE '%" + str(value)+"%'"
            if len(where)>1:
                sql+=" WHERE " + where[5:] + " and status=1 order by id desc"
                sql3+=" WHERE " + where[5:] + " and status=1 order by id desc"
            else:
                sql+=" WHERE status=1 order by id desc"
                sql3+=" WHERE status=1 order by id desc"
            sql+=pagination
            print("------------------------------------------",sql)
            try:
                conn = mysql.connect()
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(sql)
                data = cursor.fetchall()
                cursor.close()
                conn.close()
                dic={}
                lst=[]
                conn = mysql.connect()              
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(sql3)               
                data3 = cursor.fetchone()
                cursor.close()
                conn.close()
                total_count=data3["count"]
                total_page_available = math.ceil(total_count/args['row_per_column'])
                print(data)
                if args['page_number']>total_page_available:             
                    res = jsonify({"message": "pages exceed"})
                    res.status_code = 200
                    return res
                for i in data:                                      
                    i['total']=total_count
                    i['total_page_available']=total_page_available
                    i['dateAdded']=str(i['dateAdded'])
                    lst.append(i)
                if len(lst)<=0:
                    res = jsonify([])
                    res.status_code = 200
                    return res
                res = jsonify(lst)
                res.status_code = 200
                return res
            except Exception as e:
                cursor.close()
                conn.close()
                return {[]},400
        except Exception as e:
            res = jsonify({"message":"There was some problem "+ e})
            res.status_code = 400
            print(e)
            return res

    @classmethod
    def getCustomerById(self,id): # search Customer by id -- MYSQL table : Customer_Master
        try:
            sql = "SELECT * FROM Customer_Master where status=1 and id=%s"
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            temp=id
            cursor.execute(sql,temp)
            data = cursor.fetchall()
            cursor.close()
            conn.close()
            dic={}
            lst=[]           
            for i in data:
                i['dateAdded']=str(i['dateAdded'])
                lst.append(i)
            if len(lst)<=0:
                return self.not_found()
            res = jsonify(lst)
            res.status_code = 200
            return res
        except Exception as e:
            cursor.close()
            conn.close()
            return {[]},500

    @classmethod
    def getCustomerByDesignation(self,id): # search Customer by designatrion -- MYSQL table : Customer_Master
        try:
            sql = "SELECT id,CustomerName FROM `Customer_Master` where status=1 and Designation=%s"
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            temp=id
            cursor.execute(sql,temp)
            data = cursor.fetchall()
            cursor.close()
            conn.close()
            dic={}
            lst=[]     
            # i['dateAdded']=str(i['dateAdded'])
            for i in data:
                lst.append(i)
            if len(lst)<=0:
                return self.not_found()
            res = jsonify(lst)
            res.status_code = 200
            return res
        except Exception as e:
            cursor.close()
            conn.close()
            return {[]},500

    @classmethod
    def addCustomer(self, args): # add new Customer -- MYSQL table : Customer_Master
        try:
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            status=1
            sql = """INSERT INTO `Customer_Master` (`FirstName`, `LastName`, `Email_Id`, `Password`, `status`, `dateAdded`)
                     VALUES (%s,%s,%s,%s,%s,%s);"""
            data = (args['FirstName'],args['LastName'],args['Email_Id'],args['Password'],status,dt_string)
            print("SQL QUERY AND DATA ",sql,data)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql,data)
            conn.commit()
            cursor.close()
            conn.close()
            resp = jsonify({'message':'Customer Is Added Successfully'})
            resp.status_code = 200
            return resp
        except Exception as e:
            cursor.close()
            conn.close()
            print(e)
            return {[]},400

    @classmethod
    def deleteCustomer(self, args): #Shift soft delete
        try:
            id = args["id"]
            id = tuple(args["id"])
            print("tuple length",len(id))
            if(len(id)==1):
                id=str(id).replace(',','')
                print("length if ",id)
            sql = "update Customer_Master set status=0 WHERE id in " + str(id)
            print(sql)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            conn.close()
            resp = jsonify({'message':'Customer is Deleted Successfully'})
            resp.status_code = 200
            return resp
        except Exception as e:
            cursor.close()
            conn.close()
            return  {[]},400

    # @classmethod
    # def deleteShift(self, args): #Shift soft delete
    #     try:
    #         id = args["id"]
    #         res = self.isShiftDataExist(id)
    #         print("res",res)
    #         if not res:
    #             return {"message": "shift Data not found"}, 400
    #         else:
    #             sql = "update shift_Master set status=0 WHERE id = " + str(id)
    #             print(sql)
    #             conn = mysql.connect()
    #             cursor = conn.cursor()
    #             cursor.execute(sql)
    #             conn.commit()
    #             cursor.close()
    #             conn.close()
    #             resp = jsonify({'message':'Shift is Deleted Successfully'})
    #             resp.status_code = 200
    #             return resp
    #     except Exception as e:
    #         cursor.close()
    #         conn.close()
    #         return  {[]},400

#     @classmethod
#     def deleteMachineById(self, args): #machine hard delete
#         try:
#             id = args["mId"]
#             res = self.isMachineDataExist(id)
#             if not res:
#                 return {"message": "machine Data not found"}, 400
#             sql = "DELETE FROM machine_Master WHERE mId = " + str(id)
#             conn = mysql.connect()
#             cursor = conn.cursor()
#             cursor.execute(sql)
#             conn.commit()
#             cursor.close()
#             conn.close()
#             resp = jsonify({'message':'Machine is deleted successfully'})
#             resp.status_code = 200
#             return resp
#         except Exception as e:
#             cursor.close()
#             conn.close()
#             return  {[]},400

    @classmethod
    def updateCustomer(self, args):
        try:
            import datetime
            id = args["id"]
            res = self.isCustomerDataExist(id)
            if not res:
                message = {
                'status': 404,
                'message': 'error: data with given id is not found ',
                }
                res = jsonify([message])
                res.status_code = 404
                return res    
            sql = "UPDATE Customer_Master SET "
            SET = ""
            for key, val in args.items():
                if val == None:
                    continue
                if key != "id":
                    SET += str(key) + " = '" + str(val) + "'" + ','
            if(len(SET)) > 0:
                sql += SET[:-1] + " WHERE id = " + str(args["id"]) + ";"
                print(sql)
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.execute(sql)
                conn.commit()
                cursor.close()
                conn.close()
                print(sql)
                resp = jsonify({'message':'Customer is updated successfully'})
                resp.status_code = 200
                return resp
            else:
                resp = jsonify({'message':'please enter fields to update'})
                resp.status_code = 200
                return resp
        except Exception as e:
            cursor.close()
            conn.close()
            return {"message": "There was some problem"}, 500

    @classmethod
    def isCustomerDataExist(self, id): #to check if machine is available or not 
        try:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sql = "select count(*) as count from Customer_Master where id = %s and status=1"                            
            val = (id)
            cursor.execute(sql, val)
            data = cursor.fetchone()
            print("1",data)
            dataCount=data['count']
            if dataCount > 0:
                cursor.close()
                conn.close()
                return True
            cursor.close()
            conn.close()
            return False
        except Exception as e:
            cursor.close()
            conn.close()
            return False

    
    @classmethod    
    def not_found(self,error=None):
        message = {
            'status': 404,
            'message': 'There is no record: ' + request.url,
        }
        res = jsonify([message])
        res.status_code = 404
        return res                    