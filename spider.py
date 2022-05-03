import logging
import logging.config
import random
import re

import pandas as pd
import requests
import yaml


class JCRCrawler(object):
    def __init__(self):
        logger = 'logging.yml'
        uas = 'user_agents.txt'
        headers = 'headers.yml'
        self.logger = self._get_logger(logger)
        self.uas = self._load_user_agents(uas)
        self.headers, self.url, self.payload = self._load_headers(headers)

    def _get_logger(self, file):
        """
        Create a logger from the given YAML file.
        """
        with open(file, 'r') as f:
            config = yaml.safe_load(f)
            logging.config.dictConfig(config)
            logger = logging.getLogger("simpleExample")

        return logger

    def _load_headers(self, file):
        """
        Deserialize the given YAML file to Python objects.
        """
        with open(file, 'r') as f:
            ydict = yaml.safe_load(f)
            headers = ydict['headers']
            url = ydict['url']
            payload = ydict['payload']

        return headers, url, payload

    def _load_user_agents(self, file):
        """
        Load user-agents from the given TXT file.
        """
        uas = []
        with open(file, 'r') as f:
            for ua in f.readlines():
                strip = ua.strip()
                if strip:
                    uas.append(strip)
        random.shuffle(uas)

        return uas

    def _replace_user_agent(self, headers, uas):
        """
        Replace the user-agent in headers with a randomly chosen one from uas.
        """
        ua = random.choice(uas)
        headers['user-agent'] = ua

        return headers

    def _crawl_data(self, url, payload):
        """
        Crawl journal profile.
        """
        try:
            headers = self._replace_user_agent(self.headers, self.uas)
            response = requests.session().post(url, data=payload, headers=headers)
            result = response.text
        except Exception as e:
            result = None
            self.logger.error('Crawl data exception: %s', e)

        return result

    def _parse_data(self, response):
        """
        Parse journal profile. The response uses a charset of UTF-8, but contains Unicode sequences
        like **Universit\u00e4t**, which should be **Universität** instead.
        """
        r = re.sub(r' *<\\/td><\\/tr><tr><td> *', '\n', response)
        r = re.sub(r';', ',', r)
        r = re.sub(r' *<\\/td><td> *', ';', r)  # semicolon as the separator
        r = re.sub(r'<.*>', '\n', r)
        r = re.sub(r' {2,}', ' ', r)
        r = re.sub(r'\t{2,}', '\t', r)
        r = re.sub(r' *\t *', '\t', r)
        r = re.sub(r' *;*\t*\n\t*;* *', '\n', r)
        r = re.sub(r'\n{2,}', '\n', r)
        r = re.sub(r'\s*.*".*\s*', '', r)
        r = re.sub(r'\\t', '', r)
        r = re.sub(r'\\/', '/', r)
        r = re.sub(r'\\\\', '', r)

        # Unicode to UTF-8
        r = r.encode(encoding='utf-8').decode(encoding='unicode-escape')
        with open('./result.txt', 'w+', encoding='utf-8') as f:
            f.writelines(r)

    def _save_data(self):
        """
        Save journal abbreviations using tab (\t) as the separator
        in accordance with EndNote's abbreviation list requirements.
        """
        df = pd.read_csv('./result.txt', delimiter=';', header=None).drop_duplicates()
        df[2] = df[0].apply(lambda x: str(x).replace('.', ''))
        df[3] = df[1].apply(lambda x: str(x).replace(' and ', ' & '))
        df.reindex(columns=[1, 0, 2, 3]) \
            .sort_values(by=0, key=lambda x: x.str.lower()) \
            .to_csv('./UBC.txt', sep='\t', header=None, index=False)

    def crawl(self):
        """
        Start crawling.
        """
        self.logger.info('Crawling data ...')
        response = self._crawl_data(self.url, self.payload)
        self.logger.info('Parsing data ...')
        self._parse_data(response)
        self.logger.info('Saving data ...')
        self._save_data()
        self.logger.info('Done.')


if __name__ == '__main__':
    JCRCrawler().crawl()
