from bs4 import BeautifulSoup as BS  # 爬虫解析页面
import pandas as pd  # 存入csv文件
import requests  # 爬虫发送请求
import stylecloud
import tqdm
# 请求头
headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)",
           'cookie': 'buvid3=75956395-4864-5FD4-41BA-1E5FD7AE2E5F31279infoc; b_nut=1686802831; i-wanna-go-back=-1; b_ut'
                     '=7; _uuid=944310629-B4104-D586-910BA-1EBD199B3510132390infoc; buvid4=7526B20D-C749-C2C9-CB35-8A03'
                     'A9714CF433069-023061512-/xwqHe8zHTXR+W+s5/esxQ%3D%3D; header_theme_version=CLOSE; DedeUserID=3275'
                     '88631; DedeUserID__ckMd5=0bc0b2b49dbcc115; FEED_LIVE_VERSION=V8; rpdid=|(u))kkYuu|J0J\'uY)Y)|k))|'
                     '; buvid_fp_plain=undefined; CURRENT_BLACKGAP=0; is-2022-channel=1; LIVE_BUVID=AUTO221689346727274'
                     '9; CURRENT_FNVAL=4048; hit-new-style-dyn=1; hit-dyn-v2=1; fingerprint=3793f03b104bee6c4f19c3ec3d'
                     'b8bac5; home_feed_column=5; browser_resolution=1536-786; CURRENT_QUALITY=112; SESSDATA=8dd6cbd8'
                     '%2C1710046358%2Cac47b%2A91CjCYUs7HflBS4uU2z_ouBDdlcQ7coZL4MEduRdZA2fZNWc-Gjdnvt1eJFowyfFjAVhESV'
                     'ndjanZJWm0zR2lmUXBjajV4dnVvYnZ4TlVWcnlUbm9mcmtHWW42WHNQZXBZd1Y5SDQ2WXBJdWpTejMxMG1ZcTZUeGVJYWdx'
                     'c2pTa21jb2pxZE9ZWWlBIIEC; bili_jct=096a174b04037863468c374dce64be6e; bili_ticket=eyJhbGciOiJIUz'
                     'I1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTQ3NTM1OTAsImlhdCI6MTY5NDQ5NDM5MCwicGx0Ijot'
                     'MX0.Qs6QUzqoE8THrCCHznD4aUsC_YKuNmmkvgAGUW9OLM8; bili_ticket_expires=1694753590; bp_video_offse'
                     't_327588631=840836545087799344; buvid_fp=3793f03b104bee6c4f19c3ec3db8bac5; PVID=4; innersign=0;'
                     ' b_lsid=10C89B294_18A8F4AD0E2',
           'oringin': 'https://search.bilibili.com',
           'referer': 'https://search.bilibili.com/all?keyword=%E9%80%80%E9%92%B1%E5%93%A5%E7%9C%8B%E5%9B%BD%E8%B6'
                     '%B3%E4%B8%8D%E6%95%8C%E5%8F%99%E5%88%A9%E4%BA%9A&from_source=webtop_search&spm_id_from=333.'
                     '1007&search_source=4'}


danmu_list = []
danmu_dict = {}

def get_bvid():
    try:
        bv_list = []
        for page in tqdm.tqdm(range(15)):
            # 进行翻页操作
            page += 1
            #对页面发送请求
            r1 = requests.get(url='https://search.bilibili.com/all?keyword=%E6%97%A5%E6%9C%AC%E6%A0%B8%E6%B1%A1%E6%9F%93%E6'
                                  '%B0%B4%E6%8E%92%E6%B5%B7&from_source=webtop_search&spm_id_from=333.788&search_source=2'
                                  '&page={}'.format(page), headers=headers)
            #获取爬取的视频内容
            html1 = r1.text
            # 爬虫解析页面
            soup = BS(html1, 'xml')
            # 搜索标签为a class属性值为img-anchor的内容 会得到视频的url（str类型）
            video_list = soup.find_all("a", class_ = "img-anchor")
            # 对于一页内的20个视频进行循环，并将bv号存入列表中
            for i in tqdm.tqdm(range(20)):
                b_v = (video_list[i]).get('href')
                bvv = b_v[25:37]
                bv_list.append(bvv)
               # print(bvv)
    except Exception as e:
        print("get_bvid出错：", e)
    return bv_list

