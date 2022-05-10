import sqlite3 as sql
import logging

from sqlalchemy import null               #import lib for write log
#board setting function
def GetBoardID():
    VMSBoardID = ''
    try:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT DeviceName  FROM mstSetting")
            rows = cur.fetchall()
            VMSBoardID = rows[0][0]
    except:
        con.rollback()
        logging.exception('Got exception on VMSData')
    finally:
        con.close()
        return VMSBoardID
def GetBoardSetting():
    VMSBoardID =[]
    try:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT *  FROM mstSetting")
            rows = cur.fetchall()
            VMSBoardID = rows[0]
            return VMSBoardID
    except:
        con.rollback()
        logging.exception('Got exception on VMSData')
    finally:
        con.close()
        return VMSBoardID
def SetBoardSetting(width,height,Row,chainlength,parralel, brighness):
    VMSBoardID =1
    try:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("UPDATE mstSetting SET Width = ? , Height = ?, [Row] = ?, chain_length = ?, parallel = ?, DefaultBrightness = ?"
                        ,(width,height,Row,chainlength,parralel,brighness))
            con.commit()
            return 1
    except:
        con.rollback()
        logging.exception('Got exception on VMSData')
    finally:
        con.close()
        return 0        
#Image setting function
def ClearAllImage():
    try:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("DELETE  FROM mstImageList")
            con.commit()
    except:
        con.rollback()
        logging.exception('Got exception on VMSData')
    finally:
         con.close()        
def InsertImage(ImageID,ImageContent,DisplayOrder,DisplayInterval):
    try:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO mstImageList ( ImageID, ImageContent, DisplayOrder, DisplayInterval)  VALUES (?,?,?,?)",(ImageID,ImageContent,DisplayOrder,DisplayInterval) )
            con.commit()
            msg = "Record successfully added"
    except:
        con.rollback()
        msg = "error in insert operation"
        logging.exception('Got exception on VMSData')
    finally:
         con.close()
def ClearAllLastDisplayTime():
    try:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("UPDATE mstImageList SET LastDisplayTime = ''" )
            con.commit()
            msg = "Record successfully added"
    except:
        con.rollback()
        msg = "error in insert operation"
        logging.exception('Got exception on VMSData')
    finally:
         con.close()             
def UpdateLastDisplayTime(ImageID,LastDisplayTime):
    try:
        print("UpdateLastDisplayTime =", LastDisplayTime)	
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("UPDATE mstImageList SET LastDisplayTime = ? WHERE ImageID = ?",(LastDisplayTime,ImageID) )
            con.commit()
            msg = "Record successfully added"
    except:
        con.rollback()
        msg = "error in insert operation"
        logging.exception('Got exception on VMSData')
    finally:
         con.close()         
def GetCurrentDisplayingRecord(ImageID):
    VMSBoardID = ''
    try:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT  *  FROM mstImageList where ImageID = '"+str(ImageID)+"'")
            rows = cur.fetchall()
            print(len(rows))
            if  len(rows) == 0 :
                return VMSBoardID      
            else :
                VMSBoardID = rows[0]
    except:
        con.rollback()
        logging.exception('Got exception on VMSData')
    finally:
        con.close()
        return VMSBoardID         
def GetNumberofDisplayingRecord():
    VMSNUM = 0
    try:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT  *  FROM mstImageList")
            rows = cur.fetchall()
            print(len(rows))
            VMSNUM = len(rows)
            return VMSNUM  
    except:
        con.rollback()
        logging.exception('Got exception on VMSData')
    finally:
        con.close()
        return VMSNUM          