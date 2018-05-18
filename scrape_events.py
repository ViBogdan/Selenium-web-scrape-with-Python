import datetime
import re
import time

from dateutil.parser import parse
from dateutil.tz import tzutc
from selenium import webdriver
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import config

engine = create_engine(config.db_connection_string)
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
        return "<Event(name='%s', venue='%s', date='%s')>" % (
            self.name, self.venue, self.date
        )


Base.metadata.create_all(engine)
driver = webdriver.Chrome()

# TODO make headless
# options = webdriver.ChromeOptions()
# options.add_argument('headless')
# options.add_argument('--no-sandbox')
# driver = webdriver.Chrome(chrome_options=options)

for fb_page in config.fb_pages:
    driver.get(fb_page + '/events')
    driver.maximize_window()
    time.sleep(3)

    past_events = driver.find_element_by_xpath("//*[contains(text(), 'Past Events') or contains(text(), 'Past events')]")
    driver.execute_script("return arguments[0].scrollIntoView();", past_events)
    time.sleep(5)

    elements_containers = driver.find_elements_by_class_name('_24er') #identifies the paragraph containing the each event
    for element_container in elements_containers:

        # Create a datetime for today at midnight with timezone info
        now = datetime.datetime.now()
        current_day_start = now.replace(
            tzinfo=tzutc(), hour=0, minute=0, second=0, microsecond=0
        )

        month = element_container.find_element_by_class_name('_5a4-').text
        day = element_container.find_element_by_class_name('_5a4z').text
        raw_time_str = element_container.find_element_by_css_selector('._4dml.fsm.fwn.fcg').text

        # TODO handle multiple event days
        # Example date strings:
        # Sat 19:00 UTC+03 · 34 guests
        # Wed 7:00 PM UTC+03
        # 3 May–4 May · 1,582 guests (not handled)
        match = re.search('(\d{1,2}:\d{2}\s+(?:AM\s+|PM\s+)?)UTC(\+\d{2})', raw_time_str)

        if not match:
            print("Failed to find match from '{}'".format(raw_time_str))
            break

        datetime_string = ' '.join([month, day, match.group(1), match.group(2)])
        parsed_date = parse(datetime_string)

        print(parsed_date, raw_time_str)
        if parsed_date < current_day_start:
            break

        New_Event = Event(
            name=element_container.find_element_by_class_name(' _50f7').text,
            venue=driver.find_element_by_class_name('_64-f').text,
            date=parsed_date
        )

        session.add(New_Event)
        session.commit()

driver.quit()

for instance in session.query(Event).order_by(Event.id):  #order_by is optional and will order based om given item
    print(instance)

print("All Done! The DB is created and populated! You're good to go! Have fun!")