def get_cid(bv_list):
    try:
        cid_list = []
        # 遍历列表内的300个bv号获取cid列表
        for i in tqdm.tqdm(range(len(bv_list))):
            # 对某个视频发送请求
            r2 = requests.get(url=f'https://api.bilibili.com/x/player/pagelist?bvid={bv_list[i]}', headers=headers)
            # 将页面内容转换成json数据包
            html2 = r2.json()
            # 获取视频对应的cid号
            cid = html2['data'][0]['cid']
            cid_list.append(cid)
    except Exception as e:
        print("get_cid出错：", e)
    return cid_list

def get_danmu_number(cid_list):
    try:
        for cid in cid_list:
            danmu_url = 'http://comment.bilibili.com/{}.xml'.format(cid)
            # 对弹幕页发送请求
            r3 = requests.get(danmu_url)
            r3.encoding = 'utf-8'
            html3 = r3.text
            soup = BS(html3, 'xml')
            # 搜索所有标签为d的内容
            text_list = soup.find_all('d')
            for t in text_list:
                danmu_list.append(t.text)
                # 在生成弹幕列表的同时进行词频的统计
                # 没出现过的弹幕数量赋初值1
                if danmu_dict.get(t.text) is None:
                    danmu_dict[t.text] = 1
                # 出现过的弹幕数量加1
                else:
                    danmu_dict[t.text] += 1
            # 选取出现频次Top20的弹幕
            danmu_number_dict = {}
            # 将字典类型转换为元组，并且key值和value值交换
            danmu_tuplelist = [(danmu_value, danmu_key) for danmu_key, danmu_value in danmu_dict.items()]
            # 用元组的sorted函数实现对value的排序
            danmu_tuplelist_sort = sorted(danmu_tuplelist, reverse=True)
            # 将元组内容回写入字典内
            for i in range(20):
                danmu_number_dict[(danmu_tuplelist_sort[i][1])] = danmu_tuplelist_sort[i][0]
    except Exception as e:
        print("get_danmu_number出错：", e)
    return danmu_number_dict# 将频次Top20写入文档
def write_excel(danmu_number_dict):
        df = pd.DataFrame()
        df['name'] = list(danmu_number_dict.keys())
        df['value'] = list(danmu_number_dict.values())
        writer = pd.ExcelWriter('top20.xlsx')
        df.to_excel(writer)
        writer._save()
        writer.close()

        # 将词频统计写入excel
        df = pd.DataFrame()
        df['name'] = list(danmu_dict.keys())
        df['value'] = list(danmu_dict.values())
        writer = pd.ExcelWriter('统计.xlsx')
        df.to_excel(writer)
        writer._save()
        writer.close()

        # 将文件写入Excel中
        df = pd.DataFrame(danmu_list)
        writer = pd.ExcelWriter('弹幕.xlsx')
        df.to_excel(writer)
        writer._save()
        writer.close()

# 将文件写入txt中
def write_txt():
    with open('danmu.txt', 'w', encoding='utf-8') as f:
        for i in range(len(danmu_list)):
            f.write(danmu_list[i])
            f.write('\n')
def get_wordcloud():
    stylecloud.gen_stylecloud(file_path='danmu.txt',
                              icon_name='fas fa-globe',
                              palette='colorbrewer.diverging.Spectral_11',
                              background_color='black',
                              gradient='horizontal',
                              font_path='msyh.ttc',
                              custom_stopwords=["保护海洋","见证历史"],
                              size=2048,
                              output_name='弹幕.png')
if __name__ == '__main__':
    bv_list = get_bvid()
    cid_list = get_cid(bv_list)
    danmu_number_dict = danmu_dict = get_danmu_number(cid_list)
    write_excel(danmu_number_dict)
    write_txt()
    get_wordcloud()




