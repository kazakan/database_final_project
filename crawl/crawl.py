import asyncio
from time import time
from typing import List
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
import traceback
import pickle

async def getMovieDirectorActorPage(code):
    result = await loop.run_in_executor(None, requests.get,f"https://movie.naver.com/movie/bi/mi/detail.naver?code={code}")
    return result

async def getMovieReview(code,pageNum):
    result = await loop.run_in_executor(
        None, 
        requests.get,
        f"https://movie.naver.com/movie/bi/mi/pointWriteFormList.naver?code={code}&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false&page={pageNum}"
    )
    return result

def parseMyInfo(pageSoup : BeautifulSoup):
    soup_my_info : BeautifulSoup = pageSoup.select_one('.mv_info_area > .mv_info')

    ret = {}

    if(soup_my_info is None) : # this need login
        return None

    # movie name
    ret['name'] = soup_my_info.select_one('h3:nth-child(1) > a').text

    str_subhead : str = soup_my_info.find("strong","h_movie2")['title']
    
    # movie alter name, year
    if len(str_subhead) > 0:
        pos_comma : int = str_subhead.rfind(',')
        ret['altname'] = None if pos_comma == -1 else str_subhead[:pos_comma]
        year = str_subhead if pos_comma == -1 else str_subhead[pos_comma+1:]
        ret['year'] = int(year)


    # parse from info_spec
    soup_info_spec : BeautifulSoup = soup_my_info.find("dl","info_spec")

    # first dd in infospec
    # genres | nation | minute (optional) | release (optional)
    dd1 : BeautifulSoup = soup_info_spec.select_one("dd:nth-child(2)")
    dd1_spans : List[BeautifulSoup] = dd1.find_all("span")

    def parseSpan(span : BeautifulSoup):
        if("N=a:ifo.genre" in span.text): # genre
            a_summary : List[BeautifulSoup] = span.find_all("a")
            ret['summarys'] = [t.text for t in a_summary]
        elif("N=a:ifo.nation" in span.text): #nation
            a_country = span.find("a")
            ret['country']  = a_country.text if(a_country) else None
        elif("N=a:ifo.nation" in span.text): #nation
            ret['minute'] = span.text.strip()[:-1]
        elif("N=a:ifo.day" in span.text): # release date
            ret["date"] = span.find_all("a")[-1].text.strip('.')
    
    for span in dd1_spans:
        parseSpan(span)

    # get ratings
    def parseRatings(div : BeautifulSoup):
        key_num = None
        key_rating = None

        if("N=a:ifo.mgrating" in str(div)): # watched
            key_num = "watched_rating_num"
            key_rating = "watched_rating"
        elif("N=a:ifo.crating" in str(div)): # commentor
            key_num = "commentor_rating_num" # Not available in this section
            key_rating = "commentor_rating"
        elif("N=a:ifo.arating" in str(div)): # netizen
            key_num = "netizen_rating_num"
            key_rating = "netizen_rating"
        else:
            return

       
        em_numbers = div.select_one("div:nth-child(1)> div:nth-child(3) > em:nth-child(2)")
        if em_numbers:
            numbers = em_numbers.text
            ret[key_num] = numbers


        div_star_score = div.select_one("div.star_score")
        ems = div_star_score.find_all('em')
        rating = ""
        for em in ems:
            rating += em.text
        
        ret[key_rating] = rating

    
    div_main_score = soup_my_info.select_one("div.main_score")

    if div_main_score :
        div_main_scores = div_main_score.select("div.score")
        for div_score in div_main_scores:
            parseRatings(div_score)
    
    return ret

def getDirectors(pageSoup : BeautifulSoup) :
    ret = []
    div_director : BeautifulSoup = pageSoup.select_one(".director")

    if(div_director is None) : return ret # not available
    
    divs_dir_obj : List[BeautifulSoup] = div_director.select("div.dir_obj")
    for dir_obj in divs_dir_obj :
        data = {}

        img_director = dir_obj.select_one(".thumb_dir > a:nth-child(1) > img:nth-child(1)")
        if img_director :
            data['img'] = img_director['src']
        
        dir_obj_a = dir_obj.select_one(".dir_product > a:nth-child(1)",href=True)
        href = dir_obj_a['href']
        data['name'] = dir_obj_a['title']

        data['code'] = int(href.split("=")[-1].strip())
        ret.append(data)

    return ret

    
def getActors(pageSoup : BeautifulSoup) :
    ret = []
    div_made_people : BeautifulSoup = pageSoup.select_one(".made_people")

    if(div_made_people is None) : return ret # not available
    
    li_lst_people : List[BeautifulSoup] = div_made_people.select("li")

    for li_obj in li_lst_people :
        
        data = {}

        p_obj  = li_obj.select_one("div.p_info")
        if(p_obj is None):
            return
        p_obj_a = p_obj.select_one("a:nth-child(1)",href=True)
        href = p_obj_a['href']

        # actor name, code, main or sub actor, role
        data['name'] = p_obj_a['title']
        data['code'] = int(href.split("=")[-1].strip())
        data['ismain'] = p_obj.select_one("div:nth-child(3) > p:nth-child(1) > em:nth-child(1)").text
        span_actor_role = p_obj.select_one("div:nth-child(3) > p:nth-child(2) > span:nth-child(1)")
        data['role'] = span_actor_role.text if span_actor_role else None

        # image
        img = li_obj.select_one("p:nth-child(1) > a:nth-child(1) > img:nth-child(1)")
        if img is not None:
            data['img'] = img['src']

        ret.append(data)

    return ret

def getPosterSrc(pageSoup : BeautifulSoup):
    img_poster = pageSoup.select_one("div.mv_info_area > div.poster > a:nth-child(1) > img:nth-child(1)")
    if(img_poster):
        return img_poster['src']
    return None

def crawlOnePage(page : BeautifulSoup):
    result = {}

    if(page is None):
        return None

    movie = parseMyInfo(page)
    if(movie is None) :
            return None
    result['mv'] = movie
    result['director'] = getDirectors(page)
    result['actor'] = getActors(page)
    result['poster'] = getPosterSrc(page)
    return result

def parseOne(response):
        param = response
        if(param.status_code != 200) : return None
        elif("영화 코드값 오류입니다" in param.text): return None
        
        bs = BeautifulSoup(param.text,'html.parser')
        
        result = None
        try:
            result = crawlOnePage(bs)
        except Exception as e:
            traceback.print_exc(str(e))
            return None
        return result

async def processParseBetweenCode(begin,end):
    codes = range(begin,end)
    begin = time()
    responses_future = [asyncio.ensure_future(getMovieDirectorActorPage(code)) for code in codes]
    responses = await asyncio.gather(*responses_future)
    end = time()

    print('다운 실행 시간: {0:.3f}초'.format(end - begin))

    begin = time()
    with Pool() as p:
        ret = p.map(parseOne,responses)
    end = time()

    print('Parsing 실행 시간: {0:.3f}초'.format(end - begin))

    return ret


if __name__ == "__main__":

    begin, end = 10000,10100
    loop = asyncio.get_event_loop()         
    ret = loop.run_until_complete(processParseBetweenCode(begin,end))          
    loop.close()  

    with open(f'{begin}_{end}.pickle', 'wb') as handle:
        pickle.dump(ret, handle, protocol=pickle.HIGHEST_PROTOCOL)


    
    
    