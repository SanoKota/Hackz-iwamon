import requests
from bs4 import BeautifulSoup
import time

# URL for debug
url = "https://db.netkeiba.com/race/list/2023122411"
current_race_id = "2023122411"" # Dummy ID

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
print(f"Fetching {url} with headers...")

try:
    r = requests.get(url, headers=headers)
    print(f"Status Code: {r.status_code}")
    
    # バグ対策でdecode
    soup = BeautifulSoup(r.content.decode("euc-jp", "ignore"), "html.parser")
    
    soup_span = soup.find_all("span")
    print(f"Number of spans: {len(soup_span)}")
    
    #馬の数
    allnum=(len(soup_span)-6)/3
    print(f"Calculated allnum: {allnum}")
    
    if allnum < 1:
        print("Data not found (allnum < 1)")
    else:
        print("Data found! Extracting...")
        allnum = int(allnum)
        
        # レース情報の取得 (sc.pyから抜粋・調整)
        try:
            soup_smalltxt = soup.find_all("p",class_="smalltxt")
            if soup_smalltxt:
                detail=str(soup_smalltxt).split(">")[1].split(" ")[1]
                date=str(soup_smalltxt).split(">")[1].split(" ")[0]
                clas=str(soup_smalltxt).split(">")[1].split(" ")[2].replace(u'\xa0', u' ').split(" ")[0]
            else:
                detail, date, clas = "Unknown", "Unknown", "Unknown"
                
            title_tag = soup.find_all("h1")
            if len(title_tag) > 1:
                title=str(title_tag[1]).split(">")[1].split("<")[0]
            else:
                title = "Unknown"
            
            # レース詳細情報（距離、天気など）
            sur, rou, dis, con, wed = "Unknown", "Unknown", "Unknown", "Unknown", "Unknown"
            try:
                var = soup_span[8]
                sur=str(var).split("/")[0].split(">")[1][0]
                rou=str(var).split("/")[0].split(">")[1][1]
                dis=str(var).split("/")[0].split(">")[1].split("m")[0][-4:]
                con=str(var).split("/")[2].split(":")[1][1]
                wed=str(var).split("/")[1].split(":")[1][1]
            except IndexError:
                try:
                    var = soup_span[7]
                    sur=str(var).split("/")[0].split(">")[1][0]
                    rou=str(var).split("/")[0].split(">")[1][1]
                    dis=str(var).split("/")[0].split(">")[1].split("m")[0][-4:]
                    con=str(var).split("/")[2].split(":")[1][1]
                    wed=str(var).split("/")[1].split(":")[1][1]
                except IndexError:
                    try:
                        var = soup_span[6]
                        sur=str(var).split("/")[0].split(">")[1][0]
                        rou=str(var).split("/")[0].split(">")[1][1]
                        dis=str(var).split("/")[0].split(">")[1].split("m")[0][-4:]
                        con=str(var).split("/")[2].split(":")[1][1]
                        wed=str(var).split("/")[1].split(":")[1][1]
                    except:
                        pass

            print(f"Race Info: {title} | {date} | {detail} | {clas} | {sur}/{rou}/{dis}m | {con} | {wed}")

        except Exception as e:
            print(f"Error parsing race info: {e}")

        # 馬ごとのループ
        for num in range(allnum):
            try:
                #馬の情報
                soup_txt_l=soup.find_all(class_="txt_l")
                soup_txt_r=soup.find_all(class_="txt_r")
                
                #走破時間
                runtime=''
                try:
                    runtime=soup_txt_r[2+5*num].contents[0]
                except IndexError:
                    runtime = ''
                
                soup_nowrap = soup.find_all("td",nowrap="nowrap",class_=None)
                
                #通過順
                pas = ''
                try:
                    pas = str(soup_nowrap[3*num].contents[0])
                except:
                    pas = ''
                
                weight = 0
                weight_dif = 0
                #体重
                try:
                    var = soup_nowrap[3*num+1].contents[0]
                    weight = int(var.split("(")[0])
                    weight_dif = int(var.split("(")[1][0:-1])
                except (ValueError, IndexError):
                    weight = 0
                    weight_dif = 0

                soup_tet_c = soup.find_all("td",nowrap="nowrap",class_="txt_c")
                
                #上がり
                last = ''
                try:
                    last = soup_tet_c[6*num+3].contents[0].contents[0]
                except IndexError:
                    last = ''
                
                #人気
                pop = ''
                try:
                    pop = soup_span[3*num+10].contents[0]
                except IndexError:
                    pop = ''

                # 馬名、騎手など
                horse_name = soup_txt_l[4*num].contents[1].contents[0]
                jockey_name = soup_txt_l[4*num+1].contents[1].contents[0]
                horse_number = soup_txt_r[1+5*num].contents[0]
                odds = soup_txt_r[3+5*num].contents[0]
                rank = num + 1
                
                sex = soup_tet_c[6*num].contents[0][0]
                age = soup_tet_c[6*num].contents[0][1]
                weight_carry = soup_tet_c[6*num+1].contents[0]

                print("-" * 20)
                print(f"着順: {rank}")
                print(f"馬名: {horse_name}")
                print(f"騎手: {jockey_name}")
                print(f"馬番: {horse_number}")
                print(f"タイム: {runtime}")
                print(f"オッズ: {odds}")
                print(f"通過: {pas}")
                print(f"体重: {weight} ({weight_dif})")
                print(f"性齢: {sex}{age}")
                print(f"斤量: {weight_carry}")
                print(f"上がり: {last}")
                print(f"人気: {pop}")

            except Exception as e:
                print(f"Error parsing horse {num+1}: {e}")

except Exception as e:
    print(f"Global Error: {e}")
