from django.db.utils import IntegrityError
from transferguideapp.models import InternalCourse
import requests
import queue
import threading
import time

url = "https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearchOptions?institution=UVA01"

sr = requests.get(url, timeout=15).json()
subjects = [] 
for i in range(len(sr['subjects'])):
    curr_subject = sr['subjects'][i]['subject']
    if curr_subject not in subjects:
        subjects.append(curr_subject)

url = 'https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01'
page = '&page='
subject = '&subject='


def get_json(s):
    i = 0
    r = [{}]
    while r != []:
        i += 1
        print(url + subject + s + page + str(i))
        try:
            r = requests.get(url + subject + s + page + str(i), timeout=30).json()
        except Exception as error:
            print(f"timeout error. probably caused by network. small quantity of classes may not have been processed.")
            i -= 1
            continue
        #print(r)
        queue_lock.acquire()
        json_queue.put(r)
        queue_lock.release()
    else:
        i = 0

exitFlag = 0
def process():
    while not exitFlag:
        queue_lock.acquire()
        if not json_queue.empty():
            data = json_queue.get()
            queue_lock.release()
            for c in data:
                id = c['crse_id']
                mnemonic = c['subject']
                course_number = c['catalog_nbr']
                course_name = c['descr']
                try:
                    InternalCourse.objects.update_or_create(id=id,mnemonic=mnemonic, course_number=course_number, course_name=course_name)
                except IntegrityError:
                    continue
        else: 
            queue_lock.release()
        time.sleep(1)

def request_fact(threadName, q):
    while not exitFlag:
        course_lock.acquire()
        if not q.empty():
            data = q.get()
            course_lock.release()
            get_json(data)
        else:
            course_lock.release()
        time.sleep(1)


class requestThread (threading.Thread):
   def __init__(self, threadID, name, q):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.q = q
   def run(self):
      print ("Starting " + self.name)
      request_fact(self.name, self.q)
      print ("Exiting " + self.name)

class dataThread (threading.Thread):
   def __init__(self, threadID, name, q):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.q = q
   def run(self):
      print ("Starting " + self.name)
      process()
      print ("Exiting " + self.name)

course_queue = queue.Queue(300)
for c in subjects:
    course_queue.put(c)
course_lock = threading.Lock()
json_queue = queue.Queue()
queue_lock = threading.Lock()

json1 = requestThread(1, "request1", course_queue)
json2 = requestThread(2, "request2", course_queue)
json3 = requestThread(3, "request3", course_queue)
json1.start()
json2.start()
json3.start()
json4 = requestThread(4, "request4", course_queue)
json5 = requestThread(5, "request5", course_queue)
json6 = requestThread(6, "request6", course_queue)
json4.start()
json5.start()
json6.start()
json7 = requestThread(7, "request7", course_queue)
json8 = requestThread(8, "request8", course_queue)
json9 = requestThread(9, "request9", course_queue)
json7.start()
json8.start()
json9.start()
data = dataThread(0, "data", json_queue)
data.start()
