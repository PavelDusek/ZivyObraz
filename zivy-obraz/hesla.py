import datetime
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont


############
# Settings #
############
hesla_xml_path = "/home/pavel/hesla/hesla.xml"

#font_path = "/usr/share/fonts/TTF/DejaVuSans.ttf"
font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
#font_path = "/usr/share/fonts/liberation/LiberationSans-Regular.ttf"

#Large ePaper display
ePaperLarge = (800, 480)
chars_limit_large, trimming_zone_large = 45, 35 #if exceeded, trim, #position where to start searching for a blank to trim
line_count_limit_large = 9 #if exceeded, do not put a blank line in between texts
font_size_header_large, font_size_text_large = 60, 38 
target_image_large = "/var/www/html/dusek.fun/hesla800x480.png"

#Small ePaper display
ePaperSmall = (400, 300)
chars_limit_small, trimming_zone_small = 35, 25 #if exceeded, trim, #position where to start searching for a blank to trim
line_count_limit_small = 10 #if exceeded, do not put a blank line in between texts
font_size_header_small, font_size_text_small = 35, 20 
target_image_small = "/var/www/html/dusek.fun/hesla400x300.png"

########
# Code #
########

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

with open(hesla_xml_path) as f:
    xml = f.read()

soup = BeautifulSoup(xml, 'xml')
today = datetime.datetime.now()
day, month = today.day, today.month
losung = soup.find("LOSUNG", attrs={"d": f"{day}", "m": f"{month}" } )

time_line = losung.find("TL")
old_testament = losung.find("OT")
new_testament = losung.find("NT")

time_text, old_text, new_text = time_line.text.strip(), old_testament.text.strip(), new_testament.text.strip()
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
