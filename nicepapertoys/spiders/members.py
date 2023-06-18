
from datetime import datetime
import re

from dateutil import parser
import scrapy

class MembersSpider(scrapy.Spider):
    name = "members"
    allowed_domains = ["www.nicepapertoys.com"]
    start_urls = ["https://www.nicepapertoys.com/profiles/members"]

    def parse(self, response):
        urls = ('https://www.nicepapertoys.com' + u for u in
            response.css('div.member_item_thumbnail>a').xpath(
            '@href').extract()
        )
        
        yield from (scrapy.Request(u.split('?')[0], callback=self.parse_member) for u in urls)
        
        nav_anchor = response.css('ul.navigation>li.right>a')

        if nav_anchor.xpath('text()').extract()[-1].lower().startswith('next'):
            yield scrapy.Request(
                url=nav_anchor.xpath('@href').extract()[-1].split('&')[0],
                callback=self.parse)
            
    def parse_member(self, response):
        about_user = response.css('div.module_about_user>div.xg_module_body')

        profile_keys = [k.split(':')[0] for k in about_user.xpath('dl/descendant::dt/text()').extract()]
        
        profile = {
            'retrieved': datetime.now().isoformat(),
            'profile_id': response.url.split('/')[-1].split('?')[0],
            'profile_name': response.css('div.profile>dl>dt>span.fn').xpath(
                'text()').extract_first(),
            'attributes': dict(zip(profile_keys,
                about_user.xpath('dl/descendant::dd/text()').extract())),
            'links': about_user.xpath('dl/descendant::a/@href').extract(),
            'details': response.css('ul.member_detail').xpath('li/text()').extract()
        }
            
        try:
            profile['birthday'] = parser.parse(
                profile['attributes']['My Age']).isoformat()
        except:
            profile['birthday'] = None
            
        profile['image_urls'] = [response.css('span.dy-avatar-full-width').xpath(
            'img/@src').extract_first().split('?')[0]+'?profile=original']
            
        comments = response.css('dl.comment')
        timestamps = [parser.parse(ts.split('At')[-1]).isoformat() for ts in
            filter(lambda ts: ts.startswith('At'),
            comments.xpath('dt/text()').extract())]
        comment_text = ['\n'.join(c.xpath('descendant::*/text()').extract()).strip()
            for c in  comments.xpath('dd')]
        comment_ids = [p.split('/')[-1] for p in
            comments.xpath('dt/a/@href').extract()]
        comment_names = comments.xpath('dt/a/text()').extract()

        profile['comments'] = [
            dict(zip(('profile_id', 'profile_name', 'text', 'added'), c))
            for c in zip(comment_ids, comment_names, comment_text, timestamps)
        ]

        try:
            item_keys = response.css('div.xg_module_body>ul')[0].xpath(
                'li/a/text()').extract()
            item_counts = [int(re.findall('[0-9]+', n)[0]) for n in  response.css(
                'div.xg_module_body>ul')[0].xpath('li/a/parent::li/text()').extract()]
            profile['items'] = dict(zip(item_keys, item_counts))
        except:
            pass
        
        yield profile

        

