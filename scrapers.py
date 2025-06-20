from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm
import time

import transformations
import load
import global_data

LOGS = False

# Global drivers
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(global_data.selenium_user_agent)
main_driver = webdriver.Chrome(options=chrome_options)
main_driver_coockies_index = 0
second_driver = webdriver.Chrome(options=chrome_options)
second_driver_coockies_index = 0

#------ "Private functions" ---------#

# driver functions
def get_new_driver(argumets:list[str] = []) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument(global_data.selenium_user_agent)
    for argument in argumets:
        options.add_argument(argument)
    return webdriver.Chrome(options=options)

def get_manual_access(driver:webdriver.Chrome):
    driver.get("https://x.com/home/")
    #X detects and blocks selenium. The safest way to bypass it is to log in manually.
    input("Log in and press enter to continue scraping.")
    #Click cookies pop up
    try:
        coockies_buttons = WebDriverWait(driver, 10).until(
                    EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.r-1phboty.r-18kxxzh')))[1].click()
    except:
        pass
    global_data.selenium_coockies = driver.get_cookies()
    return driver

def generate_coockies(n_coockies:int = 2) -> list:
    if n_coockies < 2:
        n_coockies = 2
    coockies = []
    for i in range(n_coockies):
        driver = get_new_driver()
        get_manual_access(driver)
        coockies.append(driver.get_cookies())
        driver.close()
    return coockies

def update_coockies_driver(driver:webdriver.Chrome, actual_coockies_index:int) -> bool:
    if actual_coockies_index + 1 == len(global_data.selenium_coockies):
        actual_coockies_index = 0
    else:
        actual_coockies_index + 1

    for coockie_dict in global_data.selenium_coockies[actual_coockies_index]:
        driver.add_cookie(coockie_dict)
    driver.get("https://x.com/home/")

## scrape tweets
def get_tweet_info(tweet:WebElement) -> dict | None:
    tweet_dict = dict()
    #First looking for the time_stamp because inside it there is the unique url of the tweet
    try:
        time_stamp = tweet.find_element(By.CSS_SELECTOR, 'time').get_attribute('datetime')
        url_tweet = tweet.find_element(By.CSS_SELECTOR,
            'a[style="color: rgb(113, 118, 123);"]').get_attribute("href")
        #Little fix if it take other url "media_tags" or "history"
        if url_tweet.endswith("/media_tags") : url_tweet.replace("/media_tags", "")
        if url_tweet.endswith("/history") : url_tweet = url_tweet.replace("/history","")
        if url_tweet not in tweet_dict:
            tweet_dict[url_tweet] = {}
        tweet_dict[url_tweet]['time_stamp'] = time_stamp
    except:
        if LOGS: print("Except Tweet: time_ago")
        if LOGS: print("Cant't take unique url_tweet. Tweet will be ignored.")
        return None
    #Author of the tweet
    try: #  username = div div span span
        tweet_dict[url_tweet]["author"] = {}
        try:
            #Author Link page
            author_a = tweet.find_element(By.CSS_SELECTOR, 'a[class="css-175oi2r r-1wbh5a2 r-dnmrzs r-1ny4l3l r-1loqt21"]')
            tweet_dict[url_tweet]["author"]["page_link"] = author_a.get_attribute("href")
            #Author Name
            try:
                author_name = author_a.find_element(By.CSS_SELECTOR, 'div div span span')
                tweet_dict[url_tweet]["author"]["username"] = author_name.text
            except:
                if LOGS: print("Except Tweet: author_name")
        except:
            if LOGS: print("Except Tweet: author_link then author_name")

    except:
        if LOGS: print("Except Tweet: author_text")
    #We look for the body of the tweet which will be useful both for
    #its textual content and for parsing hashtags and links
    hashtags = list()
    links = list()
    try:
        body = tweet.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetText"]')
        body_text = body.text
        tweet_dict[url_tweet]["body"] = body_text
        for a in body.find_elements(By.CSS_SELECTOR, 'a'):
            if a.text[0] == "#":
                hashtags.append(a.text.upper())
            else:
                links.append(a.text)
        tweet_dict[url_tweet]["hashtags"] = hashtags
        tweet_dict[url_tweet]["links"] = links
    except:
        if LOGS: print("Except Tweet: body, hashtags and links.")
    #Number of comments
    try:
        n_comments_button = tweet.find_element(By.CSS_SELECTOR, 'button[data-testid=reply]')
        n_comments = transformations.twetter_numbers_convert(n_comments_button.text)
        tweet_dict[url_tweet]["n_comments"] = n_comments
    except:
        if LOGS: print("Except Tweet: n_comments_button")
    #Number of retweet
    try:
        n_retweet_button = tweet.find_element(By.CSS_SELECTOR, 'button[data-testid=retweet]')
        n_retweet = transformations.twetter_numbers_convert(n_retweet_button.text)
        tweet_dict[url_tweet]["n_retweet"] = n_retweet
    except:
        if LOGS: print("Except Tweet: n_retweet_button")
    #Like
    try:
        n_like_button = tweet.find_element(By.CSS_SELECTOR, 'button[data-testid=like]')
        n_like = transformations.twetter_numbers_convert(n_like_button.text)
        tweet_dict[url_tweet]["like"] = n_like
    except:
        if LOGS: print("Except Tweet: n_like")
    #Views (2 different possibility: post page or search page with many posts)
    try:
        #First try if we are in main post page a that is the post (not comments)
        n_view_button = tweet.find_element(By.CSS_SELECTOR, 'span[class="css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3 r-1b43r93 r-1cwl3u0 r-b88u0q"]')
        n_view_text = transformations.twetter_numbers_convert(n_view_button.text)
        tweet_dict[url_tweet]["views"] = n_view_text
    except:
        #Otherwise the article is not in it's main page
        try:
            n_view_button = tweet.find_element(By.CSS_SELECTOR, '.css-175oi2r.r-18u37iz.r-1h0z5md.r-13awgt0 a .css-1jxf684.r-bcqeeo.r-1ttztb7.r-qvutc0.r-poiln3')
            n_view_text = transformations.twetter_numbers_convert(n_view_button.text)
            tweet_dict[url_tweet]["views"] = n_view_text
        except:
            if LOGS: print("Except Tweet: n_view_text")
    
    return tweet_dict

def write_all_tweets_from_page_in_JSON(path:str, url:str, max_tweets:int = 20):
    """
    Extracts all tweets present in a page X (ex tweeter).
    The extracted values will be inserted in a dictionary and writed in JSON file
    it is possible to add the maximum number of tweets to extract, 
    if not inserted a maximum of 20 tweets will be extracted.
    """
    global main_driver
    main_driver.get(url)

    #init some object
    tweet_dict = load.get_json_data(path)
    count_no_progress = 0
    last_len_tweet_dict = 0
    last_scroll_height = main_driver.execute_script("return document.body.scrollHeight")
    pbar = tqdm(total=max_tweets, desc="Estrazione tweet")
    pbar.update(len(tweet_dict))

    #start loop
    while(len(tweet_dict) < max_tweets and count_no_progress < 20):
        #Check and print progress
        len_tweet_dict = len(tweet_dict)
        actual_scroll_height = main_driver.execute_script("return document.body.scrollHeight")
        if last_len_tweet_dict == len_tweet_dict and last_scroll_height == actual_scroll_height:
            count_no_progress+=1

            #Above 9 attempts try automatic fixes
            if count_no_progress > 9:
                #If you see the "Retry" button, click it to avoid the function block
                try:
                    retry_button = main_driver.find_element(By.CSS_SELECTOR, '.css-175oi2r.r-1awozwy.r-16y2uox.r-1777fci.r-dd0y9b.r-3o4zer.r-f8sm7e.r-13qz1uu.r-1ye8kvj button')
                    retry_button.click()    
                except:
                    #if there is no retry button try scrolling to the top and then to the bottom again
                    scroll_pos = main_driver.execute_script("return window.pageYOffset;")
                    main_driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(1)
                    main_driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
                    time.sleep(3)
            if count_no_progress > 17:
                update_coockies_driver(main_driver, main_driver_coockies_index)
                main_driver.get(url)
            #if count_no_progress == 20:
            #    main_driver.close()
            #    main_driver = webdriver.Chrome(options=chrome_options)
            #    get_manual_access(main_driver)
        else:
            count_no_progress = 0
        last_len_tweet_dict = len_tweet_dict
        pbar.set_postfix(tentativi=f"{count_no_progress}/20")

        # ------------------- Error messages ----------------#
        # Sometimes the post gets deleted.
        try:
            main_driver.find_element(By.CSS_SELECTOR, 'div[data-testid="error-detail"]')
            tweet_dict[url] = {}
            tweet_dict[url]["deleted"] = True

            start_index = url.rfind("/status/")
            tweet_dict[url]["author"] = {}
            tweet_dict[url]["author"]["page_link"] = url[:start_index]
            load.write_json(path, tweet_dict)
            break
        except:
            pass
        # Error message.
        # Other message of post gets deleted.
        try:
            main_driver.find_element(By.CSS_SELECTOR,
                'div[class="css-175oi2r r-1awozwy r-g2wdr4 r-16cnnyw r-1867qdf r-1phboty r-rs99b7 r-18u37iz r-1wtj0ep r-1mmae3n r-n7gxbd"]')
            tweet_dict[url] = {}
            tweet_dict[url]["deleted"] = True
            load.write_json(path, tweet_dict)
            break
        except:
            pass
        #------------------------------------------------------------------------------

        #Find all "article" that identifies an entire tweet.
        try:
            tweets = WebDriverWait(main_driver, 10).until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'article')))
        except:
            continue
        
        #Get data of all article
        for tweet in tweets:
            #Get data from a single tweet
            tweet_info = get_tweet_info(tweet)

            #Integrate info to main tweet dictionary. Insert just "not None" data.
            if tweet_info:
                for tweet_url, info_dict in tweet_info.items():
                    if tweet_url not in tweet_dict:
                        tweet_dict[tweet_url] = {}
                    for k_info, v_info in info_dict.items():
                        if v_info:
                            tweet_dict[tweet_url][k_info] = v_info

            #Write data on file
            load.write_json(path, tweet_dict)
            if len(tweet_dict) >= max_tweets: break

        pbar.update(len(tweet_dict) - last_len_tweet_dict)
        
        #Scroll down
        WebDriverWait(main_driver, 10).until(
            EC.visibility_of_element_located((By.TAG_NAME, 'body'))).send_keys(Keys.PAGE_DOWN)
        last_scroll_height = main_driver.execute_script("return document.body.scrollHeight")

    pbar.close()

