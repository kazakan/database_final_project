from typing import List
import requests
from bs4 import BeautifulSoup

def getMovieDetailPage(code):
    result = requests.get(f"https://movie.naver.com/movie/bi/mi/detail.naver?code={code}")
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

def getDirectors(pageSoup : BeautifulSoup) :
    ret = []
    div_director : BeautifulSoup = pageSoup.select_one(".director")
    divs_dir_obj : List[BeautifulSoup] = div_director.select("div.dir_obj")
    for dir_obj in divs_dir_obj :
        dir_obj_a = dir_obj.select_one(".dir_product > a:nth-child(1)",href=True)
        href = dir_obj_a['href']
        dir_name = dir_obj_a['title']

        dir_code = href.split("=")[-1].strip()
        ret.append((dir_code,dir_name))

    return ret

    
def getActors(pageSoup : BeautifulSoup) :
    ret = []
    div_made_people : BeautifulSoup = pageSoup.select_one(".made_people")

    if(div_made_people is None) : return ret # not available

    divs_p_info : List[BeautifulSoup] = div_made_people.select(".p_info")

    for p_obj in divs_p_info :
        p_obj_a = p_obj.select_one("a:nth-child(1)",href=True)
        href = p_obj_a['href']

        # actor name, code, main or sub actor, role
        actor_name = p_obj_a['title']
        actor_code = href.split("=")[-1].strip()
        actor_ismain = p_obj.select_one("div:nth-child(3) > p:nth-child(1) > em:nth-child(1)").text
        span_actor_role = p_obj.select_one("div:nth-child(3) > p:nth-child(2) > span:nth-child(1)")
        actor_role = span_actor_role.text if span_actor_role else None

        ret.append((actor_code,actor_name,actor_ismain,actor_role))

    return ret

    

if __name__ == "__main__":

    for code in [80,182016,99481,24452]:
        html = getMovieDetailPage(code)
        if(html is None):
            print(None)
            continue
        bs = BeautifulSoup(html,'html.parser')
        reslt = parseMyInfo(bs)
        dirs = getDirectors(bs)
        actors = getActors(bs)
        print(reslt)
        print(dirs)
        print(actors)
    
    
    