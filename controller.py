from db import get_db

def get_by_id(id,date,token):
    db = get_db()
    cursor = db.cursor()
    statement = "SELECT * from tide WHERE station_id = ? and DATE(date_local) >= ?;"
    cursor.execute(statement, [id,date])
    if token == "6b6a1f8f5a75b760b91a414d76c6b831774dd52802a76f41":
        return cursor.fetchall()
    else:
        return {"Error":"Invalid Request"}

def get_by_country():
    db = get_db()
    cursor = db.cursor()
    statement = "SELECT * from country_mapper;"
    cursor.execute(statement)
    return cursor.fetchall()

def get_countries_with_updates():
    db = get_db()
    cursor = db.cursor()
    statement = "SELECT * from country_mapper WHERE has_updates = 1;"
    cursor.execute(statement)
    return cursor.fetchall()

def get_by_id_tonga(id,date,token):
    db = get_db()
    cursor = db.cursor()
    statement = "SELECT * from tide WHERE station_id IN ('INT_TP025','INT_TP053') and DATE(date_local) >= ?;"
    cursor.execute(statement, [date])
    if token == "6b6a1f8f5a75b760b91a414d76c6b831774dd52802a76f41@!a":
        return cursor.fetchall()
    else:
        return {"Error":"Invalid Request"}

def get_by_id_vanuatu(id,date,token):
    db = get_db()
    cursor = db.cursor()
    statement = "SELECT * from tide WHERE station_id IN ('INT_TP049','INT_TP027') and DATE(date_local) >= ?;"
    cursor.execute(statement, [date])
    if token == "6b6a1f8f5a75b760b91a414d76c6b831774dd52802a76f41@!a3":
        return cursor.fetchall()
    else:
        return {"Error":"Invalid Request"}

def get_by_id_all(id,date,enddate,token):
    db = get_db()
    cursor = db.cursor()
    statement = "SELECT * from tide WHERE station_id = ? and DATE(date_local) >= ? and DATE(date_local) <= ?;"
    cursor.execute(statement, [id,date,enddate])
    if token == "6b6a1f8f5a75b760b91a414d76c6b831774dd52802a76f41":
        return cursor.fetchall()
    else:
        return {"Error":"Invalid Request"}

def get_by_id_samoa(id,date,token):
    db = get_db()
    cursor = db.cursor()
    statement = "SELECT * from tide WHERE station_id IN ('INT_TP022') and DATE(date_local) >= ?;"
    cursor.execute(statement, [date])
    if token == "6b6a1f8f5a75b760b91a414d762626c6b831774dd52802a76f41@!a":
        return cursor.fetchall()
    else:
        return {"Error":"Invalid Request"}

def get_by_id_niue(id,date,token):
    db = get_db()
    cursor = db.cursor()
    statement = "SELECT * from tide WHERE station_id IN ('INT_TP024') and DATE(date_local) >= ?;"
    cursor.execute(statement, [date])
    if token == "6b6a1f8f5a75b760b91a414d762626c6b831774dd52802a76f41@!an":
        return cursor.fetchall()
    else:
        return {"Error":"Invalid Request"}

def get_by_id_solomon(id,date,token):
    db = get_db()
    cursor = db.cursor()
    statement = "SELECT * from tide WHERE station_id IN ('INT_TP023','INT_TP050','INT_TP051') and DATE(date_local) >= ?;"
    cursor.execute(statement, [date])
    if token == "6b6a1f8f5a75b760b91a414d762626c6b831774dd52802a76f41@!sb7":
        return cursor.fetchall()
    else:
        return {"Error":"Invalid Request"}

def get_tide_predictions(station_no, start, end):
    db = get_db()
    cursor = db.cursor()
    statement = (
        "SELECT utc, height FROM tide_predictions "
        "WHERE station_no = ? AND utc >= ? AND utc <= ? "
        "ORDER BY utc;"
    )
    cursor.execute(statement, [station_no, start, end])
    rows = cursor.fetchall()
    return [{"utc": r[0], "height": r[1]} for r in rows]
