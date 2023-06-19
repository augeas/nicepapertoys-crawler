
from datetime import datetime

from dateutil import parser
import scrapy

class VideosSpider(scrapy.Spider):
    name = "videos"
    allowed_domains = ["www.nicepapertoys.com"]
    start_urls = ["https://www.nicepapertoys.com/video"]

    def parse(self, response):
        vid_list = response.css('div.xg_list_video>ul>li>div.bd>div.tb>h3>a')

        vids = [dict(zip(('url', 'title'), v)) for v in
            zip(vid_list.xpath('@href').extract(), vid_list.xpath('text()').extract())]
        
        for v in vids:
            yield scrapy.Request(url=v['url'], meta={'video': v},
                callback=self.parse_video)
            
        page_anchor = response.css('ul.pagination>li>a')[-1]
        if page_anchor.xpath('text()').extract_first().startswith('Next'):
            next_page =  page_anchor.xpath('@href').extract_first().split('page=')[-1]
            yield scrapy.Request(
                url="https://www.nicepapertoys.com/video?page={}".format(next_page),
                callback=self.parse
            )
            
    def parse_video(self, response):
        right_now = datetime.now().isoformat()
        video = response.meta['video']
        video['retrieved'] = right_now
        
        profile = response.css('div.ib>span.xg_avatar>a')
        video['profile_id'] = profile.xpath('@href').extract_first().split('/')[-1]
        video['profile_name'] = profile.xpath('@title').extract_first()
        
        video['content'] = response.css('div.vid_container>div>iframe').xpath(
            '@src').extract_first()
        
        descr = response.css('div.xg_user_generated')
        video['text'] = ''.join(descr.xpath('descendant::*/text()').extract()).strip()
        video['links'] = dict(zip(descr.xpath('descendant::a/text()').extract(),
            descr.xpath('descendant::a/@href').extract()))
        
        try:
            video['added'] = parser.parse(response.css('ul.byline>li').xpath(
                'a[last()]/text()').extract_first()).isoformat()
        except:
            raw_ts = response.css('ul.byline>li').xpath('a[last()]/text()').extract_first()
            video['added'] = parser.parse(' '.join(re.split('on|at', raw_ts)[-2:])).isoformat()
            
        video['views'] = int(response.css('span.view-count').xpath(
            'text()').extract_first())
        try:
            videp['rating'] = int(response.css('ul.star-rater').xpath(
                '@_rating').extract_first())
        except:
            video['rating'] = 0
        
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

        video['comments'] = [dict(zip(('profile_name', 'profile_id', 'text', 'added'),
            com)) for com in zip(comment_authors, comment_author_ids,
            comment_text, timestamps)
        ]

        yield video
