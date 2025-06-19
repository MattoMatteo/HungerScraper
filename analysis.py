import load

def get_all_tags_from_tweets_json(path:str) -> dict:
    data = load.get_json_data(path)
    response = dict()
    for v in data.values():
        if "hashtags" in v:
            for hashtag in v["hashtags"]:
                if hashtag not in response:
                    response[hashtag] = 0
                response[hashtag]+=1
    return response

def create_relevant_hashtags_file_from_tweets(tweets_path:str, output_path:str)-> dict:
    hashtags = get_all_tags_from_tweets_json(tweets_path)
    hashtags = {k: v for k, v in get_all_tags_from_tweets_json(tweets_path).items() if v > 30}
    hashtags = sorted(hashtags.items(), key=lambda x: x[1], reverse=True)
    hashtags = dict(hashtags)
    load.create_json_file(output_path, hashtags)