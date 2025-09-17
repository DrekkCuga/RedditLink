import praw, json, os, urllib.request, time
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
db_filename = os.environ["DB_FILE"]

REDDIT = praw.Reddit(
        client_id=os.environ["R_CL_ID"],
        client_secret=os.environ["R_CL_SECRET"],
        password=os.environ["R_PASS"],
        user_agent=f"Reddit Saved Archiver by {os.environ["R_USER"]}",
        username=os.environ["R_USER"],
    )

def downloadImage(url):
    req = urllib.request.Request(url, data=None, headers={"User-Agent": "Reddit Saved Archiver by HydraxTheDragon"})
    with urllib.request.urlopen(req) as response:
        data = response.read()
        return data

def handlePost(post):
    webhook = DiscordWebhook(url=os.environ["D_URL"])


    if post.url.startswith("https://www.reddit.com/gallery/"):
        firstItem = True
        try:
            a = post.gallery_data
        except:
            return True #No gallery data, ignore
        
        if len(post.gallery_data["items"]) > 10:
            return True #We can't post more than 10 in a single message
        
        for item in post.gallery_data["items"]:
            id = item["media_id"]
            item_url = post.media_metadata[id]["s"]["u"]

            if firstItem:
                embed = DiscordEmbed(title=post.title, url=post.shortlink)
                webhook.add_embed(embed)
                firstItem = False
            
            filename = item_url.split("/")[-1].split("?")[0]
            webhook.add_file(file=downloadImage(item_url), filename=filename)

    elif post.url.startswith("https://www.redgifs.com/"):
        webhook.content = post.url
    else:
        embed = DiscordEmbed(title=post.title, url=post.shortlink)
        webhook.add_embed(embed)
        filename = post.url.split("/")[-1].split("?")[0]
        webhook.add_file(file=downloadImage(post.url), filename=filename)
    
    response = webhook.execute()
    return response.status_code == 200


def fetch():
    db = []
    if os.path.isfile(db_filename):
        with open(db_filename, "r") as f:
            db = json.load(f)
    
    saved = REDDIT.user.me().saved(limit=10)

    for post in saved:
        if post.id in db:
            continue
        
        handled = False
        try:
            handled = handlePost(post)
        except Exception as e:
            print("Exception while handling post: " + post.id)
            print(e)
        
        if not handled:
            print(f"Failed to handle post '{post.id}'")
            
        db.append(post.id)

    with open(db_filename, "w") as f:
        json.dump(db, f)

def loop():
    while True:
        try:
            fetch()
            print(f"{datetime.now()} - Finished Fetch")
        except Exception as e:
            print("ERROR:")
            print(e)
        time.sleep(60)

if __name__ == "__main__":
    loop()