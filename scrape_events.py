import datetime
import re
import time
import os

from dateutil.parser import parse
from dateutil.tz import tzlocal
from selenium import webdriver
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import config

database_url = os.environ['DATABASE_URL']
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    venue = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    first_date = Column(DateTime)
    second_date = Column(DateTime)

    def __repr__(self):
        return "<Event(name='%s', venue='%s', start_date='%s', end_date='%s', first_date='%s', second_date='%s')>" % (
            self.name, self.venue, self.start_date, self.end_date, self.first_date, self.second_date
        )


Base.metadata.create_all(engine)

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('--no-sandbox')
options.add_argument("--lang=en")
driver = webdriver.Chrome(chrome_options=options)

# Create a datetime for today at midnight with timezone info
now = datetime.datetime.now()
current_day_start = now.replace(
    tzinfo=tzlocal(), hour=0, minute=0, second=0, microsecond=0
)


def extract_date(month, day, raw_time_str):
    """
    Extracts the event start and end dates
    :param month:
    :param day:
    :param raw_time_str:
    :return: The start and end dates
    :rtype tuple
    """

    # Sat 19:00 UTC+03 · 34 guests
    # Wed 7:00 PM UTC+03
    single_date_pattern = '(\d{1,2}:\d{2}\s+(?:AM\s+|PM\s+)?)UTC(\+\d{2})'
    single_date_match = re.search(single_date_pattern, raw_time_str)
    if single_date_match:
        datetime_string = ' '.join([month, day, single_date_match.group(1),
                                    single_date_match.group(2)])
        parsed_start_date = parse(datetime_string, default=current_day_start)
        return parsed_start_date, None

    # Sun, 13 May · 2 times · 79 guests
    # Sun May 13 · 2 Times · 79 guests
    single_date_pattern2 = '(\S+,?\s+\d*\s*\S{3}\s*\d*)\s+·'
    single_date_match2 = re.search(single_date_pattern2, raw_time_str)
    if single_date_match2:
        parsed_start_date = parse(single_date_match2.group(1),
                                  default=current_day_start)
        return parsed_start_date, None

    # May 7 - May 13 · 230 guests
    # 3 May–4 May · 1,582 guests
    # 18 April 2016–22 April 2016
    # Apr 18, 2016 - Apr 22, 2016
    multiple_date_pattern = '(\d*\s*\S+(?:\s+\d+,?\s*\d*)?)\s*(?:–|-)\s*(\d*\s*\S+(?:\s+\d+,?\s*\d*)?)'
    multiple_date_match = re.search(multiple_date_pattern, raw_time_str)
    if multiple_date_match:
        parsed_start_date = parse(multiple_date_match.group(1),
                                  default=current_day_start)
        parsed_end_date = parse(multiple_date_match.group(2),
                                default=current_day_start)

        return parsed_start_date, parsed_end_date

    return None, None


def process_event(element_container):
    month = element_container.find_element_by_class_name('_5a4-').text
    day = element_container.find_element_by_class_name('_5a4z').text
    raw_time_str = element_container.find_element_by_css_selector(
        '._4dml.fsm.fwn.fcg').text

    parsed_start_date, parsed_end_date = extract_date(month, day, raw_time_str)

    if not parsed_start_date:
        print("Failed to match time from '{}'".format(raw_time_str))
        return

    new_event = Event(
        name=element_container.find_element_by_class_name(' _50f7').text,
        venue=driver.find_element_by_class_name('_64-f').text,
        start_date=parsed_start_date,
        end_date=parsed_end_date
    )
    session.add(new_event)
    session.commit()


def process_recurring_event(recurring_element_container):

    # list with the next 2 dates for recurring events
    next_dates = recurring_element_container.find_elements_by_css_selector('._2l43.clearfix._ikh')
    next_dates_parsed = []

    for next_date in next_dates:
        month_first = next_date.find_element_by_class_name('_5a4-').text
        day_first = next_date.find_element_by_class_name('_5a4z').text
        raw_time_str_first = next_date.find_element_by_css_selector('._2l4t._4bl9').text

        parsed_date, _ = extract_date(month_first, day_first, raw_time_str_first)
        if not parsed_date:
            print("Failed to match time from '{}'".format(raw_time_str_first))
            return
        next_dates_parsed.append(parsed_date)

    if len(next_dates_parsed) == 2:
        new_recurring_event = Event(
            name=recurring_element_container.find_element_by_css_selector('._2l3f._2pic').text,
            venue=recurring_element_container.find_element_by_css_selector('._2l3g._2pic').text,
            first_date=next_dates_parsed[0],
            second_date=next_dates_parsed[1]
        )
        session.add(new_recurring_event)
        session.commit()

    elif len(next_dates_parsed) == 1:
        new_recurring_event = Event(
            name=recurring_element_container.find_element_by_css_selector('._2l3f._2pic').text,
            venue=recurring_element_container.find_element_by_css_selector('._2l3g._2pic').text,
            first_date=next_dates_parsed[0]
        )
        session.add(new_recurring_event)
        session.commit()

    else:
        pass #if the recurring event does not have displayed dates, we skip adding it


for fb_page in config.fb_pages:
    driver.get(fb_page + '/events')
    driver.maximize_window()
    # TODO remove sleep if possible
    time.sleep(3)

    past_events = driver.find_element_by_id("past_events_card")
    driver.execute_script("return arguments[0].scrollIntoView();", past_events)
    time.sleep(5)

    upcoming_elements_container = driver.find_element_by_id("upcoming_events_card") #identifies the upcoming events container
    elements_containers = upcoming_elements_container.find_elements_by_class_name('_24er') #identifies event paragraph(event) in upcoming events container
    for element_container in elements_containers:
        process_event(element_container)

    recurring_elements_containers = driver.find_elements_by_css_selector('._j6k.clearfix._ikh')
    for recurring_element_container in recurring_elements_containers:
        process_recurring_event(recurring_element_container)

# TODO quit even if there is an exception
driver.quit()

for instance in session.query(Event).order_by(Event.id):  #order_by is optional and will order based om given item
    print(instance)

print("All Done! The DB is created and populated! You're good to go! Have fun!!!!!")


