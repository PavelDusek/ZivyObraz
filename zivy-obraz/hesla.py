import datetime
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import requests
import re
from icecream import ic

############
# Settings #
############
hesla_xml_path = "/home/pavel/hesla/hesla.xml"
hesla_url = "https://hesla.dulos.cz/js/losung-cs2025v0.02.js"

#font_path = "/usr/share/fonts/TTF/DejaVuSans.ttf"
font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
#font_path = "/usr/share/fonts/liberation/LiberationSans-Regular.ttf"

#Large ePaper display
ePaperLarge = (800, 480)
chars_limit_large, trimming_zone_large = 45, 35 #if exceeded, trim, #position where to start searching for a blank to trim
line_count_limit_large = 9 #if exceeded, do not put a blank line in between texts
font_size_header_large, font_size_text_large = 60, 38 
target_image_large = "/var/www/html/dusek.fun/hesla800x480.png"
target_image_large = "./hesla800x480.png"

#Small ePaper display
ePaperSmall = (400, 300)
chars_limit_small, trimming_zone_small = 35, 25 #if exceeded, trim, #position where to start searching for a blank to trim
line_count_limit_small = 10 #if exceeded, do not put a blank line in between texts
font_size_header_small, font_size_text_small = 35, 20 
target_image_small = "/var/www/html/dusek.fun/hesla400x300.png"
target_image_small = "./hesla400x300.png"

########
# Code #
########

def get_losung_from_xml(hesla_xml_path):
    today = datetime.datetime.now()
    month, day = today.month, today.day
    with open(hesla_xml_path) as f:
        xml = f.read()

    soup = BeautifulSoup(xml, 'xml')
    losung = soup.find("LOSUNG", attrs={"d": f"{day}", "m": f"{month}" } )

    time_line = losung.find("TL").text.strip()
    old_testament = losung.find("OT").text.strip()
    new_testament = losung.find("NT").text.strip()
    return {"time": time_line, "old_testament": old_testament, "new_testament": new_testament}

def get_losung_online(hesla_url):
    dny = ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle", ]
    mesice = [ "", "leden", "únor", "březen", "duben", "květen", "červen", "červenec", "srpen", "září", "říjen", "listopad", "prosinec", ]

    today = datetime.datetime.now()
    weekday, month = dny[today.weekday()], mesice[today.month]
    time_line = f"{weekday} {today.day}. {month} {today.year}"
    daystamp = today.strftime("%Y-%m-%d")
    source = requests.get(hesla_url)
    texts = source.text.splitlines()

    old_test_search = re.compile(rf'losung.OT\[\"{daystamp}\"\] = \'\|?(.+)\';')
    new_test_search = re.compile(rf'losung.NT\[\"{daystamp}\"\] = \'\|?(.+)\';')
    old_testament, new_testament = "", ""
    for text in texts:
        old_found = old_test_search.search(text)
        new_found = new_test_search.search(text)
        if daystamp in text:
            ic(text)
        if old_found:
            old_testament = old_found.group(1).strip().replace("|", " | ")
        if new_found:
            new_testament = new_found.group(1).strip().replace("|", " | ")
    return {"time": time_line, "old_testament": old_testament, "new_testament": new_testament}

def justify(text, chars_limit, trimming_zone):
    for line in text.splitlines():
        if len(line) > chars_limit:
            #replace a blank with a newline
            old_pattern = line[trimming_zone:]
            new_pattern = old_pattern.replace(" ", "\n", 1)
            text = text.replace(old_pattern, new_pattern)

    #recurrsion, do until fitted:
    line_lengths   = [len(line) for line in text.splitlines()]
    limit_exceeded = [length > chars_limit for length in line_lengths]
    if any(limit_exceeded):
        try:
            return justify(text, chars_limit, trimming_zone)
        except RecursionError:
            print("Maximum recursion depth exceeded")
            return text
    else:
        return text

if __name__ == "__main__":
    #losung = get_losung_from_xml(hesla_xml_path)
    losung = get_losung_online(hesla_url)
    print(losung)
    time_text = losung["time"]
    old_text  = losung["old_testament"]
    new_text  = losung["new_testament"]

    old_text_large = justify( old_text, chars_limit_large, trimming_zone_large )
    new_text_large = justify( new_text, chars_limit_large, trimming_zone_large )
    old_text_small = justify( old_text, chars_limit_small, trimming_zone_small )
    new_text_small = justify( new_text, chars_limit_small, trimming_zone_small )

    if len( old_text_large.splitlines() ) + len( new_text_large.splitlines() ) > line_count_limit_large:
        #too long to put a blank line in between
        bible_text_large = f"{old_text_large}\n{new_text_large}"
    else:
        #there is space to put a blank line in between
        bible_text_large = f"{old_text_large}\n\n{new_text_large}"

    if len( old_text_small.splitlines() ) + len( new_text_small.splitlines() ) > line_count_limit_small:
        #too long to put a blank line in between
        bible_text_small = f"{old_text_small}\n{new_text_small}"
    else:
        #there is space to put a blank line in between
        bible_text_small = f"{old_text_small}\n\n{new_text_small}"

    font_header_large   = ImageFont.truetype(font = font_path, size = font_size_header_large)
    font_text_large     = ImageFont.truetype(font = font_path, size = font_size_text_large)
    font_header_small   = ImageFont.truetype(font = font_path, size = font_size_header_small)
    font_text_small     = ImageFont.truetype(font = font_path, size = font_size_text_small)

    im_large = Image.new(mode = "L", size = ePaperLarge, color = 255)
    im_small = Image.new(mode = "L", size = ePaperSmall, color = 255)

    draw_large = ImageDraw.Draw(im_large)
    draw_small = ImageDraw.Draw(im_small)

    #Header
    draw_large.text( xy = (10, 10), text = time_text, font = font_header_large, fill = 0, anchor = 'lt' )
    draw_small.text( xy = (10, 10), text = time_text, font = font_header_small, fill = 0, anchor = 'lt' )

    #Bible text
    draw_large.multiline_text( xy = (10, 70), text = bible_text_large, font = font_text_large, fill = 0 )
    draw_small.multiline_text( xy = (10, 40), text = bible_text_small, font = font_text_small, fill = 0 )

    im_large.save(fp = target_image_large, format = "png")
    im_small.save(fp = target_image_small, format = "png")
