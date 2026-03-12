import os
import datetime
import requests
import anthropic
import sendgrid
from sendgrid.helpers.mail import Mail

NEWS_API_KEY = os.environ["NEWS_API_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]
TO_EMAIL = os.environ["TO_EMAIL"]
FROM_EMAIL = os.environ["FROM_EMAIL"]

def get_news():
    url = "https://newsapi.org/v2/top-headlines"
    params = {"language": "en", "pageSize": 5, "apiKey": NEWS_API_KEY}
    res = requests.get(url, params=params)
    articles = res.json().get("articles", [])
    headlines = [a["title"] for a in articles if a.get("title")]
    return "\n".join(headlines[:5])

def generate_story(news):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = f"""以下の時事ニュースを題材に、星新一のショートショート風の短編小説を書いてください。

条件：
- 1000〜2000字程度
- 皮肉・ユーモアを含むオチ
- 登場人物は「男」「女」「ロボット」など固有名詞なし
- 最後の1行でどんでん返し
- タイトルも付けること

ニュース：
{news}
"""
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

def save_story(story):
    today = datetime.date.today().strftime("%Y-%m-%d")
    os.makedirs("stories", exist_ok=True)
    filename = f"stories/{today}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {today}\n\n{story}\n")
    print(f"保存完了: {filename}")

def send_email(story):
    today = datetime.date.today().strftime("%Y-%m-%d")
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=TO_EMAIL,
        subject=f"今日のショートショート {today}",
        plain_text_content=story
    )
    response = sg.send(message)
    print(f"メール送信完了: {response.status_code}")

if __name__ == "__main__":
    news = get_news()
    print("取得したニュース：\n", news)
    story = generate_story(news)
    print("生成されたSS：\n", story)
    save_story(story)
    send_email(story)
