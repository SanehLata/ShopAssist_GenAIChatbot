from groq import Groq
import re
import sqlite3
import pandas as pd
from app.config import GROQ_MODEL, DB_PATH

client_sql = Groq()

sql_prompt = """You are an expert in generating SQL queries from natural language using given schema.
<schema>
table: products

fields:
product_id (integer)
url (string)
title (string)
description (string)
price (integer)
currency (string)
availability (string)
rating (float)
review_count (integer)
category (string)
scraped_at (datetime)
</schema>

Rules:

1. Always SELECT * from products
2. String matching rules:
   - Use LOWER(column) exactly LIKE '% keyword %'. Always have space before and after keyword. Never use '%keyword%'
   - Each keyword must have only one word.
   - Apply keyword filters(for color, event, size, occasion) separately on title and description
   - Combine title conditions using AND
   - Combine description conditions using AND
   - Combine title and description blocks using OR

   - The WHERE clause MUST EXACTLY match this template.
        Do not rearrange parentheses.
        Do not move category inside title or description blocks.
        template:

       WHERE
       (
           (
               LOWER(title) LIKE '% keyword1 %'
               AND LOWER(title) LIKE '% keyword2 %'
           )
           OR
           (
               LOWER(description) LIKE '% keyword1 %'
               AND LOWER(description) LIKE '% keyword2 %'
           )
       )
       AND LOWER(category) LIKE '% category%'

3. Category must only use:
   - men
   - women
   - jewelry
   
4. Numeric fields (price, rating, review_count):
   Use =, <, >, <=, >=, BETWEEN only
5. Do NOT use columns outside schema
6. Do NOT use CONCAT or combine title and description
7. Output ONLY SQL query inside:

<SQL>
SELECT ...
</SQL>

8. Always add LIMIT 5"""


comprehension_prompt = """You are an expert in understanding the context of the question and replying based on the data pertaining to the question provided. You will be provided with Question: and Data:. The data will be in the form of an array or a dataframe or dict. Reply based on only the data provided as Data for answering the question asked as Question. Do not write anything like 'Based on the data' or any other technical words. Just a plain simple natural language response.
The Data would always be in context to the question asked. For example is the question is “What is the average rating?” and data is “4.3”, then answer should be “The average rating for the product is 4.3”. So make sure the response is curated with the question and data. Make sure to note the column names to have some context, if needed, for your response.
There can also be cases where you are given an entire dataframe in the Data: field. Always remember that the data field contains the answer of the question asked. All you need to do is to always reply in the following format when asked about a product: 
Produt title, price in USD and rating, and then product link. Take care that all the products are listed in list format, one line after the other. Not as a paragraph.
For example:
1. Campus Women Running Shoes: $104.48, Rating: 4.4 <link>
2. Nike Men Running Shoes: $134.29, Rating: 4.9 <link>
3. Women necklace white: $48.20, Rating: 4.7 <link>

"""


def generate_sql_query(question):
    chat_completion = client_sql.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": sql_prompt,
            },
            {
                "role": "user",
                "content": question,
            }
        ],
        model=GROQ_MODEL,
        temperature=0.2,
        # max_tokens=1024
    )

    return chat_completion.choices[0].message.content



def run_query(query):
    if query.strip().upper().startswith('SELECT'):
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query(query, conn)
            return df


def data_comprehension(question, context):
    chat_completion = client_sql.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": comprehension_prompt,
            },
            {
                "role": "user",
                "content": f"QUESTION: {question}. DATA: {context}",
            }
        ],
        model=GROQ_MODEL,
        temperature=0.2,
        # max_tokens=1024
    )

    return chat_completion.choices[0].message.content



def sql_chain(question):
    sql_query = generate_sql_query(question)
    pattern = "<SQL>(.*?)</SQL>"
    matches = re.findall(pattern, sql_query, re.DOTALL)

    if len(matches) == 0:
        return "Sorry, LLM is not able to generate a query for your question"

    print(matches[0].strip())

    response = run_query(matches[0].strip())
    if response is None:
        return "Sorry, there was a problem executing SQL query"

    # context = response.to_dict(orient='records')
    context = response[[
        "title",
        "price",
        "rating",
        "url",
    ]].head(5).to_dict(orient='records')

    answer = data_comprehension(question, context)
    return answer


if __name__ == "__main__":
    # question = "All shoes with rating higher than 4.5 and total number of reviews greater than 500"
    # sql_query = generate_sql_query(question)
    # print(sql_query)
    question = "Show top 3 shoes in descending order of rating"
    # question = "Show me 3 running shoes for woman"
    # question = "sfsdfsddsfsf"
    answer = sql_chain(question)
    print(answer)
