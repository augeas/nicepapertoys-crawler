
import re

from dateutil import parser
import scrapy

image_xp = {
    'url': 'h3/a/@href',
    'text': 'h3/a/text()',
    'profile_id': 'p/span/a/@href',
    'profile_name': 'p/span/a/text()',
}

class PhotosSpider(scrapy.Spider):
    name = "photos"
    allowed_domains = ["www.nicepapertoys.com"]
    start_urls = ["http://www.nicepapertoys.com/photo"]

    def parse(self, response):        
        image_items = response.css('div.xg_list_photo>ul>li>div.bd>div.tb')        
                
        images = [dict(zip(image_xp.keys(), img)) for img in 
            zip(*[image_items.xpath(xp).extract() for xp in image_xp.values()])
        ]
        
        for im in images:
            im['profile_id'] = im['profile_id'].split('/')[-1]
            yield scrapy.Request(url=im['url'], meta=im, callback=self.parse_image)
            
        page_anchor = response.css('ul.pagination>li>a')[-1]
        if page_anchor.xpath('text()').extract_first().startswith('Next'):
            next_page =  page_anchor.xpath('@href').extract_first().split('page=')[-1]
            yield scrapy.Request(
                url="https://www.nicepapertoys.com/photo?page={}".format(next_page),
                callback=self.parse
            )

    def parse_image(self, response):
        image = {k: response.meta.get(k) for k in image_xp.keys()}

        image['url'] = response.url.split('?')[0]

        try:
            image['added'] = parser.parse(response.css('ul.byline>li').xpath(
                'a[last()]/text()').extract_first()).isoformat()
        except:
            raw_ts = response.css('ul.byline>li').xpath('a[last()]/text()').extract_first()
            image['added'] = parser.parse(' '.join(re.split('on|at', raw_ts)[-2:])).isoformat()

        image['image_urls'] = response.css('a.xg_sprite-view-fullsize').xpath(
            '@href').extract()
        
        body = response.css('div.imgarea>div.xg_user_generated')
        
        image['text'] = ''.join(body.xpath(
            'descendant::*/text()').extract()).strip()

        anchors = filter(lambda a: a.xpath('text()').extract(),
            body.xpath('descendant::a'))

        image['links'] = {a.xpath('text()').extract_first(): a.xpath('@href').extract_first()
            for a in anchors}

        comments = response.css('dl.comment')
        comment_authors = comments.css('span.xg_avatar>a').xpath('@title').extract()
        comment_author_ids = [h.split('/')[-1]
            for h in comments.css('span.xg_avatar>a').xpath('@href').extract()]
        comment_text = comments.css('dd>div.xg_user_generated').xpath(
            'descendant::*/text()').extract()
        timestamps = [parser.parse(
            ''.join(c.xpath('text()').extract()).split('on')[-1]).isoformat()
            for c in  comments.xpath('dt')
        ]
            
        image['comments'] = [dict(zip(('author', 'author_id', 'text', 'added'),
            com)) for com in zip(comment_authors, comment_author_ids,
            comment_text, timestamps)
        ]

        yield image
