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
        f = open(f"./htmls/{code}_basic.html",'r')
        data = f.read()
        f.close()
        return data
    except Exception as e:
        traceback.print_exception(e)
        return None

async def getMovieBasicPage(code):
    result = await loop.run_in_executor(None,readFile,code)
    return result


def parseSectionGroup(pageSoup : BeautifulSoup):
    ret = {}
    div_objSections = pageSoup.select("div.obj_section")
    

    def parseObjSection(objSectionSoup : BeautifulSoup):

        story_area = objSectionSoup.select_one('div.story_area')
        if story_area is not None:
            con_tx = story_area.select_one("p.con_tx")
            if con_tx is not None:
                ret['story'] = con_tx.text
            return

        comment_list = objSectionSoup.select(".score_result > ul:nth-child(1) > li")
        comments = []
        if len(comment_list > 0):
            for li in comment_list:
                cmt = {}

                em = li.select_one("em:nth-child(2)")
                if em is not None:
                    cmt['star'] = int(em.text)

                reple = li.select_one("div:nth-child(2) > p:nth-child(1)")
                if reple is not None:
                    cmt['reple'] = reple.text

                good = li.select_one("a._sympathyButton > strong")
                if good is not None:
                    cmt['good'] = int(good.text)

                bad = li.select_one("a._notSympathyButton > strong")
                if good is not None:
                    cmt['bad'] = int(bad.text)

                if len(cmt.keys()) > 0:
                    comments.append(cmt)

            ret['comments'] = comments
                
        
    for objsection in div_objSections:
        parseObjSection(objsection)

    if len(ret.keys()) > 0 :
        return ret
    return None


def crawlOnePage(page : BeautifulSoup):
    result = {}

    if(page is None):
        return None

    result = parseSectionGroup(page)

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
    responses_future = [asyncio.ensure_future(getMovieBasicPage(code)) for code in codes]
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

