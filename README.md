## Technology Stack
# Frontend
     ReactJS: A JavaScript library for building user interfaces, used for frontend development.
# Backend
     AWS Lambda (Python Flask): Serverless computing service for running backend code with Flask, adapted to the serverless environment using serverless-wsgi.
# Database
     DynamoDB: A NoSQL database service used for storing and retrieving user and session data.
# Email Notifications
     SMTP: Handled by smtplib for sending email-based notifications.
Storage
# AWS S3:
     Utilized for storing documents such as student and counselor files.
# Payment Gateway
     Integrated Payment Gateway: Used for handling payments related to counselor selection.
## Python Dependencies
# Flask: 
     A lightweight web framework for handling HTTP requests and responses, powering the backend API.
# serverless-wsgi:
     A utility for deploying Flask applications on AWS Lambda, integrating with AWS API Gateway.
# boto3:
     The AWS SDK for Python, enabling interaction with AWS services including DynamoDB and S3.
# flask_cors:
     Provides Cross-Origin Resource Sharing (CORS) support for secure communication between the ReactJS frontend and Flask backend.
# requests: 
     A Python library for making HTTP requests to interact with external services (e.g., third-party API integrations).
## Flows
# Super Admin Flow
Login: Super Admin logs in with credentials (email and password).
Dashboard:
View personal information, counselor information, and student information.
Calendar module shows meeting links between:
Student and Counselor
Counselor and Admin
Admin and Super Admin
Transaction Module:
Inflow: View student payments for counselor selection.
Outflow: View payments made to counselors.
Profile Management:
Create Admin profiles and send credentials via email (SMTP).
Approve counselor profiles and send notifications via email (SMTP).
Document Access:
View and download student and counselor documents.
Reports and Notifications:
View, download reports, and notify students of counselor feedback via email and system notifications.
# Admin Flow
Profile Creation:
Super Admin creates the Admin profile and sends credentials via email (SMTP).
Login:
Admin logs in and views personal information on their dashboard.
Dashboard:
Calendar shows meeting links between:
Admin and Super Admin
Counselor and Admin
Includes:
Counselors assigned to Admin
Student feedback from counselors
Profile Management:
Create counselor profiles and send credentials to counselors via email (SMTP).
Permission to view student documents.
# Counselor Flow
Profile Approval:
Admin creates the Counselor profile, and Super Admin approves the profile.
Notifications:
Counselor receives email notifications after profile approval.
Counselor Activities:
View the profile of students who selected them (cannot download documents).
Schedule meetings with students.
Assign essays.
Provide feedback after each meeting.
Feedback Notification:
Feedback is notified to Admin and Super Admin via email (SMTP).
# Student Flow
register with their basic details
Counselor Selection:
Students select a counselor and make the payment.
Notifications:
After successful payment, both the student and the counselor are notified via email (SMTP).
Receive meeting schedules from counselors.
Receive feedback notifications via email.