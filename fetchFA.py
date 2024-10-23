import os,requests,re,json
import pandas as pd
from bs4 import BeautifulSoup
from mako.template import Template

def fetchArticle(link):
    r = requests.get(link)
    doc = BeautifulSoup(r.content,features='lxml')
    coverImage = doc.find(class_="article-inline-img-block")
    title = doc.find(class_="row article-header--metadata-title")
    titlename = title.find(class_="f-serif ls-0 article-title pt-2").text
    post = doc.find(class_="article-content-offset")
    if coverImage:
      coverImageURL = coverImage.find("img").attrs['srcset'].split(',')[-1]
      img = requests.get(coverImageURL).content
      coverFile = './image/' + coverImageURL.split('/')[-1].split('?')[0].replace('%','')
      with open(coverFile,'wb') as f:
          f.write(img)
      coverImage.find("img").attrs['srcset'] = '../image/' + coverImageURL.split('/')[-1].split('?')[0].replace('%','')
      coverImage.find("img").attrs['src'] = '../image/' + coverImageURL.split('/')[-1].split('?')[0].replace('%','')

    for i in post.findAll("img"):
        url = i.attrs['srcset'].split(',')[-1]
        if './image' not in url:
            img = requests.get(url).content
            imgfile = './image/'+ url.split('/')[-1].split('?')[0].replace('%','')
            with open(imgfile,'wb') as f:
                f.write(img)
            i.attrs['src'] = '../image/'+ url.split('/')[-1].split('?')[0].replace('%','')
            i.attrs['srcset'] = ''
    html = '<html lang="en"><meta name="viewport" content="width=device-width, initial-scale=1" /><head><!-- Global site tag (gtag.js) - Google Analytics --><script async src="https://www.googletagmanager.com/gtag/js?id=G-Z85NNYZRHX"></script><script> window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);}  gtag("js", new Date());  gtag("config", "G-Z85NNYZRHX");</script><link rel="stylesheet" href="../init.css"><title>'+titlename+'</title></head><body>'+str(coverImage)+str(title)+str(post)+'</body></html>'
    with open('./html/'+link.split('/')[-1]+'.html','w',encoding='utf8') as f:
        f.write(html)
    return

url = 'https://www.foreignaffairs.com/issues'
r = requests.get(url)
doc = BeautifulSoup(r.content,features="lxml")
coverTitle = doc.find('h1').text
coverURL = doc.find(property="og:image").attrs['content']
issue = json.loads(doc.find('script', type='application/json').string)
node = issue['path']['currentPath'].split('/')[-1]
url = 'https://www.foreignaffairs.com/fa-search.php'
query = {"query":{"match_all":{}},"from":0,"size":100,"_source":{"includes":["fa_node_primary_image_url__mobile_2x","title","field_display_authors","field_subtitle","path","fa_node_type_or_subtype","nid"]},"post_filter":{"bool":{"must":[{"term":{"field_issue__nid":node}}]}},"sort":[{"field_sequence":"asc"},{"fa_normalized_date":"desc"}]}
r = requests.post(url,data=json.dumps(query))
art = json.loads(r.content.decode('utf8'))['hits']['hits']
df_fa = pd.DataFrame(columns=['nid','fa_node_type_or_subtype','title','field_subtitle','field_display_authors','path','fa_node_primary_image_url__mobile_2x'])
for i in art:
    item = json.loads(json.dumps(i['_source']).replace('[','').replace(']',''))
    df_fa = pd.concat([df_fa,pd.DataFrame(data=item,index=[0])],ignore_index=True)

img = requests.get(coverURL).content
with open('./image/cover.png','wb') as f:
    f.write(img)

essay_li = []
df_essay = df_fa.loc[df_fa['fa_node_type_or_subtype']=='Essay']
for i in df_essay.index:
    title = df_essay.title[i]
    desc = df_essay.field_subtitle[i]
    author = df_essay.field_display_authors[i]
    path = './html/'+df_essay.path[i].split('/')[-1]+'.html'
    fetchArticle('https://www.foreignaffairs.com/'+df_essay.path[i])
    imgURL = df_essay.fa_node_primary_image_url__mobile_2x[i]
    img = requests.get(imgURL).content
    imgPath = './image/'+imgURL.split('/')[-1].split('?')[0].replace('%','')
    with open(imgPath,'wb') as f:
        f.write(img)
    essay_li.append((title,desc,author,path,imgPath))

review_li = []
df_review = df_fa.loc[df_fa['fa_node_type_or_subtype']=='Review Essay']
for i in df_review.index:
    title = df_review.title[i]
    desc = df_review.field_subtitle[i]
    author = df_review.field_display_authors[i]
    path = './html/'+df_review.path[i].split('/')[-1]+'.html'
    fetchArticle('https://www.foreignaffairs.com/'+df_review.path[i])
    imgURL = df_review.fa_node_primary_image_url__mobile_2x[i]
    img = requests.get(imgURL).content
    imgPath = './image/'+imgURL.split('/')[-1].split('?')[0].replace('%','')
    with open(imgPath,'wb') as f:
        f.write(img)
    review_li.append((title,desc,author,path,imgPath))

HTML = Template("""<!DOCTYPE html>
<html>
<head>
  <meta content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no" name=viewport>
  <meta charset=utf-8>
  <link rel="stylesheet" href="./index.css">
  <title>${coverTitle}</title>
</head>
<body>
<figure>
  <img src="./image/cover.png">
</figure>
<h1 class="cover-story">${coverTitle}</h1>
<div class="magazine-list">
<h2 class="section">Essay</h2>
<div class="magazine-article-container">
%for title,desc,author,path,imgPath in essay_li:
    <a class="article-card" href=${path}>
      <div class="article-image">
        <img class="col-4" src=${imgPath}>
      </div>
      <div class="article">
        <h3 class="article-title">${title}</h3>
        <p class="article-desc">${desc}</p>
        <h4 class="article-author">${author}</h4>
      </div>
    </a>
%endfor
</div>
  <h2 class="section">Review Essay</h2>
  <div class="magazine-article-container">
%for title,desc,author,path,imgPath in review_li:
    <a class="article-card" href=${path}>
      <div class="article-image">
        <img class="col-4" src=${imgPath}>
      </div>
      <div class="article">
        <h3 class="article-title">${title}</h3>
        <p class="article-desc">${desc}</p>
        <h4 class="article-author">${author}</h4>
      </div>
    </a>
%endfor
</div>
</div>
</body>
</html>
""")

with open('index.html','w',encoding='utf8') as f:
    f.write(HTML.render(coverTitle=coverTitle,essay_li=essay_li,review_li=review_li))
