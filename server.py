from app import (
    app,
    db,
    Base,
    Customer,
    Service_Ticket,
    Mechanic,
    service_mechanics,  
)

@app.route("/members", methods=["GET"])
def get_members():
    return {"message": "Members endpoint works!"}
