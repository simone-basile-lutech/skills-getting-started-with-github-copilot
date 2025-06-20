"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Connessione a MongoDB locale
client = MongoClient("mongodb://localhost:27017/")
db = client["school"]
activities_collection = db["activities"]


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    # Recupera tutte le attività dal database e restituisce come dict
    activities = {}
    for doc in activities_collection.find():
        name = doc["_id"]
        activities[name] = {
            "description": doc["description"],
            "schedule": doc["schedule"],
            "max_participants": doc["max_participants"],
            "participants": doc["participants"]
        }
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    doc = activities_collection.find_one({"_id": activity_name})
    if not doc:
        raise HTTPException(status_code=404, detail="Activity not found")
    if email in doc["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up")
    # Aggiorna la lista dei partecipanti
    result = activities_collection.update_one(
        {"_id": activity_name},
        {"$push": {"participants": email}}
    )
    return {"message": f"Signed up {email} for {activity_name}"}


@app.post("/activities/{activity_name}/unregister")
def unregister_for_activity(activity_name: str, email: str):
    doc = activities_collection.find_one({"_id": activity_name})
    if not doc:
        raise HTTPException(status_code=404, detail="Activity not found")
    if email not in doc["participants"]:
        raise HTTPException(status_code=400, detail="Student not registered")
    activities_collection.update_one(
        {"_id": activity_name},
        {"$pull": {"participants": email}}
    )
    return {"message": f"Removed {email} from {activity_name}"}
