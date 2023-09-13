import datetime
import pytz
import re
from dateutil.parser import parse

from .core import PageScraper


class PCMSScraper(PageScraper):

    SCHEDULE_URL = "https://www.pcmsconcerts.org/concerts/livestreams/"

    def __init__(self):
        super(PCMSScraper, self).__init__(pytz.timezone("America/New_York"))

    def get_livestream_details(self, url: str) -> dict:
        # parse, create soup
        soup = self.get_soup(url)

        # info, in the title of the page
        info = soup.title.text
        if "Philadelphia" not in info:
            info += " by PCMS"

        # start date
        evt_dt = soup.find("span", itemprop="startDate")
        evt_dt = datetime.datetime.strptime(evt_dt.text,
                                            "%A, %B %d, %Y - %I:%M %p")

        # return
        res = {
            "start": evt_dt,
            'summary': info,
            'description': url,
        }

        return res

    def get_upcoming_livestreams(self):
        # parse, create soup
        soup = self.get_soup(self.SCHEDULE_URL)

        # events are in the grid of 3 columns
        events = soup.find_all("div", class_="col-lg-4 col-md-6")

        res = list()
        for e_ in events:
            href = e_.find('a', href=True)["href"]
            res.append(href)

        return res


class SCOScraper(PageScraper):
    """Scottish Chamber Orchestra (Edinburgh)"""

    def __init__(self):
        super(SCOScraper, self).__init__(pytz.timezone("Europe/London"))

    def _get_event(self, url: str) -> dict:
        # parse, create soup
        soup = self.get_soup(url)

        # info is the first header in a certain div
        info = soup \
            .find("div", class_="c-page-header__container o-container") \
            .find("h1") \
            .text.strip()

        # start date is in <time>
        evt_dt = soup.find("time").text.strip()
        evt_dt = datetime.datetime.strptime(evt_dt, "%d %B, %I:%M%p")

        # but there is no year, need to add manually
        now = datetime.datetime.now()
        if evt_dt.month < now.month:
            evt_dt = evt_dt.replace(year=now.year + 1)
        else:
            evt_dt = evt_dt.replace(year=now.year)

        evt_dt = self.tz.localize(evt_dt)

        # return
        res = {
            "start": {
                "dateTime": evt_dt,
                "timeZone": self.tz.zone
            },
            'summary': info,
            'description': "\n".join(
                (url,
                 "https://www.youtube.com/user/SCOmusic")
            )
        }

        return res

    def get_event_schedule(self):
        url = "https://www.sco.org.uk/whats-on/category/streamed-concert"

        # parse, create soup
        soup = self.get_soup(url)

        # events are in the grid of 3 columns
        events = soup.find_all(
            "a", class_="c-media c-media--link c-media--event",
            href=True
        )

        res = [e_["href"] for e_ in events]

        return res


class ZeneakademiaScraper(PageScraper):
    def __init__(self):
        super(ZeneakademiaScraper, self) \
            .__init__(pytz.timezone("Europe/Budapest"))

    def get_event_schedule(self):
        url = "https://zeneakademia.hu/streaming"

        # parse, create soup
        soup = self.get_soup(url)

        # links are relative (!) hrefs in articles
        events = soup.find_all("article", class_="event soldout")

        res = list()
        for e_ in events:
            href = e_.find_all('a', href=True)[-1]["href"]
            res.append("https://zeneakademia.hu" + href)

        return res

    def _get_event(self, url: str) -> dict:
        # parse, create soup
        soup = self.get_soup(url)

        # start date
        expr = "([0-9]+ [A-Za-z]+ [0-9]{4}), ([0-9]+[.:][0-9]{2})"
        evt_dt_tag = soup.find("h2", text=re.compile(expr))

        # extract date and time separately
        dt_dt, dt_tm = re.search(expr, evt_dt_tag.text).group(1, 2)
        dt_tm = re.sub(r"[.]", ":", dt_tm)

        evt_dt = f"{dt_dt}, {dt_tm}"
        evt_dt = datetime.datetime.strptime(evt_dt, "%d %B %Y, %H:%M")
        evt_dt = self.tz.localize(evt_dt)

        # info, in the sibling of the date's grand-parent
        info_tag = evt_dt_tag.find_parent().find_parent().find_next_sibling()
        info = info_tag.text

        if "Liszt Academy" not in info:
            info += " by Liszt Academy"

        # return
        res = {
            "start": {
                "dateTime": evt_dt,
                "timeZone": self.tz.zone
            },
            'summary': info,
            'description': url,
        }

        return res


