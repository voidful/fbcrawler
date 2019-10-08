import json

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
import sys
import time
import argparse
import csv
import re

parser = argparse.ArgumentParser(description='Non API public FB miner')

parser.add_argument('-p', '--page',
                    dest="page",
                    help="page you want to scrape for recent posts")

parser.add_argument("-g", '--group',
                    dest="group",
                    help="group you want to scrape for recent posts")

parser.add_argument("-d", "--depth", action="store",
                    dest="depth", default=5, type=int,
                    help="How many recent posts you want to gather -- in multiples of (roughly) 8.")

args = parser.parse_args()

global driver

options = Options()

#  Code to disable notifications pop up of Chrome Browser
options.add_argument("--disable-notifications")
options.add_argument("--disable-infobars")
options.add_argument("--mute-audio")
# options.add_argument("headless")

driver = webdriver.Chrome(executable_path="./chromedriver", options=options)


class CollectPosts(object):

    def __init__(self, ids=["oxfess"], depth=5, delay=5):
        self.ids = ids
        self.dump = "./" + ids + ".csv"
        self.depth = depth + 1
        self.delay = delay
        # browser instance
        self.browser = driver
        self.writed = []

        # creating CSV header
        with open(self.dump, "w", newline='', encoding="utf-8") as save_file:
            writer = csv.writer(save_file)
            writer.writerow(["Type", "Id", "Name", "Content", "Link", "Images", "Reactions"])

    def strip(self, string):
        words = string.split()
        words = [word for word in words if "#" not in word]
        string = " ".join(words)
        clean = ""
        for c in string:
            if str.isalnum(c) or (c in [" ", ".", ","]):
                clean += c
        return clean

    def fatch_fbid(self, str):
        have_fbid = re.search(re.compile(r"\&id=(\d+)"), str)
        if have_fbid:
            fbid = have_fbid.groups()[0]
            return fbid

        have_fbid = re.search(re.compile(r"\?id=(\d+)"), str)
        if have_fbid:
            fbid = have_fbid.groups()[0]
            return fbid

        have_fbid = re.search(re.compile(r"\/(\d+)\/"), str)
        if have_fbid:
            fbid = have_fbid.groups()[0]
            return fbid

        return None

    def _extract_html(self, bs_data):
        k = bs_data.find_all(class_="_5pcr userContentWrapper")
        post = list()
        for count, item in enumerate(k):
            try:
                content_post = ['content']
                try:
                    id = self.fatch_fbid(item.find(class_="profileLink").find("a").get('data-hovercard'))
                    content_post.append(id)
                except:
                    content_post.append("")
                    pass

                name = item.find(class_='clearfix').find('img').get('aria-label')
                content_post.append(name)

                # Post Text
                actualPosts = item.find_all(attrs={"data-testid": "post_message"})
                text = ""
                for posts in actualPosts:
                    paragraphs = posts.find_all('p')
                    text = ""
                    for index in range(0, len(paragraphs)):
                        text += paragraphs[index].text
                content_post.append(text)

                # Links
                postLinks = item.find_all(class_="_6ks")
                links = ""
                for postLink in postLinks:
                    links += postLink.find('a').get('href') + "|||||"
                content_post.append(links)

                # Images
                postPictures = item.find_all(class_="scaledImageFitWidth img")
                pictures = ""
                for postPicture in postPictures:
                    pictures = postPicture.get('src') + "|||||"
                content_post.append(pictures)

                # Reactions
                toolBar = item.find_all(attrs={"role": "toolbar"})
                if not toolBar:  # pretty fun
                    continue
                summery = ""
                for toolBar_child in toolBar[0].children:
                    str = toolBar_child['data-testid']
                    reaction = str.split("UFI2TopReactions/tooltip_")[1]
                    for toolBar_child_child in toolBar_child.children:
                        num = toolBar_child_child['aria-label'].split()[0]
                        summery += (reaction + ":" + num)
                content_post.append(summery)
                post.append(content_post)

                # Comments
                postComments = item.find_all(attrs={"data-testid": "UFI2Comment/root_depth_0"})
                for comment in postComments:
                    if comment.find(class_="_6qw4") is None:
                        continue
                    comment_post = ["Comment"]
                    commenter = comment.find(class_="_6qw4").text
                    # Post Id
                    id = self.fatch_fbid(comment.find(class_="_ohe lfloat").find("a").get('data-hovercard'))
                    comment_post.append(id)
                    # Post Name
                    comment_post.append(commenter)

                    comment_text = comment.find("span", class_="_3l3x")
                    if comment_text is not None:
                        comment_post.append(comment_text.text)
                    else:
                        comment_post.append("")
                    comment_link = comment.find(class_="_ns_")
                    if comment_link is not None:
                        comment_post.append(comment_link.get("href"))
                    else:
                        comment_post.append("")
                    comment_pic = comment.find(class_="_2txe")
                    if comment_pic is not None:
                        comment_post.append(comment_pic.find(class_="img").get("src"))
                    else:
                        comment_post.append("")
                    comment_post.append("")
                    post.append(comment_post)
            except Exception as e:
                print(e)

        print(len(post))
        return post

    def collect(self, url):
        # navigate to page
        self.browser.get(url)

        try:
            lastCount = -1
            contCount = 5
            match = False
            lenOfPage = self.browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            while not match:
                lastCount = lenOfPage
                time.sleep(self.delay)
                lenOfPage = self.browser.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return "
                    "lenOfPage;")
                try:
                    self.browser.find_element_by_xpath('//a[@id="expanding_cta_close_button"]').click()
                except:
                    pass
                print("Number Of Scrolls Needed " + str(lenOfPage))
                if lastCount == lenOfPage and contCount > 0:
                    contCount -= 1
                elif lastCount == lenOfPage:
                    match = True
                if contCount < 5 and lastCount != lenOfPage:
                    contCount = 5
        except:
            pass

        try:
            moreComments = self.browser.find_elements_by_xpath(
                '//a[@data-testid="UFI2CommentsPagerRenderer/pager_depth_0"]')
            print("Scrolling through to click on more comments:" + str(len(moreComments)))
            while len(moreComments) != 0:
                for moreComment in moreComments:
                    action = webdriver.common.action_chains.ActionChains(self.browser)
                    try:
                        # move to where the comment button is
                        action.move_to_element_with_offset(moreComment, 1, 1)
                        action.perform()
                        moreComment.click()
                    except:
                        pass
                moreComments = []
        except:
            pass

        # Now that the page is fully scrolled, grab the source code.
        source_data = self.browser.page_source

        bs_data = bs(source_data, 'html.parser')
        post = self._extract_html(bs_data)

        if post not in self.writed:
            self.writed.extend(post)

        self.browser.close()

    def save(self):
        # Once the full page is loaded, we can start scraping
        with open(self.dump, "a+", newline='', encoding="utf-8") as save_file:
            writer = csv.writer(save_file)
            for i in self.writed:
                writer.writerow(i)

    def safe_find_element_by_id(self, elem_id):
        try:
            return self.browser.find_element_by_id(elem_id)
        except NoSuchElementException:
            return None

    def login(self, email, password):
        try:

            self.browser.get("https://www.facebook.com")
            self.browser.maximize_window()

            # filling the form
            self.browser.find_element_by_name('email').send_keys(email)
            self.browser.find_element_by_name('pass').send_keys(password)

            # clicking on login button
            self.browser.find_element_by_id('loginbutton').click()
            # if your account uses multi factor authentication
            mfa_code_input = self.safe_find_element_by_id('approvals_code')

            if mfa_code_input is None:
                return

            mfa_code_input.send_keys(input("Enter MFA code: "))
            self.browser.find_element_by_id('checkpointSubmitButton').click()

            # there are so many screens asking you to verify things. Just skip them all
            while self.safe_find_element_by_id('checkpointSubmitButton') is not None:
                dont_save_browser_radio = self.safe_find_element_by_id('u_0_3')
                if dont_save_browser_radio is not None:
                    dont_save_browser_radio.click()

                self.browser.find_element_by_id(
                    'checkpointSubmitButton').click()

        except Exception as e:
            print("There's some error in log in.")
            print(sys.exc_info()[0])
            exit()


if __name__ == "__main__":

    # with open('credentials.txt') as f:
    #     email = f.readline().split('"')[1]
    #     password = f.readline().split('"')[1]
    #
    #     if email == "" or password == "":
    #         print(
    #             "Your email or password is missing. Kindly write them in credentials.txt")
    #         exit()

    try:
        if args.group:
            C = CollectPosts(ids=args.group, depth=args.depth)
            # C.login(email, password)
            C.collect('https://www.facebook.com/groups/' + args.group + '/')
        elif args.page:
            C = CollectPosts(ids=args.page, depth=args.depth)
            # C.login(email, password)
            C.collect('https://www.facebook.com/' + args.page + '/')
    finally:
        C.save()
        print("close")
