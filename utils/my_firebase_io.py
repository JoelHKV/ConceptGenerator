import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


def init_firebase():  
    cred = credentials.Certificate("C:\key_storage\koira-363317-150430c677f4.json")
    firebase_admin.initialize_app(cred)
    firestore_db = firestore.client()
    return firestore_db
    
def read_firebase(firestore_db, this_collection, this_document):      
    tempdata = firestore_db.collection(this_collection).document(this_document).get()
    if tempdata:
        tempdata_dict = tempdata.to_dict()
        print(this_collection +  this_document +  "exists - reading content") 
    else:
        tempdata_dict = {}
        print(this_collection +  this_document +  "does not exists - start with empty dict")
   
    return tempdata_dict

def write_firebase(firestore_db, this_collection, this_document, this_dict): 
    firestore_db.collection(this_collection).document(this_document).set(this_dict)
    print(this_collection +  this_document +  "succesfully written")