class AllaScalaScraper(PageScraper):
    def __init__(self):
        super(AllaScalaScraper, self).__init__(pytz.timezone("Europe/Rome"))

    def _get_event(self, url: str) -> dict:
        # parse, create soup
        soup = self.get_soup(url)

        # summary
        info_tag = soup.find("h1", class_="title")
        info = info_tag.text
        info += " at Teatro alla Scala" if "alla Scala" not in info else ""

        # date is 5 March 2021 above, but time is like 6pm CET a bit lower
        date_tag = soup.find("div", class_="brd-tl")
        date = date_tag.text
        time_tag = soup.find("div", class_="tab opened").find("p")
        time = re.search("(at [0-9]+[ap]m CET)", time_tag.text).group()
        dt = re.sub(u"\xa0", " ", f"{date} {time}")
        dt = datetime.datetime.strptime(dt, "%d %B %Y at %I%p %Z")
        dt = self.tz.localize(dt)

        res = {
            "start": {
                "dateTime": dt,
                "timeZone": self.tz.zone
            },
            'summary': info,
            'description': url,
        }

        return res

    def get_event_schedule(self) -> list:
        url = "https://www.teatroallascala.org/en/scala-streaming.html"

        # parse, create soup
        soup = self.get_soup(url)

        # links are relative (!) hrefs in articles
        def match_pattern(tag):
            res_ = (tag.name == "article") & \
                   (tag.find("a", href=True) is not None)
            return res_

        events = soup.find_all(match_pattern)

        res = list()
        for e_ in events:
            href = e_.a["href"]
            res.append("https://www.teatroallascala.org/" + href)

        return res


class ConcertgebouwScraper(PageScraper):
    EVENTS_URL = "https://www.concertgebouworkest.nl/en/calendar"

    def get_event_schedule(self) -> list:
        pass

    def get_event(self, url: str) -> dict:
        pass


class MagyarorszagScraper(PageScraper):

    def __init__(self):
        super(MagyarorszagScraper, self) \
            .__init__(pytz.timezone("Europe/Budapest"))

    def _get_event(self, url: str) -> dict:
        # parse, create soup
        soup = self.get_soup(url)

        # date, somewhere in format 2021. 03. 04. 19:00
        dt_tag = soup.find("div",
                           class_="list_under_title program_under_title")
        dt_str = re.search(
            "([0-9]{4}[.] ?[0-9]{1,2}[.] ?[0-9]{1,2}[.] [0-9]{2}:[0-9]{2})",
            dt_tag.text
        ).group(0)
        dt_str = re.sub(" ", "", dt_str)
        dt = datetime.datetime.strptime(dt_str, "%Y.%m.%d.%H:%M")
        dt = self.tz.localize(dt)

        # info, in h2 at the top, possiblywrapped in (Magyar), ... - Online...
        info_tag = soup.find("h2", class_="list_title program_title")
        info = info_tag.text.strip("(Magyar) ")
        info = re.sub(" – Online közvetítés", "", info)

        # add venue info
        if "Filharmónia Magyarország" not in info:
            info += " by Filharmónia Magyarország"

        # description: link to livestream under big yellow circle
        link2live_tag = soup.find("a", href=True,
                                  rel="attachment wp-att-16975")
        link2live = link2live_tag["href"]
        description = "\n\n".join((link2live, url))

        # result
        res = {
            "start": {
                "dateTime": dt,
                "timeZone": self.tz.zone
            },
            'summary': info,
            'description': description,
        }

        return res

    def get_event_schedule(self) -> list:
        url = "http://filharmonia.hu/virtualis-koncertterem-elo-kozvetitesek/"

        # parse, create soup
        soup = self.get_soup(url)

        content_tag = soup.find("div", class_="entry-content")

        def match_pattern(tag):
            res_ = re.match(re.compile(r"^[0-9]{4}[.] [a-záéúőóüö]+ [0-9]+"),
                            tag.text)
            return res_

        a_tags = content_tag.find_all("a", href=True)

        event_urls = list()
        for a_tag in a_tags:
            if a_tag.find(match_pattern) is not None:
                event_urls.append(a_tag["href"])

        return event_urls


class MalmoScraper(PageScraper):
    def __init__(self):
        super(MalmoScraper, self).__init__(pytz.timezone("Europe/Stockholm"))

    def get_event_schedule(self) -> list:
        url = "https://malmolive.se/en/program"

        # parse, create soup
        soup = self.get_soup(url)

        # links are relative (!) hrefs in articles
        events = soup.find_all(
            "div", class_="event-list-item--info__title"
        )

        res = list()
        for e_ in events:
            # is MSO Live?
            if "MSO Live" not in e_.text:
                continue
            href = e_.find_parent("a")["href"]
            res.append("https://malmolive.se/" + href)

        return res

    def _get_event(self, url: str) -> dict:
        # parse, create soup
        soup = self.get_soup(url)

        evt_dt_txt = soup.find("div", class_="event--date").find("span").text
        evt_dt = datetime.datetime.strptime(evt_dt_txt, "%a %d %b %H:%M")

        # but there is no year, need to add manually
        now = datetime.datetime.now()
        if evt_dt.month < now.month:
            evt_dt = evt_dt.replace(year=now.year + 1)
        else:
            evt_dt = evt_dt.replace(year=now.year)

        evt_dt = self.tz.localize(evt_dt)

        # info,
        info = re.sub("\t\r\n", "", soup.find("h1").text.strip())

        # return
        res = {
            "start": {
                "dateTime": evt_dt,
                "timeZone": self.tz.zone
            },
            'summary': info,
            'description': url,
        }

        return res
    

