import load

def twetter_numbers_convert(number:str) -> int | None:
    """
    Convert numbers string of twetter in INT.
    """
    #First try easy case
    try:
        return int(number)
    except:
        pass
    if number == "":
        return 0
    #Then try K and M case
    number = number.strip().upper()
    if number.endswith("K") or number.endswith("M"):
        if number.endswith("K"):
            number = number.replace("K", "")
            n_zero = 3
        else:
            number = number.replace("M", "")
            n_zero = 6

        first_index = number.find(".")
        if first_index != -1:
            end_index = len(number)-1
            try:
                response = int(number.replace(".", "") + (n_zero - (end_index - first_index)) * "0")
            except:
                response = None
        else:
            try:
                response = int(number + (n_zero * "0"))
            except:
                response = None
    else: #At least try x,xxx case
        try:
            response = int(number.replace(",",""))
        except:
            response = None
    return response

def tweetter_join_data_convert(data:str) -> str:
    """
    Convert some like this: "January 26", to some like this -> "2025-01-26T00:00:00.000Z"
    """
    months_dict = {
        "January ": "01",
        "February ": "02",
        "March ": "03",
        "April ": "04",
        "May ": "05",
        "June ": "06",
        "July ": "07",
        "August ": "08",
        "September ": "09",
        "October ": "10",
        "November ": "11",
        "December ": "12",
        "Gennaio ": "01",
        "Febbraio ": "02",
        "Marzo ": "03",
        "Aprile ": "04",
        "Maggio ": "05",
        "Giugno ": "06",
        "Luglio ": "07",
        "Agosto ": "08",
        "Settembre ": "09",
        "Ottobre ": "10",
        "Novembre ": "11",
        "Dicembre ": "12"
    }
    for k, v in months_dict.items():
        data = data.capitalize()
        if data.find(k) != -1:
            data = data.replace(k,"").replace("Joined ","").replace("Iscrizione: ", "")
            data = data + f"-{v}-01T00:00:00"
            break
    return data

def clean_hashtags():
    tweets = load.get_json_data("tweets.json")
    valid_hashtags = set(load.get_json_data("hashtags_first_generation.json").keys())
    hashtags = load.get_json_data("hashtags.json")
    new_hashtags = set()

    for k_tweet, v_tweet in tweets.items():

        author = author = v_tweet["author"]["username"]
        # Tweet senza hashtags e non scritto da G7 → scartalo
        if "hashtags" not in v_tweet and author != "G7":
            continue

        # Tweet con hashtags → mantieni solo se almeno uno è nei validi
        if "hashtags" in v_tweet:
            tweet_tags = v_tweet["hashtags"]
            if not any(tag in valid_hashtags for tag in tweet_tags):
                continue
            # Tweet valido → aggiungilo
            for hashtag in v_tweet["hashtags"]:
                new_hashtags.add(hashtag)
            final_hashtags_dict = {}
            for k, v in hashtags.items():
                if k.upper() in new_hashtags:
                    final_hashtags_dict[k] = v

def clean_tweets():
    tweets = load.get_json_data("tweets.json")
    valid_hashtags = set(load.get_json_data("hashtags.json").keys())
    new_tweets = {}

    for k_tweet, v_tweet in tweets.items():

        author = v_tweet["author"]["username"]
        # Tweet senza hashtags e non scritto da G7 → scartalo
        if "hashtags" not in v_tweet and author != "G7":
            continue
        # Tweet con hashtags → mantieni solo se almeno uno è nei validi
        if "hashtags" in v_tweet:
            tweet_tags = v_tweet["hashtags"]
            if not any(tag in valid_hashtags for tag in tweet_tags):
                continue

        # Tweet valido → aggiungilo
        new_tweets[k_tweet] = v_tweet

    load.write_json(path="tweets.json", data=new_tweets)
