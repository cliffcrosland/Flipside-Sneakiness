import urllib, re

pages_cache = {}

def fetch_page(url):
    if url in pages_cache:
        return pages_cache[url]
    contents = urllib.urlopen(url).read()
    pages_cache[url] = contents
    return contents

def get_latest_issue_number():
    contents = fetch_page("http://www.stanfordflipside.com/category/puzzles")
    match = re.search(r'Issue (\d+) Puzzles', contents)
    if match:
        return match.group(1)
    return '0'

def get_url_to_issue_from_puzzles_index(issue, current_page):
    puzzles_div_start = current_page.find('<div class="puzzleList"')
    while puzzles_div_start != -1:
        puzzles_div_end = current_page.find('</div>', puzzles_div_start)
        puzzle_div = current_page[puzzles_div_start:puzzles_div_end]
        match = re.search(r'Issue (\d+) Puzzles', puzzle_div)
        if match and match.group(1) == issue:
            # Found the right issue, return the url
            match = re.search(r'<a href="(.+)" rel', puzzle_div)
            return match.group(1)
        puzzles_div_start = current_page.find('<div class="puzzleList"', puzzles_div_end)
    return ""

def get_the_shift(puzzles_page):
    match = re.search(r'theshift = (\d+);', puzzles_page)
    return match.group(1)

def get_formatted_answers(puzzles_page):
    match = re.search(r'formattedAnswers = new Array\((.+)\)', puzzles_page)
    answers = match.group(1)
    return answers.split(", ")

def get_shifted_answers(the_shift, formatted_answers):
    shifted_answers = []
    for answer in formatted_answers:
        # In old puzzle pages, the answer letters are not shifted. You can tell
        # if the puzzle page is an old one by noticing that the stored answer
        # is in lower case letters.
        if answer.islower(): 
            shifted_answers.append(answer.upper())
        else:
            shifted_answer = ""
            for ch in answer:
                if ch == '"' or ch == " " or ch == "*":
                    shifted_answer += ch
                else:
                    shifted_ch = (ord(ch) - int(the_shift))
                    if shifted_ch < ord('A'):
                        shifted_ch += 26
                    shifted_answer += chr(shifted_ch)
            shifted_answers.append(shifted_answer)
    return shifted_answers

def get_answers_from_puzzles_page(url):
    puzzles_page = fetch_page(url)
    the_shift = get_the_shift(puzzles_page)
    formatted_answers = get_formatted_answers(puzzles_page)
    return get_shifted_answers(the_shift, formatted_answers)

def get_puzzles_index_page_with_number(current_page, page_num):
    link_start = current_page.find("http://stanfordflipside.com/category/puzzles/page/")
    while link_start != -1:
        link_end = current_page.find('</a>', link_start)
        link = current_page[link_start:link_end]
        match = re.search(r'[\w|/|\.|:]+', link)
        if match:
            url = match.group(0)
            match = re.search(r'page/(\d+)/', url)
            if match.group(1) == str(page_num):
                return fetch_page(url)
        link_start = current_page.find('http://stanfordflipside.com/category/puzzles/page/', link_end)
    return ""


def find_answers_for_issue(issue):
    print "Searching for issue %s..." % issue
    current_page = fetch_page("http://www.stanfordflipside.com/category/puzzles")
    page_num = 1
    while page_num < 20:
        print "Checking page %d of Puzzles index..." % page_num
        url = get_url_to_issue_from_puzzles_index(issue, current_page)
        if len(url) > 0:
            print "Issue found! Retrieving and unscrambling answers for puzzles..."
            return get_answers_from_puzzles_page(url)
        else:
            page_num += 1
            current_page = get_puzzles_index_page_with_number(current_page, page_num)
    return []

def main():
    oldest_issue_num = 35
    latest_issue_num = int(get_latest_issue_number())
    print "Get answers to the Stanford Flipside puzzles!"
    print ""
    while True:
      print "For which issue would you like the puzzle answers?"
      print "Answers available for issues %d through %d." % (oldest_issue_num, latest_issue_num)
      print "(Press Enter to exit)"
      issue = raw_input("Issue #: ")
      if len(issue) == 0:
          break
      if int(issue) < oldest_issue_num or int(issue) > latest_issue_num:
          print "Invalid issue number"
          continue
      answers = find_answers_for_issue(issue)
      print ""
      for answer in answers:
          print answer[1:-1] # remove surrounding quotes
      print ""

main()
