import asyncio
from time import time
import requests
import sys


async def getMovieDirectorActorPage(code):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, requests.get,f"https://movie.naver.com/movie/bi/mi/detail.naver?code={code}")
    return result

async def main(begin,end, step):

    for chunk_begin in range(begin,end,step):
        chunk_end = chunk_begin + step
        if chunk_end > end : chunk_end = end

        print(f"Code {chunk_begin}~{chunk_end-1} 작업중...")

        codes = range(chunk_begin,chunk_end)
        t_begin = time()
        responses_future = [asyncio.ensure_future(getMovieDirectorActorPage(code)) for code in codes]
        responses = await asyncio.gather(*responses_future)
        t_end = time()

        print('다운 실행 시간: {0:.3f}초'.format(t_end - t_begin))

        t_begin = time()

        for idx, res in enumerate(responses):
            c = idx + begin

            with open(f"./htmls/{c}.html",'wb') as file:
                file.write(res.content)

        t_end = time()

        print('저장 실행 시간: {0:.3f}초'.format(t_end - t_begin))

if __name__ == "__main__":
    begin , end, step = 10000, 10010 ,1

    if len(sys.argv) >= 4:
        begin = int(sys.argv[1]) if sys.argv[1] else 10000
        end = int(sys.argv[2]) if sys.argv[2] else 10010
        step =int(sys.argv[3]) if sys.argv[3] else 10010

    loop = asyncio.new_event_loop()       
    ret = loop.run_until_complete(main(begin,end,step))          
    loop.close()  
