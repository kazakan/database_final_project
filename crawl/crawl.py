from typing import List
import requests
from bs4 import BeautifulSoup

def getMovieDetailPage(code):
    result = requests.get(f"https://movie.naver.com/movie/bi/mi/basic.naver?code={code}")
    if(result.status_code != 200) : return None
    if("영화 코드값 오류입니다" in result.text): return None
    return result.text

def parseMyInfo(pageSoup : BeautifulSoup):
    soup_my_info : BeautifulSoup = pageSoup.select_one('div.mv_info:nth-child(1)')

    ret = {}

    # movie name
    ret['name'] = soup_my_info.select_one('h3:nth-child(1) > a:nth-child(1)').text

    str_subhead : str = soup_my_info.find("strong","h_movie2").text
    
    # movie alter name, year
    pos_comma : int = str_subhead.rfind(',')
    ret['altname'] = None if pos_comma == -1 else str_subhead[:pos_comma]
    year = str_subhead if pos_comma == -1 else str_subhead[pos_comma+1:]
    ret['year'] = int(year)


    # parse from info_spec
    soup_info_spec : BeautifulSoup = soup_my_info.find("dl","info_spec")

    # first dd in infospec
    # summary | nation | minute (optional) | release (optional)
    dd1 : BeautifulSoup = soup_info_spec.select_one("dd:nth-child(2)")
    dd1_spans : List[BeautifulSoup] = dd1.find_all("span")

    # summary
    a_summary : List[BeautifulSoup] = dd1_spans[0].find_all("a")
    ret['summarys'] = [t.text for t in a_summary]

    # country
    ret['country']  = dd1_spans[1].find("a").text

    # minute
    if(len(dd1_spans) >= 3) :
        ret['minute'] = dd1_spans[2].text.strip()[:-1]

    # release date
    if(len(dd1_spans) >= 4) :
        ret["date"] = dd1_spans[3].find_all("a")[-1].text.strip('.')
        
    return ret

    
    

if __name__ == "__main__":

    for code in [80,182016,99481]:
        html = getMovieDetailPage(code)
        if(html is None):
            print(None)
            continue
        bs = BeautifulSoup(html,'html.parser')
        reslt = parseMyInfo(bs)
        print(reslt)
    
    
    