class ElbScraper(PageScraper):
    def __init__(self):
        super(ElbScraper, self).__init__(pytz.timezone("Europe/Berlin"))

    def get_event_schedule(self) -> list:
        url = "https://www.elbphilharmonie.de/en/mediatheque/category/streams"

        # parse, create soup
        soup = self.get_soup(url)

        #
        def match_pattern(tag):
            res_ = (tag.name == "span") & \
                   ("ive stream" in tag.text)
            return res_
        events = soup.find_all(match_pattern)
        res = [e_.find_parent().find("a", href=True)["href"] for e_ in events]

        # + root
        res = ["https://www.elbphilharmonie.de" + url_ for url_ in res]

        return res

    def _get_event(self, url: str) -> dict:
        # parse, create soup
        soup = self.get_soup(url)

        dt_expr = r"on +([0-9]+\s+[A-Za-z]+\s+[0-9]{4})\s+" \
                  r"at ([0-9]{2}:[0-9]{2})"

        def match_pattern(tag):
            res_ = (tag.name in ("p", "span")) and \
                re.search(dt_expr, tag.text)
            return res_
        evt_tag = soup.find(match_pattern)
        evt_dt = re.search(dt_expr, evt_tag.text).group(1) + " " + \
            re.search(dt_expr, evt_tag.text).group(2)
        evt_dt = datetime.datetime.strptime(evt_dt, "%d %B %Y %H:%M")
        evt_dt = self.tz.localize(evt_dt)

        # evt_tag = soup.find("span",
        #                     class_="blog-detail__sub-title h3 no-uppercase")
        # info = soup.find("h1", class_="blog-detail__title no-line").text\
        #     .strip("\n ")
        info = url.split("/")[-2].replace("-", " ")

        # return
        res = {
            "start": {
                "dateTime": evt_dt,
                "timeZone": self.tz.zone
            },
            'summary': info,
            'description': url,
        }

        return res
    

class HrScraper(PageScraper):
    def __init__(self):
        super(HrScraper, self).__init__(pytz.timezone("Europe/Berlin"))

    def get_event_schedule(self) -> list:
        url = "https://www.hr-sinfonieorchester.de/livestreams/index.html"

        # parse, create soup
        soup = self.get_soup(url)

        # links are hrefs
        events = soup \
            .find("section", class_="c-teaserGroup -s100") \
            .find_all("article", class_="c-teaser -alternative -s100 -v100")

        res = list()
        for e_ in events:
            href = e_.find('a', href=True)["href"]
            res.append(href)

        # extra url in the header!
        extra_link = soup.find("a", class_="link c-teaser__headlineLink")
        res.append(extra_link["href"])

        return res

    def _get_event(self, url: str) -> dict:

        e2g = {
            "Januar": "January",
            "Februar": "February",
            "März": "March",
            "April": "April",
            "Mai": "May",
            "Juni": "June",
            "Juli": "July",
            "August": "August",
            "September": "September",
            "Oktober": "October",
            "November": "November",
            "Dezember": "December"
        }

        # parse, create soup
        soup = self.get_soup(url)

        evt_info_tag = soup.find("h2", itemprop="headline")
        evt_dt_tag = evt_info_tag.find("span")
        evt_summary = evt_dt_tag.find_next_sibling("span")
        evt_summary = evt_summary.text
        evt_dt = evt_dt_tag.text
        for k, v in e2g.items():
            evt_dt = re.sub(k, v, evt_dt)
        evt_dt = re.search(
            r"([0-9]+[.] [A-Za-z]+ [0-9]{4} [–|] [0-9.]{5})", evt_dt
        ).group(0)
        evt_dt = re.sub("[–|] ", "", evt_dt)
        evt_dt = datetime.datetime.strptime(evt_dt, "%d. %B %Y %H.%M")

        evt_dt = self.tz.localize(evt_dt)

        # return
        res = {
            "start": {
                "dateTime": evt_dt,
                "timeZone": self.tz.zone
            },
            'summary': evt_summary,
            'description': url,
        }

        return res


class StMaryScraper(PageScraper):
    _YEAR = datetime.date.today().year

    def __init__(self):
        super(StMaryScraper, self).__init__(pytz.timezone("Europe/London"))

    def get_upcoming_livestreams(self) -> list:

        def match_pattern(tag):
            res_ = \
                (tag.name == "table") & \
                (tag.find("table") is not None)
            return res_

        soup = self.get_soup(
            "https://www.st-marys-perivale.org.uk/events-001.shtml"
        )

        tbl = soup.find(match_pattern) \
                  .find("table") \
                  .find_all("tr")

        return tbl

    def get_livestream_details(self, event_tr) -> dict:
        """

        Parameters
        ----------
        event_tr : tag
            row tag of HTML table containing 2 td

        """
        # to dates
        dt, info = tuple(
            td.find("strong").text.strip() for td in event_tr.find_all("td")
        )

        dt = parse(dt, ignoretz=True) \
            .replace(year=self._YEAR)

        info = f"{info} @St. Mary's Perivale"

        res = {"start": dt, "summary": info,
               "description": "https://www.youtube.com/@stmarysperivale2842"}

        return res


if __name__ == '__main__':
    pass
