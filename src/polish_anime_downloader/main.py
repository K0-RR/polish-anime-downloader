"desc"
from urllib.parse import urlsplit, urlunsplit
import requests, re, signal, time, timeit, logging
from bs4 import BeautifulSoup
# TODO użyj time timeit logging
URL = "https://desu-online.pl/kono-subarashii-sekai-ni-bakuen-wo-odcinek-9/"
URL = "https://docchi.pl/series/oshi-no-ko/8"
URL = "https://docchi.pl/series/11eyes/9"
URL = "https://animeni.pl/isekai-shoukan-wa-nidome-desu-odcinek-09/"
# URL = "https://anime-odcinki.pl/anime/s2-opm/15/"
EP_1_LINKS, EP_NUM, base_url = None, None, None  # previously was "[]"
PREV_LINKS = ""
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}


def handle_interrupt(
    signum, frame
):  # MIGHTDO Maybe try wrapping the code inside try: except block would be better since rn I'm importing a "signal" module just to exit gracefully
    "shut up pylint"
    raise SystemExit("\r  Sprzątam...")


def got_links():
    "shut up pylint"
    global EP_NUM, PREV_LINKS
    print(f"Znalezione linki dla odcinka {EP_NUM}:")
    print(links[0])
    EP_NUM = int(EP_NUM) + 1
    PREV_LINKS = links


def get_page_title(html):
    "shut up pylint"
    soup = BeautifulSoup(html, "html.parser")
    if not soup.title.string is None:
        title = soup.title.string.strip()
        return title


signal.signal(
    signal.SIGINT, handle_interrupt
)  # Register the signal handler for SIGINT (Ctrl+C)
if "desu-online" in URL:
    DOMAIN = "desu-online"
elif "animeni" in URL:
    DOMAIN = "animeni"
    print("Anime z lektorem? Serio?")
elif "docchi" in URL:
    DOMAIN = "docchi"
elif URL in ("anime-odcinki", "shinden", "ogladajanime", "animezone"):
    DOMAIN = (
        "anime-odcinki, ogladajanime, shinden i animezone nie są obecnie obsługiwane"
    )
    print(DOMAIN)  # TODO usunąć do dodaniu wsparcia
    raise SystemExit()
else:
    print(
        "Błąd: Nieobsługiwana domena. Zgłoś to tutaj: https://github.com/RDKRACZ/polish-anime-downloader/issues/new"
    )
    raise SystemExit()

if URL.endswith("/"):  # Remove "/" at the end of the URL
    URL = URL[:-1]

if DOMAIN in ('desu-online', 'animeni'):
    base_url = URL.rsplit("-", 1)[0] + "-"

    if URL[-2] == "/" or URL[-2] == "-":
        EP_NUM = int(URL[-1])  # Check if the last char is "/", "-",
    elif URL[-2].isdigit():  # or a digit
        EP_NUM = str(URL[-2:])  # musi być str, bo "leading zeros in decimal integer literals are not permitted" - na wypadek jakby nr odcinka był "01", a nie "1" itd...
    else:
        print("Błąd: Nie można odnaleźć numeru odcinka w URL.")
        raise SystemExit()

elif DOMAIN == "docchi":
    parsed_url = urlsplit(URL)
    BASE_PATH = "/".join(parsed_url.path.split("/")[:-1]) + "/"
    base_url = urlunsplit((parsed_url.scheme, parsed_url.netloc, BASE_PATH, "", ""))

    EP_NUM = int(parsed_url.path.split("/")[-1])

while True:
    episode_url = f"{base_url}{EP_NUM}/"
    response = requests.get(episode_url, headers=headers, timeout=10)
    page_title = get_page_title(response.text)

    if response.status_code == 200:
        with open("anime_page.html", "w", encoding="utf-8") as file:  # TODO albo zapisz ten plik do temp albo w ogóle zapisz w pamięci bo po co na dysku?
            file.write(response.text)
    else:
        print(
            f"Błąd {response.status_code} podczas pobierania strony. Odcinek {EP_NUM} prawdopodobnie nie istnieje (jeszcze?)"
        )
        print(f"{episode_url} - Tytuł strony: {page_title}")
        raise SystemExit()

    with open("anime_page.html", "r", encoding="utf-8") as file:
        contents = file.read()

    PATTERN = r'(https?://[^/]*?(?:ebd\.cda\.pl|cda\.pl/video|drive\.google\.com/file|mega\.nz/embed|mega\.nz/file)[^"\s]*)'
    links = re.findall(
        PATTERN, contents
    )  # Wyszukaj linki w zawartości pobranej na dysk strony

    if EP_NUM == 1:
        EP_1_LINKS = links
        got_links()
    elif links == EP_1_LINKS:
        print(
            f"{DOMAIN} - Błąd: linki odcinka {EP_NUM} są takie same, jak te, w 1. Odcinek {EP_NUM} prawdopodobnie nie istnieje (jeszcze?)"  # to się zdaża tylko na desu, o ile mi wiadomo, gdy wprowadzony numer odcinka mieści się w ilości odcinków w tym anime, ale ten konkretny nie został jeszcze wrzucony? Przykład: seria ma mieć 12 odcinków, na stronie jest obecnie dostępne 11. Jeśli podamy więcej niż 12 to dostaniemy 404, ale jeśli podamy 12 to przekieruje nas na 1 odc...
        )
        break
    elif links == PREV_LINKS:
        print(
            f"Coś poszło nie tak - linki odcinka {EP_NUM}. są takie same, jak te, w poprzednim."
        )
        break
    elif links == []:
        print(
            f"Nie znaleziono linków dla odcinka {EP_NUM} - zakończono wyszukiwanie. Tytuł strony: {page_title}"
        )
        break
    else:
        got_links()
