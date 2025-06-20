from scrapers import scrape_x_url, init_coockies, scrape_main_page_G7
import load
import global_data
from analysis import create_relevant_hashtags_file_from_tweets
import transformations

def scrape_hastags_pages_loop(n_tweets_for_page:int):
    hashtags = load.get_json_data(path="hashtags.json")
    x_pages = {}

    for k in hashtags:
        links = [global_data.generate_X_page_from_hashtag(k, global_data.Tablist.TOP).replace("#",""),
                  global_data.generate_X_page_from_hashtag(k, global_data.Tablist.LATEST).replace("#","")]
        x_pages[k] = []
        x_pages[k] = links

    for k_hashtag, v_links in x_pages.items():
        for link in v_links:
            json_name = k_hashtag.replace("#","")+".json"
            scrape_x_url(file_name=json_name, url=link, max_tweet=n_tweets_for_page)
    load.convert_tweet_json_dict_to_list(path_input="tweets.json", path_output="tweets_final.json")

def update_scraped_tweets(starting_index:int):
    tweets = load.get_json_data("tweets.json")
    for i, k in enumerate(tweets):
        if i >= starting_index:
            scrape_x_url(file_name="tweets_updating.json", url=k , max_tweet=1)
            with open("dove_sono_arrivato.txt", "w") as file:
                file.write(str(i))

def main():
    init_coockies(3)
    update_scraped_tweets(1)
    #Get Hashtags first generation
    #scrape_main_page_G7(file_name="G7_main_page.json", url='https://x.com/G7', max_tweet=800)
    #create_relevant_hashtags_file_from_tweets(tweets_path="G7_main_page.json", output_path="hashtags_first_generation.json")
    #create_relevant_hashtags_file_from_tweets(tweets_path="G7_main_page.json", output_path="hashtags.json")
    
    #Get Hashtags second generation. That will merge with first in hashtags.json file.
    #No more hashtags will be added to these
    #scrape_hastags_pages_loop(n_tweets_for_page=100)
    #create_relevant_hashtags_file_from_tweets(tweets_path="tweets.json", output_path="hashtags.json")

    while(True):
        scrape_hastags_pages_loop(n_tweets_for_page=100)

if __name__ == "__main__":
    main()

