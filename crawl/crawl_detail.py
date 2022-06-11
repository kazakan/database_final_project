import asyncio
from time import time
from typing import List
from bs4 import BeautifulSoup
from multiprocessing import Pool
import traceback
import pickle
import sys

def readFile(code):
    try :
        f = open(f"./htmls/{code}.html",'r')
        data = f.read()
        f.close()
        return data
    except Exception as e:
        traceback.print_exception(e)
        return None

async def getMovieDirectorActorPage(code):
    result = await loop.run_in_executor(None,readFile,code)
    return result

# async def getMovieReview(code,pageNum):
#     result = await loop.run_in_executor(
#         None, 
#         requests.get,
#         f"https://movie.naver.com/movie/bi/mi/pointWriteFormList.naver?code={code}&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false&page={pageNum}"
#     )
#     return result

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
        year = year.strip()

        if year.isnumeric():
            ret['year'] = int(year)            


    # parse from info_spec
    soup_info_spec : BeautifulSoup = soup_my_info.find("dl","info_spec")

    # first dd in infospec
    # genres | nation | minute (optional) | release (optional)
 

    def parseSpan(span : BeautifulSoup):
        stringfy_span = str(span)
        if("N=a:ifo.genre" in stringfy_span): # genre
            a_summary : List[BeautifulSoup] = span.find_all("a")
            ret['summarys'] = [t.text for t in a_summary]
        elif("N=a:ifo.nation" in stringfy_span): #nation
            a_country : List[BeautifulSoup] = span.find_all("a")
            ret['nation'] = [t.text for t in a_country]
        elif("분" in stringfy_span): #minute
            ret['minute'] = span.text.strip()[:-1]
        elif("N=a:ifo.day" in stringfy_span): # release date
            ret["date"] = span.find_all("a")[-1].text.strip('.')

    dts = soup_info_spec.find_all('dt')
    dds = soup_info_spec.find_all('dd')

    for dt, dd in zip(dts,dds):
        if "개요" in dt.text:
            dd1_spans : List[BeautifulSoup] = dd.select("span")
    
            for span in dd1_spans:
                parseSpan(span)

        elif "등급" in dt.text:
            _grade = []
            for a in dd.select('a'):
                if 'grade' in str(a):
                    _grade.append(a.text)
            ret["grade"] = _grade

        elif "감독" in dt.text:
            _directors = []
            for a in dd.select('a'):
                _directors.append(a.text)
            ret["director_short"] = _directors

                
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
        if img_director is not None:
            data['img'] = img_director['src']
        
        dir_obj_a = dir_obj.select_one(".dir_product > a:nth-child(1)",href=True)

        if dir_obj_a is not None:
            if dir_obj_a.has_attr('href'):
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
            continue
            
        p_obj_a = p_obj.select_one("a:nth-child(1)",href=True)
        if p_obj_a is None or not p_obj_a.has_attr('href'):
            continue

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

def parseOne(pageText : str):
        if(pageText is None) : return None
        if("영화 코드값 오류입니다" in pageText): return None
        
        bs = BeautifulSoup(pageText,'html.parser')
        
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

    with Pool() as p:
        ret = p.map(parseOne,responses)


    return ret


if __name__ == "__main__":

    start, end, step = 10000,20000,1000

    if len(sys.argv) >= 3:
        start = int(sys.argv[1]) if sys.argv[1] else 10000
        end = int(sys.argv[2]) if sys.argv[2] else 20000
    if len(sys.argv) >= 4:
        step = int(sys.argv[3]) if sys.argv[2] else 1000

    nChunk = (end-start) // step + (1 if (end-start) % step > 0 else 0)

    t_begin = time()

    for idx,chunk_start in enumerate(range(start,end,step)):

        chunk_end = chunk_start+step
        if chunk_end > end: chunk_end = end

        
        print(f"Processing {chunk_start}~{chunk_end} | {round(idx/nChunk * 100,4)}% | {idx} / {nChunk} | time ellapsed {int(time() - t_begin)} sec",end="\r")

        loop = asyncio.get_event_loop()       
        ret = loop.run_until_complete(processParseBetweenCode(chunk_start,chunk_end)) 

        with open(f'./out/{chunk_start}_{chunk_end}_crawled.pickle', 'wb') as handle:
            pickle.dump(ret, handle, protocol=pickle.HIGHEST_PROTOCOL)
                 
    loop.close()  

    print(f"\nDone! {start}~{end}, Time ellapsed = {int(time() - t_begin)} sec")

