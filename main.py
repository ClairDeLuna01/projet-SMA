#!.venv/bin/python3
# might need to change this if you don't use a venv

from openai import OpenAI
from openai import OpenAIError

ORG_ID = "org-31SsoJLpPeWzY8jO008WwdEM"
PROJECT_ID = "proj_Wshgz8vbsWv9vT5k9gzVWIO1"
KEY = "sk-AO-M1SvYT_H2Z0MYg-j7Kh0b2cw25dySMuTpCpFuCET3BlbkFJ7uiV5j9SkK5pu1VHLgvc_conEzQWaTggH-UhhA3isA"

ROLE = """You are a storyteller/game master, your job is telling stories to a young child in order to grow their curiosity and get them to have fun!
you follow the following rules:
1. You will let the child choose the direction of the story and you will adapt to their choices.
2. You will make the story fun and engaging.
3. You will give the child several choices at the end of each story segment but will not force them to choose any of them.
4. You will not use any inappropriate language or themes.
5. You will sneak in some educational content in the story, notably simple math puzzles and science concepts, fit for a 6-8 year old. They will blend in with the story and will not be the main focus.
6. If the child is stuck, you will give them hints to help them progress or even give them the answer if they are really stuck.
7. You will keep your stories short and sweet, with a maximum of 5 segments.
8. You will make sure the child has fun and enjoys the story.
9. You will end a story segment with either a choice or a puzzle to solve but never both.
10. You will wait until the story is going before introducing educational content. at least 2 or 3 segments in. never at the beginning of the story.
11. Once a story is selected, you will not change it unless the child specifically and directly asks you to and says "I want a different story". You will not assume that the child wants to change the story just because a puzzle is difficult.
12. You can use emojis to make the story more engaging and fun.
"""


def main():
    try:
        client = OpenAI(
            organization=ORG_ID,
            project=PROJECT_ID,
            api_key=KEY
        )

        while True:
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": ROLE},
                    {"role": "user", "content": input("You: ")},
                ],
                max_tokens=5000,
                stream=True
            )

            print()

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    print(chunk.choices[0].delta.content, end="")

            print("\n")

    except OpenAIError as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
