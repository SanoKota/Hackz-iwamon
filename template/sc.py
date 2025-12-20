import requests
from bs4 import BeautifulSoup
import time
import csv
#取得開始年
year_start = 2023
#取得終了年
year_end = 2024

race_id = '202306050610'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

import os

for year in range(year_start, year_end):
    # CSVファイルのパス
    csv_file_path = './data/'+str(year)+'.csv'
    
    existing_race_ids = set()
    # ファイルが存在する場合は既存のrace_idを読み込む
    if os.path.exists(csv_file_path):
        try:
            with open(csv_file_path, 'r', encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header:
                    # race_idが何列目か確認（通常は0列目）
                    try:
                        race_id_idx = header.index('race_id')
                    except ValueError:
                        race_id_idx = 0
                    
                    for row in reader:
                        if len(row) > race_id_idx:
                            existing_race_ids.add(row[race_id_idx])
        except Exception as e:
            print(f"Error reading existing CSV: {e}")

    # ファイルが存在しない場合はヘッダーを書き込む
    if not os.path.exists(csv_file_path):
        with open(csv_file_path, 'w', newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(['race_id','馬','騎手','馬番','走破時間','オッズ','通過順','着順','体重','体重変化','性','齢','斤量','上がり','人気','レース名','日付','開催','クラス','芝・ダート','距離','回り','馬場','天気','場id','場名'])

    List=[]
    #競馬場
    l=["01","02","03","04","05","06","07","08","09","10"]
    for w in range(len(l)):
        place = ""
        if l[w] == "01":
            place = "札幌"
            continue
        elif l[w] == "02":
            place = "函館"
            continue
        elif l[w] == "03":
            place = "福島"
            continue
        elif l[w] == "04":
            place = "新潟"
            continue
        elif l[w] == "05":
            place = "東京"
        elif l[w] == "06":
            place = "中山"
        elif l[w] == "07":
            place = "中京"
        elif l[w] == "08":
            place = "京都"
        elif l[w] == "09":
            place = "阪神"
        elif l[w] == "10":
            place = "小倉"
            continue

        #開催回数分ループ（最大12回）
        for z in range(6, 12):
            continueCounter = 0  # 'continue'が実行された回数をカウントするためのカウンターを追加
            #開催日数分ループ（最大12日）
            for y in range(12):
                
                if y<9:
                    race_id = str(year)+l[w]+"0"+str(z+1)+"0"+str(y+1)
                    url1="https://db.netkeiba.com/race/"+race_id
                else:
                    race_id = str(year)+l[w]+"0"+str(z+1)+str(y+1)
                    url1="https://db.netkeiba.com/race/"+race_id
                #yの更新をbreakするためのカウンター
                yBreakCounter = 0
                #レース数分ループ（12R）
                for x in range(12):
                    # サーバー負荷軽減のため待機
                    time.sleep(0.3)
                    
                    if x<9:
                        url=url1+str("0")+str(x+1)
                        current_race_id = race_id+str("0")+str(x+1)
                    else:
                        url=url1+str(x+1)
                        current_race_id = race_id+str(x+1)
                    
                    # 重複チェック
                    if current_race_id in existing_race_ids:
                        print(f"Skip existing race: {current_race_id}")
                        continue

                    try:
                        r=requests.get(url, headers=headers)
                    #リクエストを投げすぎるとエラーになることがあるため
                    #失敗したら10秒待機してリトライする
                    except requests.exceptions.RequestException as e:
                        print(f"Error: {e}")
                        print("Retrying in 10 seconds...")
                        time.sleep(10)  # 10秒待機
                        r=requests.get(url, headers=headers)
                    #バグ対策でdecode
                    soup = BeautifulSoup(r.content.decode("euc-jp", "ignore"), "html.parser")
                    soup_span = soup.find_all("span")
                    #馬の数
                    allnum=(len(soup_span)-6)/3
                    #urlにデータがあるか判定
                    if allnum < 1:
                        yBreakCounter+=1
                        print('continue: ' + url)
                        continue
                    allnum=int(allnum)
                    race_data = []
                    for num in range(allnum):
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
                            if 3*num+1 < len(soup_nowrap):
                                var = soup_nowrap[3*num+1].contents[0]
                                weight = int(var.split("(")[0])
                                weight_dif = int(var.split("(")[1][0:-1])
                        except (ValueError, IndexError):
                            weight = 0
                            weight_dif = 0
                        weight = weight
                        weight_dif = weight_dif

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
                        
                        #レースの情報
                        sur, rou, dis, con, wed = "", "", "", "", ""
                        try:
                            for idx in [8, 7, 6]:
                                try:
                                    var = soup_span[idx]
                                    text = str(var)
                                    parts = text.split("/")
                                    if len(parts) < 3:
                                        continue
                                    
                                    info_part = parts[0].split(">")[1]
                                    sur = info_part[0]
                                    rou = info_part[1]
                                    dis = info_part.split("m")[0][-4:]
                                    
                                    wed_part = parts[1].split(":")
                                    if len(wed_part) > 1:
                                        wed = wed_part[1].strip()[0]
                                        
                                    con_part = parts[2].split(":")
                                    if len(con_part) > 1:
                                        con = con_part[1].strip()[0]
                                    
                                    break
                                except (IndexError, ValueError):
                                    continue
                        except Exception:
                            pass
                        soup_smalltxt = soup.find_all("p",class_="smalltxt")
                        detail=str(soup_smalltxt).split(">")[1].split(" ")[1]
                        date=str(soup_smalltxt).split(">")[1].split(" ")[0]
                        clas=str(soup_smalltxt).split(">")[1].split(" ")[2].replace(u'\xa0', u' ').split(" ")[0]
                        title=str(soup.find_all("h1")[1]).split(">")[1].split("<")[0]

                        # G3以上のレースのみ取得するフィルタリング
                        # レース名やクラス情報に G1, G2, G3, J.G1, J.G2, J.G3 が含まれているか確認
                        # netkeibaのクラス表記やレース名表記に依存するため、複数のパターンをチェック
                        is_graded_race = False
                        target_grades = ["G1", "G2", "G3", "GI", "GII", "GIII", "J.G1", "J.G2", "J.G3"]
                        
                        # タイトルまたはクラス情報にグレードが含まれているか
                        for grade in target_grades:
                            if grade in title or grade in clas:
                                is_graded_race = True
                                break
                        
                        # G3以上でなければスキップ（ただし、同じレースの他の馬データもスキップする必要があるため、
                        # ここでcontinueすると「この馬だけスキップ」になってしまう。
                        # レース単位でスキップしたいので、ループの外側で判定するか、フラグを立てておく必要があるが、
                        # ここは馬ごとのループ内なので、is_graded_raceがFalseならこのレースの全馬データの保存をスキップする制御が必要。
                        # しかし、現在の構造では馬ごとに処理して保存しているわけではなく、
                        # 1頭ごとに race_data を作成して保存している。
                        # したがって、ここで is_graded_race が False なら continue して次の馬へ... とすると、
                        # 結局そのレースのデータは保存されない（全馬スキップされる）ので目的は達成できる。
                        # ただし、無駄なループが回ることになるので、馬ループの最初で判定して break するのが効率的。
                        
                        if not is_graded_race:
                            # このレースは対象外なので、馬ループを抜ける（次のレースへ）
                            # ただし、break すると「このレースの残りの馬」をスキップして次の処理（進捗表示など）に行く。
                            # これでOK。
                            break

                        # 安全にデータを取得
                        try:
                            horse_name = soup_txt_l[4*num].contents[1].contents[0]
                        except (IndexError, AttributeError):
                            horse_name = ""
                        
                        try:
                            jockey_name = soup_txt_l[4*num+1].contents[1].contents[0]
                        except (IndexError, AttributeError):
                            jockey_name = ""
                            
                        try:
                            horse_number = soup_txt_r[1+5*num].contents[0]
                        except (IndexError, AttributeError):
                            horse_number = ""
                            
                        try:
                            odds = soup_txt_r[3+5*num].contents[0]
                        except (IndexError, AttributeError):
                            odds = ""
                            
                        try:
                            sex = soup_tet_c[6*num].contents[0][0]
                            age = soup_tet_c[6*num].contents[0][1]
                        except (IndexError, AttributeError, TypeError):
                            sex = ""
                            age = ""
                            
                        try:
                            weight_carry = soup_tet_c[6*num+1].contents[0]
                        except (IndexError, AttributeError):
                            weight_carry = ""

                        race_data = [
                            current_race_id,
                            horse_name,#馬の名前
                            jockey_name,#騎手の名前
                            horse_number,#馬番
                            runtime,#走破時間
                            odds,#オッズ,
                            pas,#通過順
                            num+1,#着順
                            weight,#体重
                            weight_dif,#体重変化
                            sex,#性
                            age,#齢
                            weight_carry,#斤量
                            last,#上がり
                            pop,#人気,
                            title,#レース名
                            date,#日付
                            detail,
                            clas,#クラス
                            sur,#芝かダートか
                            dis,#距離
                            rou,#回り
                            con,#馬場状態
                            wed,#天気
                            w,#場
                            place]
                        
                        # G3以上の場合のみ保存
                        if is_graded_race:
                            # 1レースごとに追記
                            with open(csv_file_path, 'a', newline='', encoding="utf-8") as f:
                                csv.writer(f).writerow(race_data)
                            
                            # 追加したrace_idをセットに追加
                            existing_race_ids.add(current_race_id)
                    
                    print(detail+str(x+1)+"R")#進捗を表示
                    
                # 12レース全部ない日が検出されたら、その開催回(z)の次の開催日(y)へ進むが、
                # 連続してデータがない場合のみ開催回(z)のループを抜ける判定を行うべきだが、
                # ここでは単純にbreakせず、次の開催日を確認するように変更する。
                # ただし、あまりにも無駄なリクエストが続くのを防ぐため、
                # 「開催日(y)の全レースが存在しない」かつ「yがある程度進んでいる」場合はbreakするなどの調整も考えられるが、
                # 今回はユーザーの要望通り「早期ブレイクの見直し」として、breakを削除または条件を厳しくする。
                
                # ここではbreakを削除し、全日程をチェックするように変更する
                # if yBreakCounter == 12:
                #     break
    print("終了")

# pip install charset-normalizer
from charset_normalizer import from_bytes
b = open("data/2023.csv","rb").read()
match = from_bytes(b).best()
if match is None:
    print("Encoding detection: no match found")
else:
    # Print the match object and the detected encoding (safe attributes)
    print(match)
    try:
        print("detected encoding:", match.encoding)
    except Exception:
        pass
