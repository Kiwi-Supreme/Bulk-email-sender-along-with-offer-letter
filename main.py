from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd
import json
import os
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def load_email_list():
    df = pd.read_excel("email_list.xlsx")
    return df.to_dict(orient="records")

@app.post("/send-emails")
async def send_bulk_emails():
    email_list = load_email_list()
    for person in email_list:
        personalized_message = f"""
Dear {person['Name']},

Congratulations!!

We are delighted to have you on board with us.

Role: {person['Role']}
Offer Amount: {person['Offer_amount']}
Start Date: {person['Starting_date']}
Location: {person['Location']}

Regards,
HR Team
"""

        payload = {
            "Email": person["Email"],
            "Name": person["Name"],
            "Role": person["Role"],
            "Offer_amount": person["Offer_amount"],
            "Starting_date": person["Starting_date"],
            "Location": person["Location"],
            "message": personalized_message
        }

        producer.send("offer_topic", value=payload)
    producer.flush()
    return JSONResponse({"status": "Emails queued successfully"})
