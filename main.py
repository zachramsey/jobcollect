from jobscrape import job_scraper, PROXY  # type: ignore


results_wanted = 500
hours_old = 48

locations = ["United States"]
# locations = ["Greater Seattle Area", "San Francisco Bay Area",
#              "Portland, Oregon Metropolitan Area"]

rl_include = ["Reinforcement Learning", "Optimal Control",
              "Markov Decision Process", "Dynamic Programming"]
rl_exclude = None

ml_include = ["Machine Learning", "Deep Learning", "Neural Network",
              "Computer Vision"]
ml_exclude = None

es_include = ["Embedded", "Firmware"]
es_exclude = None

search = {"Reinforcement Learning": (rl_include, rl_exclude),
          "Machine Learning": (ml_include, ml_exclude),
          "Embedded Systems": (es_include, es_exclude)}

title_include = ["Engineer", "Developer", "Scientist", "Researcher"]

title_exclude = ["Intern", "Senior", "Sr", "Principal", "Staff", "Manager", "\
                 Director", "Lead", "VP", "Vice", "Head", "Chief"]

descr_include = ["Bachelor", "Bachelors", "Bachelor's", "BS ", "BSE ", "BSc ",
                 "B.S.", "B.Sc."]

descr_exclude = ["LangChain", "LlamaIndex", "OpenAI API", "Haystack",
                 "Prompt Engineer", "Prompt Engineering", "Prompt Design",
                 "RAG", "Retrieval-Augmented Generation", "Vector Database",
                 "Pinecone", "ChromaDB", "Weaviate"]


if __name__ == "__main__":
    for group, (search_include, search_exclude) in search.items():
        job_scraper(
            proxy=PROXY,
            results_wanted=results_wanted,
            hours_old=hours_old,
            locations=locations,
            group=group,
            search_include=search_include,
            search_exclude=search_exclude,
            title_include=title_include,
            title_exclude=title_exclude,
            descr_include=descr_include,
            descr_exclude=descr_exclude
        )
