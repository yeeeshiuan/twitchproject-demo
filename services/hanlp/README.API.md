---
title: 自然语言处理API服务
header-includes:
    <meta name="keywords" content="NLP，中文分词，自然语言处理，自然语言理解" />
    <meta name="description" content="自然语言处理API服务 powered by HanLP" />
    <link rel="icon" type="image/x-icon" href="favicon.ico" />
---

[![Docker Pulls](https://img.shields.io/docker/pulls/samurais/hanlp-api.svg?maxAge=2592000)](https://hub.docker.com/r/samurais/hanlp-api/) [![Docker Stars](https://img.shields.io/docker/stars/samurais/hanlp-api.svg?maxAge=2592000)](https://hub.docker.com/r/samurais/hanlp-api/) [![Docker Layers](https://images.microbadger.com/badges/image/samurais/hanlp-api.svg)](https://microbadger.com/#/images/samurais/hanlp-api) [![](https://images.microbadger.com/badges/version/samurais/hanlp-api.svg)](https://microbadger.com/images/samurais/hanlp-api "Get your own version badge on microbadger.com")

* 支持中文分词（N-最短路分词、CRF分词、索引分词、用户自定义词典、词性标注），命名实体识别（中国人名、音译人名、日本人名、地名、实体机构名识别），关键词提取，自动摘要，短语提取，拼音转换，简繁转换，文本推荐，依存句法分析（MaxEnt依存句法分析、CRF依存句法分析）

* Powered by [HanLP](http://www.hankcs.com/nlp/hanlp.html)

## About me

<img src="https://avatars3.githubusercontent.com/u/3538629" width="100"/>

[Hain Wang](https://github.com/Samurais/), Software Developer, Thinker and Doer.

通向智能聊天机器人服务过程中的点滴 [http://blog.chatbot.io](http://blog.chatbot.io)

# API

## tokenizer 中文分词

```
POST /tokenizer HTTP/1.1
Host: nlp.chatbot.io
Content-Type: application/json
BODY:
{
	"type": "nlp",
	"content": "刘德华和张学友创作了很多流行歌曲"
}

RESPONSE:
{
  "status": "success",
  "data": [
    {
      "word": "刘德华",
      "nature": "nr",
      "offset": 0
    },
    {
      "word": "和",
      "nature": "cc",
      "offset": 0
    },
    {
      "word": "张学友",
      "nature": "nr",
      "offset": 0
    },
    {
      "word": "创作",
      "nature": "v",
      "offset": 0
    },
    {
      "word": "了",
      "nature": "ule",
      "offset": 0
    },
    {
      "word": "很多",
      "nature": "m",
      "offset": 0
    },
    {
      "word": "流行歌曲",
      "nature": "n",
      "offset": 0
    }
  ]
}
```

| type | description |
| --- | --- | 
| nlp | NLP分词，NLP分词NLPTokenizer会执行全部命名实体识别和词性标注。 |
| crf | CRF分词，CRF对新词有很好的识别能力，但是无法利用自定义词典。 |
| nostopword | 去除停用词分词 |
| index | 索引分词，索引分词IndexTokenizer是面向搜索引擎的分词器，能够对长词全切分，另外通过term.offset可以获取单词在文本中的偏移量。|
| short | 最短路分词，N最短路分词器NShortSegment比最短路分词器慢，但是效果稍微好一些，对命名实体识别能力更强。一般场景下最短路分词的精度已经足够，而且速度比N最短路分词器快几倍，请酌情选择。 |
| nshort | N-最短路分词 |
| speed | 极速词典分词，极速分词是词典最长分词，速度极其快，精度一般。 |
| standard | 标准分词 |

* 返回值

| key | description |
| --- | --- |
| nature | 词性，[词性标记规范](http://samurais.github.io/development/2017/04/28/chinese-pos-tagging/) |
| offset | 单词在文本中的偏移量 |

## keyword 关键词提取
内部采用TextRankKeyword实现，用户可以直接调用，算法详解 [《TextRank算法提取关键词的Java实现》](http://www.hankcs.com/nlp/textrank-algorithm-to-extract-the-keywords-java-implementation.html)

```
POST /keyword HTTP/1.1
Host: nlp.chatbot.io
Content-Type: application/json
BODY:
{
	"num": 2,
	"content": "刘德华和张学友创作了很多流行歌曲"
}

RESPONSE:
{
  "status": "success",
  "data": [
    "创作",
    "张学友",
    "流行歌曲"
  ]
}
```

## summary 自动摘要
内部采用TextRankSentence实现，用户可以直接调用，算法详解 [《TextRank算法自动摘要的Java实现》](http://www.hankcs.com/nlp/textrank-algorithm-java-implementation-of-automatic-abstract.html)。

```
POST /summary HTTP/1.1
Host: nlp.chatbot.io
Content-Type: application/json
BODY:
{
	"num": 2,
	"content": "华尔街向来都是资本主义至上。但理查德·克雷布认为，华尔街还可以是一个友好合作的地方。他在旧金山创立的对冲基金Numerai依靠人工智能算法来处理所有的交易。但这位现年29岁的南非数学家并不是依靠一己之力开发出这些算法的。相反，他的基金从成千上万名匿名数据科学家那里众包这些算法，那些科学家通过打造最成功的交易模型来争夺比特币奖励。而那还不是最奇怪的部分。"
}

RESPONSE:
{
  "status": "success",
  "data": [
    "他在旧金山创立的对冲基金Numerai依靠人工智能算法来处理所有的交易",
    "华尔街还可以是一个友好合作的地方",
    "他的基金从成千上万名匿名数据科学家那里众包这些算法"
  ]
}
```

## 同时获取关键词、摘要

```
POST /query HTTP/1.1
Host: nlp.chatbot.io
Content-Type: application/json
BODY:
{
	"num": 3,
	"content": "华尔街向来都是资本主义至上。但理查德·克雷布认为，华尔街还可以是一个友好合作的地方。他在旧金山创立的对冲基金Numerai依靠人工智能算法来处理所有的交易。但这位现年29岁的南非数学家并不是依靠一己之力开发出这些算法的。相反，他的基金从成千上万名匿名数据科学家那里众包这些算法，那些科学家通过打造最成功的交易模型来争夺比特币奖励。而那还不是最奇怪的部分。"
}

RESPONSE:
{
  "status": "success",
  "data": [
    "争夺比特币",
    "交易模型",
    "人工智能算法"
  ]
}
```

## phrase 短语提取
内部采用MutualInformationEntropyPhraseExtractor实现，用户可以直接调用。算法详解[《基于互信息和左右信息熵的短语提取识别》](http://www.hankcs.com/nlp/extraction-and-identification-of-mutual-information-about-the-phrase-based-on-information-entropy.html)。


```
POST /phrase HTTP/1.1
Host: nlp.chatbot.io
Content-Type: application/json
BODY:
{
	"num": 4,
	"content": "华尔街向来都是资本主义至上。但理查德·克雷布认为，华尔街还可以是一个友好合作的地方。他在旧金山创立的对冲基金Numerai依靠人工智能算法来处理所有的交易。但这位现年29岁的南非数学家并不是依靠一己之力开发出这些算法的。相反，他的基金从成千上万名匿名数据科学家那里众包这些算法，那些科学家通过打造最成功的交易模型来争夺比特币奖励。而那还不是最奇怪的部分。"
}

RESPONSE:
{
  "status": "success",
  "data": {
    "keyword": [
      "算法",
      "交易",
      "依靠"
    ],
    "summary": [
      "他在旧金山创立的对冲基金Numerai依靠人工智能算法来处理所有的交易",
      "华尔街还可以是一个友好合作的地方",
      "他的基金从成千上万名匿名数据科学家那里众包这些算法"
    ]
  }
}
```

## conversion 简、繁、拼音转换
支持声母、韵母、音调、音标和输入法首字母首声母功能。也能给繁体中文注拼音。算法详解[《汉字转拼音与简繁转换的Java实现》](http://www.hankcs.com/nlp/java-chinese-characters-to-pinyin-and-simplified-conversion-realization.html#h2-17)

* 简体转繁体

```
POST /conversion HTTP/1.1
Host: nlp.chatbot.io
Content-Type: application/json
BODY:
{
	"type": "ft",
	"content": "我们的机器人由诗人和音乐家驱动。"
}

RESPONSE:
{
  "status": "success",
  "data": "我們的機器人由詩人和音樂家驅動。"
}
```


* 繁体转简体

```
POST /conversion HTTP/1.1
Host: nlp.chatbot.io
Content-Type: application/json
BODY:
{
	"type": "jt",
	"content": "我們的機器人由詩人和音樂家驅動。"
}

RESPONSE:
{
  "status": "success",
  "data": "我们的机器人由诗人和音乐家驱动。"
}
```

* 转拼音

```
POST /conversion HTTP/1.1
Host: nlp.chatbot.io
Content-Type: application/json
BODY:
{
	"type": "py",
	"content": "我们的机器人由诗人和音乐家驱动。"
}

RESPONSE:
{
  "status": "success",
  "data": [
    "wo",
    "men",
    "de",
    "ji",
    "qi",
    "ren",
    "you",
    "shi",
    "ren",
    "he",
    "yin",
    "le",
    "jia",
    "qu",
    "dong"
  ]
}
```

## REST API Client
[Postman API Collection](https://documenter.getpostman.com/view/244455/hanlp-api/6taa5Ut)

## 声明
> 欢迎联系我：hain_wang#foxmail.com, "# --> @"

# 大家怎么说

> 我曾经也做过 NLP 方面的研究，看了您的接口项目感到由衷敬佩。 -- [jeasonstudio](https://github.com/jeasonstudio)

## 感谢

### HanLP自然语言处理包开源 感谢：

``` 
 Han Language Processing 码农场/自然语言处理	

《基于角色标注的中国人名自动识别研究》张华平 刘群

《基于层叠隐马尔可夫模型的中文命名实体识别》俞鸿魁 张华平 刘群 吕学强 施水才

《基于角色标注的中文机构名识别》俞鸿魁 张华平 刘群

《基于最大熵的依存句法分析》 辛霄 范士喜 王轩 王晓龙

An Efficient Implementation of Trie Structures, JUN-ICHI AOE AND KATSUSHI MORIMOTO

TextRank: Bringing Order into Texts, Rada Mihalcea and Paul Tarau

上海林原信息科技有限公司的刘先生，允许我利用工作时间开发HanLP，提供服务器和域名，并且促成了开源。感谢诸位用户的关注和使用，HanLP并不完善，未来还恳求各位NLP爱好者多多关照，提出宝贵意见。
```

### HanLP自然语言处理 API服务 感谢：

[beyai/node-hanlp](https://github.com/beyai/node-hanlp) 提供npm module。

[fundon](https://github.com/fundon) 提供服务域名。


## FAQ
1. 目前本站服务支持时间？
从2017年5.1至未来9个月没有问题，长期看捐助情况。

2. 如何搭建自己的服务？

参考[这里](https://www.npmjs.com/package/node-hanlp)。

3. 想加入聊天机器人开发者社区？
联系我: hain_wang#foxmail.com, "# --> @"

## 其他

1. 英文：https://stanfordnlp.github.io/CoreNLP/
```
sudo docker run -p 9000:9000 --name coreNLP --rm -i -t motiz88/corenlp
open http://localhost:9000
```

2. Natural Language Toolkit: http://www.nltk.org/

3. Guide [Python自然语言处理](https://item.jd.com/11487324.html)

<img src="https://img14.360buyimg.com/n1/jfs/t154/143/1404795766/112373/a26532a9/53ab8364N00ae0de3.jpg" width="300" />

4. 工作: [http://nlpjob.com/](http://nlpjob.com/)


