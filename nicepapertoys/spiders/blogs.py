
from datetime import datetime
import re

from dateutil import parser
import scrapy


blog_xp = {
    'profile': 'span/a/@title',
    'profile_id': 'span/a/@href',
    'title': 'a[last()]/text()',
    'url': 'a[last()]/@href'
}

class BlogsSpider(scrapy.Spider):
    name = "blogs"
    allowed_domains = ["www.nicepapertoys.com"]
    start_urls = ["https://www.nicepapertoys.com/profiles/blog/list"]

    def parse(self, response):
        blog_titles = response.css('div.xg_blog_list>div>h3.title')
        
        blogs = [dict(zip(blog_xp.keys(), blog)) for blog in 
            zip(*[blog_titles.xpath(xp).extract() for xp in blog_xp.values()])
        ]
        
        for blog in blogs:
            blog['profile_id'] = blog['profile_id'].split('/')[-1]
            yield scrapy.Request(url=blog['url'], meta=blog, callback=self.parse_blog)
            
        page_anchor = response.css('ul.pagination>li>a')[-1]
        if page_anchor.xpath('text()').extract_first().startswith('Next'):
            next_page =  page_anchor.xpath('@href').extract_first().split('page=')[-1]
            yield scrapy.Request(
                url="https://www.nicepapertoys.com/profiles/blog/list?page={}".format(next_page),
                callback=self.parse
            )
            
    def parse_blog(self, response):
        right_now = datetime.now().isoformat()
        blog = {k: response.meta.get(k) for k in blog_xp.keys()}
        blog['retrieved'] = right_now    
        blog['url'] = response.url.split('?')[0]
            
        try:
            blog['added'] = parser.parse(response.css('ul.byline>li').xpath(
                'a[last()]/text()').extract_first()).isoformat()
        except:
            raw_ts = response.css('ul.byline>li').xpath('a[last()]/text()').extract_first()
            blog['added'] = parser.parse(' '.join(re.split('on|at', raw_ts)[-2:])).isoformat()
            
        body = response.css('div.postbody')
            
        blog['text'] = ''.join(body.xpath(
            'descendant::*/text()').extract()).strip()
            
        blog['image_urls'] = body.xpath('descendant::img/@src').extract()
        
        try:
            blog['views'] = int(response.css('span.view-count').xpath(
                'text()').extract_first())
        except:
            blog['views'] = None
            
        anchors = filter(lambda a: a.xpath('text()').extract(), body.xpath('descendant::a'))
        blog['links'] = {a.xpath('text()').extract_first(): a.xpath('@href').extract_first()
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
            
        blog['comments'] = [dict(zip(('profile_name', 'profile_id', 'text', 'added'),
            com)) for com in zip(comment_authors, comment_author_ids,
            comment_text, timestamps)
        ]
                
        yield blog









