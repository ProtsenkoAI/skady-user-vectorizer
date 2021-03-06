# Suvec
#### Pretrained models are [here](https://drive.google.com/drive/folders/1L_cHapEISPOgUohZN7Tt84f3kj5OHl41?usp=sharing).
#### Example of training word2vec using crawled data is [here](https://github.com/ProtsenkoAI/skady-user-vectorizer/blob/master/notebooks/group2vec.ipynb)
#### Crawled data dumps are [here](https://drive.google.com/drive/folders/1LjrENnP_RD0xAFq-lXc7GJ-s9JiTgeYo?usp=sharing)

Suvec is a tool intended to create features of users using their social networks. At the moment it includes:
1. Engine to crawl groups and friends of users to create group2vec embeddings (details below)
2. [GUI to monitor and manage crawling](https://github.com/ProtsenkoAI/skady-ward): set settings, add proxy and credentials, monitor progress.

### Main features implemented in the engine:
1. Checkpoints of crawling. If an error occurs, crawling can be resumed
2. Import proxies and credentials dynamically if the crawler used all records.
3. [Progress tracking](https://github.com/ProtsenkoAI/skady-user-vectorizer/tree/master/suvec/common/events_tracking) (with terminal or GUI)
4. [Optimized requests scheme](https://github.com/ProtsenkoAI/skady-user-vectorizer/tree/master/suvec/common/requesting) to reduce the number of duplicated requests and requests to private pages.
5. Extensible architecture: I developed Vk-API and scrapy implementation in parallel (at the moment scrapy isn't supported) thus as many components as possible are framework-agnostic, built with interfaces, and connected using simple types.

### Results at the moment
1. Can crawl 24/7 because of dynamic proxy and creds rotating and reloading every day
2. 150k users parsed in one day
3. Pretrained [word2vec embeddings](https://github.com/ProtsenkoAI/skady-user-vectorizer/blob/master/notebooks/group2vec.ipynb) for vk users


It's super alpha-alpha, main problem now is unhandled vk-api and proxy errors, so be careful.
