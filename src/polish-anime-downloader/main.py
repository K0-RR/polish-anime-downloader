import requests, re, signal, sys, time, timeit, logging
from urllib.parse import urlsplit, urlunsplit
from bs4 import BeautifulSoup
# TODO użyj time timeit logging
url = "https://desu-online.pl/kono-subarashii-sekai-ni-bakuen-wo-odcinek-9/"
url = "https://docchi.pl/series/oshi-no-ko/8"
url = "https://docchi.pl/series/11eyes/9"
url = "https://animeni.pl/isekai-shoukan-wa-nidome-desu-odcinek-09/"
# url = "https://anime-odcinki.pl/anime/s2-opm/15/"
episode_1_links = None  # wcześniej było []
prev_links = ""
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}


def handle_interrupt(
    signum, frame
):  # MIGHTDO Maybe wrapping the code inside try: except block would be better since rn I'm importing two modules just to exit gracefully
    exit("\r  Sprzątam...")


def got_links():
    global episode_number, prev_links
    print(f"Znalezione linki dla odcinka {episode_number}:")
    print(links[0])
    episode_number = int(episode_number) + 1
    prev_links = links


def get_page_title(html):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip()
    return title


signal.signal(
    signal.SIGINT, handle_interrupt
)  # Register the signal handler for SIGINT (Ctrl+C)
if "desu-online" in url:
    domain = "desu-online"
elif "animeni" in url:
    domain = "animeni"
    print("Anime z lektorem? Serio?")
elif "docchi" in url:
    domain = "docchi"
elif "anime-odcinki" or "shinden" or "ogladajanime" or "animezone" in url:
    domain = (
        "anime-odcinki, ogladajanime, shinden i animezone nie są obecnie obsługiwane"
    )
    print(domain)  # TODO usunąć do dodaniu wsparcia
    exit()
else:
    print(
        "Błąd: Nieobsługiwana domena. Zgłoś to tutaj: https://github.com/RDKRACZ/polish-anime-downloader/issues/new"
    )
    exit()

if url.endswith("/"):  # Usuń "/" na końcu URL, jeśli istnieje
    url = url[:-1]

if domain == "desu-online" or "animeni":
    base_url = url.rsplit("-", 1)[0] + "-"

    if url[-2] == "/" or url[-2] == "-":
        episode_number = int(url[-1])  # Sprawdź, czy przedostatni znak to "/", "-",
    elif url[-2].isdigit():  # lub cyfra
        episode_number = url[
            -2:
        ]  # musi być str, bo "leading zeros in decimal integer literals are not permitted" - na wypadek jakby nr odcinka był "01", a nie "1" itd...
    else:
        print("Błąd: Nie można odnaleźć numeru odcinka w URL.")
        exit()

elif domain == "docchi":
    parsed_url = urlsplit(url)
    base_path = "/".join(parsed_url.path.split("/")[:-1]) + "/"
    base_url = urlunsplit((parsed_url.scheme, parsed_url.netloc, base_path, "", ""))

    episode_number = int(parsed_url.path.split("/")[-1])

while True:
    episode_url = f"{base_url}{episode_number}/"
    response = requests.get(episode_url, headers=headers)
    page_title = get_page_title(response.text)

    if response.status_code == 200:
        with open("anime_page.html", "w", encoding="utf-8") as file:
            file.write(response.text)
    else:
        print(
            f"Błąd {response.status_code} podczas pobierania strony. Odcinek {episode_number} prawdopodobnie nie istnieje (jeszcze?)"
        )
        print(f"{episode_url} - Tytuł strony: {page_title}")
        exit()

    with open("anime_page.html", "r", encoding="utf-8") as file:
        contents = file.read()

    pattern = r'(https?://[^/]*?(?:ebd\.cda\.pl|cda\.pl/video|drive\.google\.com/file|mega\.nz/embed|mega\.nz/file)[^"\s]*)'
    links = re.findall(
        pattern, contents
    )  # Wyszukaj linki w zawartości pobranej na dysk strony

    if episode_number == 1:
        episode_1_links = links
        got_links()
    elif links == episode_1_links:
        print(
            f"{domain} - Błąd: linki odcinka {episode_number} są takie same, jak te, w 1. Odcinek {episode_number} prawdopodobnie nie istnieje (jeszcze?)"  # to się zdaża tylko na desu, o ile mi wiadomo, gdy wprowadzony numer odcinka mieści się w ilości odcinków w tym anime, ale ten konkretny nie został jeszcze wrzucony? Przykład: seria ma mieć 12 odcinków, na stronie jest obecnie dostępne 11. Jeśli podamy więcej niż 12 to dostaniemy 404, ale jeśli podamy 12 to przekieruje nas na 1 odc...
        )
        break
    elif links == prev_links:
        print(
            f"Coś poszło nie tak - linki odcinka {episode_number}. są takie same, jak te, w poprzednim."
        )
        break
    elif links == []:
        print(
            f"Nie znaleziono linków dla odcinka {episode_number} - zakończono wyszukiwanie. Tytuł strony: {page_title}"
        )
        break
    else:
        got_links()
