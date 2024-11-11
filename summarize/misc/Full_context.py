"""
Like map reduce, but use entire text with every call.
So far this is not promising.
"""

from Chain import Model, Prompt, Chain

# preferred_model = "claude-3-haiku-20240307"
preferred_model = "claude"

# Import our example article for testing
example_article = "examples/zitron.txt"
with open(example_article, 'r') as f:
    article_text = f.read()

sectioning_prompt = """
You are an experienced development editor who is able to quickly identify the main narrative of a text and identify the most relevant sections.

You will be provided an article, and asked to label it as separate sections.

<article>
{{article}}
</article>

Please return the article verbatim, with xml tags around each section, like this:
<section1>Dmitri Dmitriyevich Shostakovich[a][b] (25 September [O.S. 12 September] 1906 – 9 August 1975) was a Soviet-era Russian composer and pianist[1] who became internationally known after the premiere of his First Symphony in 1926 and thereafter was regarded as a major composer. Shostakovich achieved early fame in the Soviet Union, but had a complex relationship with its government. His 1934 opera Lady Macbeth of Mtsensk was initially a success but later condemned by the Soviet government, putting his career at risk. In 1948 his work was denounced under the Zhdanov Doctrine, with professional consequences lasting several years. Even after his censure was rescinded in 1956, performances of his music were occasionally subject to state interventions, as with his Thirteenth Symphony (1962). Nevertheless, Shostakovich was a member of the Supreme Soviet of the RSFSR (1947) and the Supreme Soviet of the Soviet Union (from 1962 until his death), as well as chairman of the RSFSR Union of Composers (1960–1968). Over the course of his career, he earned several important awards, including the Order of Lenin, from the Soviet government.</section1>
<section2>Shostakovich combined a variety of different musical techniques in his works. His music is characterized by sharp contrasts, elements of the grotesque, and ambivalent tonality; he was also heavily influenced by neoclassicism and by the late Romanticism of Gustav Mahler. His orchestral works include 15 symphonies and six concerti (two each for piano, violin, and cello). His chamber works include 15 string quartets, a piano quintet, and two piano trios. His solo piano works include two sonatas, an early set of 24 preludes, and a later set of 24 preludes and fugues. Stage works include three completed operas and three ballets. Shostakovich also wrote several song cycles, and a substantial quantity of music for theatre and film. Shostakovich's reputation has continued to grow after his death. Scholarly interest has increased significantly since the late 20th century, including considerable debate about the relationship between his music and his attitudes toward the Soviet government.</section2>

Do not provide any extra text, or comments, or summarizations.
""".strip()

summarizing_prompt = """
You are a talented summarizer who is able to provide information-dense but compact and readable summaries of texts.
""".strip()

# Our functions
def section_text(text: str) -> str:
    """
    Split the text into sections.
    """
    prompt = Prompt(sectioning_prompt)
    model = Model(preferred_model)
    chain = Chain(prompt, model)
    response = chain.run({"article": text})
    return response.content

if __name__ == "__main__":
    section = section_text(article_text)
    print(section)