## scrape users/authors of tweets
def get_user_info(user_page:WebElement) -> dict | None:
    global second_driver
    user_dict = dict()
    #Check if the retry button has appeared and click it to reload the content
    try:
        retry_button = user_page.find_element(By.CSS_SELECTOR, '.css-175oi2r.r-1awozwy.r-16y2uox.r-1777fci.r-dd0y9b.r-3o4zer.r-f8sm7e.r-13qz1uu.r-1ye8kvj button')
        retry_button.click()    
    except:
        pass
    #Find "card" where user info are locate
    try:
        user_card = WebDriverWait(user_page, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, '.css-175oi2r.r-3pj75a.r-ttdzmv.r-1ifxtd0')))
    except:
        return None
    #Username
    try:
        username = user_card.find_element(By.CSS_SELECTOR, '.css-175oi2r.r-18u37iz.r-1w6e6rj.r-6gpygo.r-14gqq1x .css-1jxf684.r-bcqeeo.r-1ttztb7.r-qvutc0.r-poiln3')
        user_dict["username"] = username.text
    except:
        if LOGS: print("No username found")
    #all other user info
    try:
        user_info = user_card.find_element(By.CSS_SELECTOR, 'div[data-testid="UserProfileHeader_Items"]')
        #Location
        try:
            user_location = user_info.find_element(By.CSS_SELECTOR, 'span[data-testid="UserLocation"]')
            user_dict["location"] = user_location.text
        except:
            if LOGS: print("No user location found")
        #Birthdate
        try:
            user_birthdate = user_info.find_element(By.CSS_SELECTOR, 'span[data-testid="UserBirthdate"]')
            user_dict["birthdate"] = transformations.tweetter_join_data_convert(user_birthdate.text.replace("Born ", ""))
        except:
            if LOGS: print("No user birthday found")
        #Join date
        try:
            user_join_date = user_info.find_element(By.CSS_SELECTOR, 'span[data-testid="UserJoinDate"]')
            user_dict["join_date"] = transformations.tweetter_join_data_convert(user_join_date.text.replace("Join ", ""))
        except:
            if LOGS: print("No user birthday found")
    except:
        if LOGS: print("No user info fond.")
    #Following and Follower
    try:
        follow_card = user_card.find_elements(By.CSS_SELECTOR, '.css-175oi2r.r-13awgt0.r-18u37iz.r-1w6e6rj a span span')
        #Following
        n_following = transformations.twetter_numbers_convert(follow_card[0].text)
        if n_following:
            user_dict["following"] = n_following
        n_follower = transformations.twetter_numbers_convert(follow_card[2].text)
        if n_follower:
            user_dict["follower"] = n_follower
    except:
        if LOGS: print("No follow card found")
        pass

    return user_dict

