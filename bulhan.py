#! /usr/bin/python

'''

Author : Khurram Naseem
Date: Oct-03-2017

Description:

What?: List of user define functions using boto3. boto3 is python library, which help programmers to access AWS resources and get things done. 
for e.g. you want to know any thing (class, disk size, state, version) about any AWS service like EC2, S3, RDS. you can use boto3 library and get information about service or even create or change them programmatically. 

Why?:  Not every time you need to login to AWS console and go to particular service web page and get things done some time we need to handle things programmatically like if we need automation. 

How?:  I used these boto3 functions in my actual working scripts, these are handy functions to perform various tasks on AWS RDS and on some other services. Please use these functions at your own risk esp. when using in production environment, I've put a small description before every function so you will get an idea what is the purpose of these functions. While using these functions in your code please put proper logic to handle failure in some case it might fail the whole functionality for e.g. you are promoting read replica as master and before it is available you accidentally redirect traffic to it.

'''

import boto3
import datetime 
import pymysql
import time



default_rr_instance_class = '' # for e.g. 'db.t2.micro'


aws_key     = ''  #<add key here>
aws_secret  = ''  #<add secret here>
aws_region = '' # for e.g. 'eu-west-1'

rds = boto3.client('rds',aws_access_key_id=aws_key,aws_secret_access_key=aws_secret,region_name=aws_region)


#Upgrade database version. please do some homework.

def upgrade_version(dbname,dbversion):
	response = rds.modify_db_instance(ApplyImmediately=True, DBInstanceIdentifier=dbname,EngineVersion=dbversion)

#Check if backup option is enable on db or not.
def check_db_backup(dbname):
	#if backup option is enable then we return true otherwise false
	response        = rds.describe_db_instances(DBInstanceIdentifier=dbname)
	db_instances 	= response['DBInstances'] 
	db_instance 	= db_instances[0]
	
	#dbidentifier 	= db_instance['DBInstanceIdentifier']
	backup 			= db_instance['BackupRetentionPeriod']
	#status 			= db_instance['DBInstanceStatus']
	
	if backup > 0:
   		return True
	else:
   		return False

#Enable backup on RDS instance.
def enable_backup(dbname,backupdays):
	response = rds.modify_db_instance(ApplyImmediately=True, DBInstanceIdentifier=dbname,BackupRetentionPeriod=backupdays)


#if you want to create read replica,  make sure backup should be enabled on source RDS (this is a must), please use above function to check or enable this.
def create_read_replica(s_dbname,rr_db_name,instance_class=default_rr_instance_class):
	response = response = rds.create_db_instance_read_replica(DBInstanceIdentifier=rr_db_name,SourceDBInstanceIdentifier=s_dbname,DBInstanceClass=instance_class)


#Make Database readonly, there are many way where you can stop write traffice comes to particualr db.

# You can change database parameter value. 

def make_db_readonly(parameter_gr_name):
	response = rds.modify_db_parameter_group(DBParameterGroupName=parameter_gr_name,Parameters=[{'ApplyMethod':'immediate','ParameterName':'read_only','ParameterValue':'1'}])


# Change database port (db will reboot).

def change_port(dbname,newdbport):
	response        	= rds.describe_db_instances(DBInstanceIdentifier=dbname)

	db_instances 		= response['DBInstances'] 
	db_instance 		= db_instances[0]
	endpoint 			= db_instance['Endpoint']
	olddbport 			= endpoint['Port']
	
	response = rds.modify_db_instance(ApplyImmediately=True, DBInstanceIdentifier=dbname,DBPortNumber=newdbport)
	
	status = db_instance['DBInstanceStatus']
	

	
	while (status != "available" or olddbport != newdbport):
		
		time.sleep(1)
		response2 = rds.describe_db_instances(DBInstanceIdentifier=dbname)
		db_instances2 = response2['DBInstances']
		db_instance2 = db_instances2[0]
		endpoint2 = db_instance2['Endpoint']
		olddbport = endpoint2['Port']
		status = db_instance2['DBInstanceStatus']
	print "Port Changed Successfully! new is :"	+ str(olddbport)
	return olddbport
		
#Promote Read Replica as new master, please provide backup retention days.

def promote_read_replica(dbname, backup_days=1):
	response = rds.promote_read_replica(DBInstanceIdentifier=dbname,BackupRetentionPeriod=backup_days)
	responses = rds.describe_db_instances(DBInstanceIdentifier=dbname)
	time.sleep(10)
	db_instances = responses['DBInstances'] 
	db_instance 	= db_instances[0]
	status = db_instance['DBInstanceStatus']
	
	a = True
	while (a):
		
		time.sleep(10)
		responses = rds.describe_db_instances(DBInstanceIdentifier=dbname)
		db_instances = responses['DBInstances'] 
		db_instance 	= db_instances[0]
		status = db_instance['DBInstanceStatus']
		
		if (status == "available"):
			
			a = False
    	print "Db promoted !"

#Get Route53 value against your provided entry , sometime we need this te redirect traffic to another read replica.

def route53_value(hostid,entryname)
r53 = boto3.client('route53',aws_access_key_id=aws_key,aws_secret_access_key=aws_secret,region_name=aws_region)


r = r53.list_resource_record_sets(HostedZoneId=hostid)

for i in r['ResourceRecordSets']:
  if i['Type'] == 'CNAME' and i['Name'] == entryname :
    
    d = i['ResourceRecords']
    
for a in d:
    return str( a['Value'] )
