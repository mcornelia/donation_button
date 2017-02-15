#!/usr/bin/env python

# lambda_function version 0.1
# 15.FEB.2017
# 
# Original idea & script by Nathan Pryor https://github.com/nathanpryor
# And this version forked by Mike Cornelia <mike.cornelia@gmail.com>
# 

# This is a simple python script that sends $$$ to the ACLU
# It runs on Amazon's AWS Lambda service 
# See more here: https://aws.amazon.com/lambda/
# This script also uses Amazon's AWS SNS service to send confirmations via text message
# see https://aws.amazon.com/sns/ for setup and details


# Load modules
# Modules are uploaded to Lambda vi a zip file called a 'Python deployment package'
# see http://amzn.to/2lhEWrG for how to create and upload this

import mechanize
import boto3 # AWS module - I believe this is loaded by default in AWS Lambda?
import json
import os

# User variables
# Replace with your information

first_name='Jane' 
last_name='Doe'
e_mail='janedoe+IoTbutton@gmail.com'
street_address='123 Main ST'
city='Some City'
state_code='44' # see http://bit.ly/2l7I5HP
zip_code='10101'

phone_number='+15551234567' # for Amazon SNS (SMS) text confirmation,
# use +1 before area code and number in the US

# Credit card info (need to figure out how to hash this?)

Billing_country_code="840" # see http://bit.ly/2l7I5HP, 840 = United States
CC_number="3xxxxxxxxx6994" # Suggest a pre-loaded gift card just to be safe. 
CC_Exp_MM="7" # No leading zeros please. i.e. July==7
CC_Exp_YYYY="2024"
CC_cvv="123" 

# from base64 import b64decode
# CC_number=boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ['CC_number']))['Plaintext']
# CC_expiration_month=boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ['CC_expiration_month']))['Plaintext']
# CC_expiration_year=boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ['CC_expiration_year']))['Plaintext']
# CC_CSC=boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ['CC_CSC']))['Plaintext']

donation_amount="5" # $5 is the minimum 

sns=boto3.client('sns') # SNS is Amazon's method for SMS text messaging 

br = mechanize.Browser(factory=mechanize.RobustFactory()) 

def lambda_handler(event, context):
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    br.open("https://action.aclu.org/donate-aclu")
    br.select_form(nr=3)

    br.form['submitted[donation][aclu_recurring]']=0 
    br.form['submitted[donation][amount]']=["other"]
    br.form['submitted[donation][other_amount]']=donation_amount

    br.form['submitted[donor_information][first_name]']=first_name
    br.form['submitted[donor_information][last_name]']=last_name
    br.form['submitted[donor_information][email]']=e_mail

    br.form['submitted[billing_information][address]']=street_address
    br.form['submitted[billing_information][city]']=city
    br.form['submitted[billing_information][state]']=[state_code] 
    br.form['submitted[billing_information][zip]']=zip_code
    br.form['submitted[billing_information][country]']=[Billing_country_code] 

    br.form['submitted[credit_card_information][card_number]']=CC_number
    br.form['submitted[credit_card_information][expiration_date][card_expiration_month]']=[CC_Exp_MM]
    br.form['submitted[credit_card_information][expiration_date][card_expiration_year]']=[CC_Exp_YYYY]
    br.form['submitted[credit_card_information][card_cvv]']=CC_cvv

    br.form['submitted[credit_card_information][fight_for_freedom][1]']=0
    br.form['submitted[credit_card_information][profile_may_we_share_your_info][1]']=0

# Submit form and send text message

    response = br.submit()
    if "Thank You" in response.read():
         message = '$5 donated to the ACLU!'
    else:
         message = 'Error: no donation occurred'
    sns.publish(PhoneNumber=phone_number, Message=message)
