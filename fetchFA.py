def fetchArticle(link):
    r = requests.get(link)
    doc = BeautifulSoup(r.content,features='lxml')
    coverImage = doc.find(class_="article-inline-img-block")
    title = doc.find(class_="row article-header--metadata-title")
    post = doc.find(class_="article-content-offset")
    coverImageURL = coverImage.find("img").attrs['data-src']
    img = requests.get(coverImageURL).content
    coverFile = './image/' + coverImageURL.split('/')[-1].split('?')[0]
    with open(coverFile,'wb') as f:
        f.write(img)
    coverImage.find("img").attrs['data-src'] = '../image/' + coverImageURL.split('/')[-1].split('?')[0]
    coverImage.find("img").attrs['src'] = '../image/' + coverImageURL.split('/')[-1].split('?')[0]

    for i in post.findAll("img"):
        url = i.attrs['data-src']
        img = requests.get(url).content
        imgfile = './image/'+ url.split('/')[-1].split('?')[0]
        with open(imgfile,'wb') as f:
            f.write(img)
        i.attrs['src'] = '../image/'+ url.split('/')[-1].split('?')[0]
        i.attrs['data-src'] = '../image/'+ url.split('/')[-1].split('?')[0]
    html = '<html lang="en"><meta name="viewport" content="width=device-width, initial-scale=1" /><head><link rel="stylesheet" href="../init.css"><title>Graphic Details</title></head><body>'+str(coverImage)+str(title)+str(post)+'</body></html>'
    with open('./html/'+link.split('/')[-1]+'.html','w') as f:
        f.write(html)
    return
