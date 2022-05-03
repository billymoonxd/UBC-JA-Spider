# UBC-JA-Spider

Crawl journal abbreviations from [UBC](https://woodward.library.ubc.ca/research-help/journal-abbreviations/), which currently holds as many as 10,172 journals after dropping duplicates (as of April 2022). The abbreviation list *UBC.txt* can be used in place of EndNote's built-in list.

## Encoding Issue

The response seems to use a mixed encoding of UTF-8 and Unicode. The `Content-Type` in Response Headers is `text/javascript;charset=UTF-8`, but the response contains Unicode sequences like **Universit\u00e4t**, which should be **Universität** instead. However, the texts displayed on the website produce desired visual effects. (I guess there may be some post-processing by the JavaScript on the website. 🤔)

A solution to the encoding problem is to encode these Unicode sequences to bytes, and then decode the bytes using `unicode-escape` encoding. **Ensure the file is opened using `utf-8` encoding, otherwise `UnicodeEncodeError` will be thrown.**

```python
# '\\u00e4' --> 'ä'
r = r.encode(encoding='utf-8').decode(encoding='unicode-escape')
with open('./result.txt', 'w+', encoding='utf-8') as f:
    f.writelines(r)
```

Surprisingly, the `payload` in this case is optional. 😊

## File Format

In the built-in list of EndNote, fields are separated using tabs (\t).

| Full Journal |     Abbreviation 1     |      Abbreviation 2       |             Abbreviation 3              |
| :----------: | :--------------------: | :-----------------------: | :-------------------------------------: |
| Journal name | Abbreviation with dots | Abbreviation without dots | Journal name with "and" replaced by "&" |

## Copyright

© 2022 UBC. All rights rested with the University of British Columbia.