def add_users_info_in_tweet_JSON(path:str):
    global second_driver
    #load data from file
    tweets = load.get_json_data(path)
    #Get all unique author
    authors = dict()
    for _, v_tweet in tweets.items():
        if not "author" in v_tweet:
            continue
        if not "page_link" in v_tweet["author"]:
            continue
        if v_tweet["author"]["page_link"] not in authors:
            link = v_tweet["author"]["page_link"]
            authors[link] = {}
            authors[link] = v_tweet["author"]

    author_size = len(authors)
    pbar = tqdm(total=author_size, desc="Estrazione info autori")
    len_authors = len(authors)
    for i, author in enumerate(authors):
        #Calculate process progression 
        pbar.update(1)

        user_info = None
        while(not user_info):
            #Scrape author page
            second_driver.get(author)
            time.sleep(2)
            user_info = get_user_info(second_driver)
            if not user_info:
                #second_driver.close()
                #second_driver = webdriver.Chrome(options=chrome_options)
                #get_manual_access(second_driver)
                update_coockies_driver(second_driver, second_driver_coockies_index)
            else:
                user_info["page_link"] = authors[author]["page_link"]
                authors[author] = user_info
    
    tweets_size = len(tweets)
    pbar = tqdm(total=tweets_size, desc="Aggiornamento tweets con info autori")
    for i, tweet in enumerate(tweets):
        #Calculate process progression 
        pbar.update(1)
        if not "author" in tweets[tweet]:
            continue
        if not "page_link" in tweets[tweet]["author"]:
            continue
        #Merging
        tweets[tweet]["author"] = authors[tweets[tweet]["author"]["page_link"]]

    load.write_json(path, tweets)

#------------ "Public Functions" -------------------#

def init_coockies(n_coockies:int):
    global_data.selenium_coockies = generate_coockies(n_coockies)
    main_driver.get("https://x.com/home/")
    update_coockies_driver(main_driver, 0)
    second_driver.get("https://x.com/home/")
    update_coockies_driver(second_driver, 1)

# Main funtion to scrape tweets from X.com
def scrape_x_url(file_name:str, url:str, max_tweet:int):
    write_all_tweets_from_page_in_JSON(path=file_name, url=url, max_tweets=max_tweet)
    #add_users_info_in_tweet_JSON(file_name)
    load.merge_tweet_json(path_first="tweets.json", path_second=file_name, path_final="tweets.json")
    load.delete_file(path=file_name)

def scrape_main_page_G7(file_name:str, url:str, max_tweet:int):
    write_all_tweets_from_page_in_JSON(path=file_name, url=url, max_tweets=max_tweet)
    add_users_info_in_tweet_JSON(file_name)
    load.merge_tweet_json(path_first="tweets.json", path_second=file_name, path_final="tweets.json")

# -------------------------------------------------#