from selenium import webdriver
import time
import datetime
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime

engine = create_engine(r'sqlite:///C:\Users\Bogdan\Desktop\\My_Events.db')
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    venue = Column(String)
    date = Column(DateTime)

    def __repr__(self):
        return "<Event(name='%s', venue='%s', date='%s')>" % (self.name, self.venue, self.date)


Base.metadata.create_all(engine)
driver = webdriver.Chrome()

# options = webdriver.ChromeOptions()
# options.add_argument('headless')
# options.add_argument('--no-sandbox')
# driver = webdriver.Chrome(chrome_options=options)

fb_pages = [
    'https://www.facebook.com/pg/Galeria-Elite-Prof-Art-185399108168591',
    'https://www.facebook.com/teatrulevreiesc',
    'https://www.facebook.com/pg/TeatrulMetropolis',
    'https://www.facebook.com/pg/UniversitateaRomanoAmericana',
    'https://www.facebook.com/pg/muzeul.literaturii.romane',
    'https://www.facebook.com/pg/CentruldeTeatruEducational',
    'https://www.facebook.com/TNB.Ro'
    ]


for fb_page in fb_pages:
    driver.get(fb_page + '/events')
    driver.maximize_window()
    time.sleep(3)

    my_element = driver.find_element_by_xpath("//*[contains(text(), 'Past Events')]")
    driver.execute_script("return arguments[0].scrollIntoView();", my_element)
    time.sleep(5)

    elements_containers = driver.find_elements_by_class_name('_24er') #identifies the paragraph containing the each event
    for element_container in elements_containers:

        d = datetime.date.today()
        now = datetime.datetime.combine(d, datetime.datetime.min.time())

        month = element_container.find_element_by_class_name('_5a4-').text
        day = element_container.find_element_by_class_name('_5a4z').text
        hour_support = element_container.find_element_by_css_selector('._4dml.fsm.fwn.fcg').text
        hour = re.search('\d+:\d+\s(AM|PM)', hour_support)
        #TODO add UTC timezone to parsed_date

        if hour:
            parsed_date = datetime.datetime.strptime('{} {} {} {}'.format(month, day, now.year, hour.group(0)), '%b %d %Y %I:%M %p')

        if not hour or parsed_date < now:
            break

        New_Event = Event(name=element_container.find_element_by_class_name(' _50f7').text,
                          venue=driver.find_element_by_class_name('_64-f').text,
                          date=parsed_date)

        session.add(New_Event)
        session.commit()

#TODO close browser
#TODO make headless

for instance in session.query(Event).order_by(Event.id):  #order_by is optional and will order based om given item
    print(instance.name, instance.venue, instance.date)

# my_events = session.query(Event).all()
# print(my_events)


