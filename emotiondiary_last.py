import streamlit as st
import json
import pandas as pd
import random
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime

SPREADSHEET_ID = "1kbAcy_jV_AM-PGAZN2hfaIw0auDyrhm1gcrPuKcVC-s"
SHEET_NAME = "emotiongirok"

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["google_service_account"],
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
service = build('sheets', 'v4', credentials=credentials)

def save_score_to_sheets(score, emotion):
    values = [[score, emotion]]
    body = {"values": values}
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="시트1!A:B",  # 또는 A2
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()

st.markdown(
    """
    <style>
    /* 배경 애니메이션 */
    @keyframes gradientBG {
      0% {
        background-position: 0% 50%;
      }
      50% {
        background-position: 100% 50%;
      }
      100% {
        background-position: 0% 50%;
      }
    }
    .stApp {
      background: linear-gradient(-45deg, #fce4ec, #f8bbd0, #AFDDFF, #E8F9FF);
      background-size: 400% 400%;
      animation: gradientBG 15s ease infinite;
      color: white;
    }

    /* 상단 헤더 투명 처리 */
    [data-testid="stHeader"] {
      background-color: rgba(0, 0, 0, 0) !important;
      box-shadow: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# 감성어 사전 불러오기
with open('SentiWord_info.json', encoding='utf-8-sig') as f:
    SentiWord_info = json.load(f)

sentiword_dic = pd.DataFrame(SentiWord_info)

# 감정 점수 계산 함수 (점수 범위 -2~2 → 1~10 점수 변환)
def calculate_sentiment(text):
    total_score = 0
    count = 0

    # 단어 길이 내림차순 정렬(긴 단어부터 처리)
    sorted_dic = sentiword_dic.sort_values(by='word', key=lambda x: x.str.len(), ascending=False)

    text_copy = text  # 텍스트 복사본

    for _, row in sorted_dic.iterrows():
        word = row['word']
        polarity = row['polarity']
        if word in text_copy:
            try:
                score = float(polarity)
            except:
                score = 0
            total_score += score
            count += 1
            text_copy = text_copy.replace(word, "")  # 중복 처리 방지

    if count == 0:
        return 5  # 단어 없으면 중립(10단계 중 중간 값 5점)

    avg_score = total_score / count

    # 점수 변환: -2~2 범위 → 1~10 점수
    sentiment_score = int(round((avg_score + 2) * (9 / 4) + 1))
    sentiment_score = max(1, min(sentiment_score, 10))

    return sentiment_score

# 점수별 노래 리스트 (예시: 제목, 가수, Spotify 링크)
songs_by_score = {
    1: [
        ("괜찮아도 괜찮아", "도경수(D.O.)", "https://youtu.be/j2aQ_NqeTNw?si=GUt2Ru_R5ZmmeyyN"),
        ("Track 9", "이소라", "https://youtu.be/MjQjaB-HedA?si=iAFFPu6cdumVZuQq"),
        ("Live, Laugh, Love", "Ade Parker", "https://youtu.be/pkK_8xY2spg?si=vrSsPYIwXJrRLx3S"),
        ("Karma", "AJR", "https://youtu.be/Vy1JwiXHwI4?si=5AN0rpotQjI3uuLR"),
        ("내가 죽으려고 생각한 것은", "amazarashi", "https://youtu.be/_hcvGjy2v18?si=4_YfeKuG_GRbc1bI"),
        ("Komm, Susser Tod", "Arianne", "https://youtu.be/hoKluzn07eQ?si=4tojq1k0oxdZtMQe"),
        ("Your Power", "Billie Eilish", "https://youtu.be/BPp4doFEkYE?si=M3q_bHnrqifZrSJu"),
        ("Courage to Change", "Sia", "https://youtu.be/mWQACEqf4QY?si=KiCoegjeqAd4CYaM"),
        ("STILL ALIVE", "BIGBANG(빅뱅)", "https://youtu.be/HY8G_hsuhDs?si=s6moDSW7x83ijPgn"),
        ("기댈곳", "싸이(PSY)", "https://youtu.be/7goHyFzym2I?si=DP2WTIlWLfGJ_TuF"),
        ("Beautiful", "NCT 2021", "https://youtu.be/nAvjYapdSxk?si=XnNAun9azgLP65rI"),
        ("비상", "임재범", "https://youtu.be/hfaLDzIB81k?si=TxodxaEJ-VN4IJkv"),
        ("문", "강승윤, MINO", "https://youtu.be/M0F5fyQwCdQ?si=dKIp2cvdx6585-wA"),
        ("Try", "Colbie Caillat", "https://youtu.be/GXoZLPSw8U8?si=lzClFISSiyl9LAMQ"),
        ("허물", "VINXEN(빈첸)", "https://youtu.be/5MYwjCgnkJs?si=pJ0-TVnG6XfpCjOi"),

    ],
    2: [
        ("Lost Stars", "Adam Levine", "https://youtu.be/cL4uhaQ58Rk?si=fw89fvmNtVLY1qgm"),
        ("Toxic", "BoyWithUke", "https://youtu.be/Mvaosumc4hU?si=mKK1tp9ugIrWcxOt"),
        ("위잉위잉", "혁오", "https://youtu.be/D6dqkvR4F9g?si=wWm_SdHZFD5xE4kf"),
        ("Older", "Alec benjamin", "https://youtu.be/2v7djBZFrfE?si=QyMTUBcjBkynES99"),
        ("난로", "LUCY(루시)", "https://youtu.be/jjhep_yVTCE?si=3nj67bKMuCd5KK5S"),
        ("궤도(Orbit_)", "ONEWE(원위)", "https://youtu.be/v43CpZxE_0E?si=TFE52Rs9XemLbAI2"),
        ("지나갈 테니", "EXO", "https://youtu.be/6WOzJF-7mrc?si=MChWIzQFLtva3Qto"),
        ("Alone", "Marshmello", "https://youtu.be/ALZHF5UqnU4?si=v18-lkICpDfZryJD"),
        ("우르르 쾅쾅쾅", "스텔라장", "https://youtu.be/MXY08fPiqdA?si=kAuhtbNgnzn0zRqT"),
        ("우물 속 작은 아이", "ONEWE(원위)", "https://youtu.be/FgT_RxAZuzw?si=3jwyPEPaSBBoVtOB"),
        ("Zombie", "DAY6(데이식스)", "https://youtu.be/k8gx-C7GCGU?si=v8-o3BD7oNmJ9Dmo"),
    ],
    3: [
        ("Missing You", "G-DRAGON", "https://youtu.be/XNSmuTpzr8U?si=0qtXboNaHfmF2CFq"),
        ("3.6.5", "EXO", "https://youtu.be/0X39D9goPqc?si=7Dd8AZgqL5ufQ8VJ"),
        ("Youth", "기현", "https://youtu.be/0OliiOgXlJI?si=h0eF595sEmAMSFJ8"),
        ("빛이 나는 너에게", "던(DAWN)", "https://youtu.be/kRCssNJtZ4c?si=olhlv3xQ-CHraThO"),
        ("Baby V.O.X", "Killer", "https://youtu.be/X2blHAOzTYg?si=_BDAIFdlJyctiWNp"),
        ("Falling Slowly", "대성", "https://youtu.be/guQeMg5g_yc?si=6I0Xp5rSMlescJOz"),
        ("stan", "Eminem", "https://youtu.be/7u1Jj6aRIec?si=xbFUAQV69goNj63v"),
        ("맹그로브", "윤하", "https://youtu.be/The_R7jYQ8o?si=xVx0bcjzCEOIsb4S"),
        ("형", "노라조", "https://youtu.be/aGvTFU7NP8I?si=_Qxo0k9BWe6Q_auo"),
        ("셀 수 없는", "SHINEE(샤이니)", "https://youtu.be/6lE0AJzOb-I?si=e9dOn622UnWSmJSl"),
        ("재연", "SHINEE(샤이니)", "https://youtu.be/yp-zkC2aXv0?si=RU7QZWPR5y1yUgrD"),
        ("얼음틀", "AKMU(악뮤)", "https://youtu.be/sUCIzn0mRHc?si=FQkGJKrEu4hWDTd5"),
        ("75분의 1초(Moment)", "수호", "https://youtu.be/39bZ0Eq8H1g?si=7gX2TvREIABGQZvg"),
        ("Be Kind", "Marshmello, Halsey", "https://youtu.be/n7eq3E9zE2Y?si=w4zD-VV07_JJrliA"),
    ],
    4: [
        ("Fly", "에픽하이(EPIK HIGH)", "https://youtu.be/8kw-RXHSyAo?si=NT1tp2ptOYwxFEpK"),
        ("Painkiller", "Rue1", "https://youtu.be/3YHGEuefsbI?si=dPt6P-EPE6B_2PoN"),
        ("크림소스 파스타", "윤하", "https://youtu.be/MicrnoPopM4?si=pOAhS4i2reAvSeZA"),
        ("매직 카펫 라이드", "자우림", "https://youtu.be/JUdwUb6QN5w?si=YNyBja-0sY8Pmb_C"),
        ("시시한 청춘에 남기는 노래", "음율", "https://youtu.be/oj3iiOs6bSk?si=ZqkrKRW0xDJUGFrS"),
        ("MOVIE", "JUNNY(주니)", "https://youtu.be/ZWYVrUrsvIA?si=kIf_2jI8x3X1bF9z"),
        ("내버려(So What)", "LUCY(루시)", "https://youtu.be/mFETJWbutgM?si=Rt3gI5gR8wE0Kaa7"),
        ("Crazy", "케빈오", "https://youtu.be/ozrDzqDWBEo?si=PvKL33LTEkFU7MAU"),
        ("oh My Friend", "BIGBANG(빅뱅)", "https://youtu.be/HT1By1zHZjM?si=rnT8M_DbpRVdXsVU"),
        ("낮과 밤", "태민", "https://youtu.be/yr_OsRLDj1E?si=4VziBN5gFK3dKt50"),
        ("St Myself On Fire", "태연", "https://youtu.be/U03r-YzpOjg?si=1ZEI1UBaVt3iWIfF"),
    ],
    5: [
        ("Steal The Show", "Lauv", "https://youtu.be/DwuJeGYlYyw?si=VFdeZBMRjJIwwhrI"),
        ("parachute", "john K", "https://youtu.be/d8UAqPZ7d90?si=cAYeLDT15LLK_zS2"),
        ("By your Side", "Crush", "https://youtu.be/rgDmqJS1S7I?si=UOmbsm9NRgRtcudq"),
        ("Love Again", "백현", "https://youtu.be/gAJkUetwS4Y?si=tss_p1yrhbJ9-Wfa"),
        ("STAR WALKIN'", "Lil Nas X", "https://youtu.be/Zrly3QMUhoo?si=UOMpZbPJ1KeA2Da0"),
        ("Summertime", "뎁트", "https://youtu.be/ttJ0I8vv4ts?si=_e2mysbLXbHsMdpR"),
        ("투명우산", "SHINEE(샤이니)", "https://youtu.be/LV3vxkZpUjk?si=o9hjy_-rLv_QiKwS"),
        ("데자부", "드림캐쳐", "https://youtu.be/W761DtH1oRg?si=3Z44zU-OsFEIF-ll"),
        ("고래", "AKMU(악뮤)", "https://youtu.be/huj809wLjAU?si=VTIgTbAyjL8onTp1"),
        ("휴일(Lazy)'", "EXO-CBX(첸백시)", "https://youtu.be/7EkqycevH58?si=U3jAb6Cbi6EJolob"),
        ("Dazzling", "POW(파우)", "https://youtu.be/vQ21mMH8Yps?si=qnrqt7fgfvTic44n"),
        ("What Makes YOu Beautiful", "One Direction", "https://youtu.be/UlANZSYZ2Js?si=1JSPdBlvfB4rZIo4"),
        ("비밀의 화원", "이상은", "https://youtu.be/TY0PA68gBXE?si=r7eKnp_YQdb8trOM")
    ],
    6: [
        ("Blue Moon", "엔플라잉", "https://youtu.be/_8SnRN0114k?si=n0dLmSmp0X3pMjKp"),
        ("View", "SHINEE(샤이니)", "https://youtu.be/UF53cptEE5k?si=nFoNYp4V0WQJjLN_"),
        ("I'm born to run", "American Authers", "https://youtu.be/kb901KsDtjo?si=iy3e3Acad2H90rWa"),
        ("Checklist", "MAX", "https://youtu.be/Jcvi0iHiWnw?si=jbhRLIBK7fHwQ6iX"),
        ("Inferno", "Mrs. GREEN APPLE", "https://youtu.be/wfCcs0vLysk?si=Fm952-q7ZpATHdxU"),
        ("Trip", "릴러말즈", "https://youtu.be/5C-UzW1FLiA?si=JMTIzQmvLSPbwwIb"),
        ("Love or Die", "CRAVITY", "https://youtu.be/nnBiA1iq8r0?si=Wb0Zw_KaZ8H7hKyr"),
        ("Notion", "THe Rare Occasion", "https://youtu.be/PD1EXJScA6k?si=bmzzLFCQgsiOBDsG"),
    ],
    7: [
        ("녹아내려요", "DAY6(데이식스)", "https://youtu.be/yss4rIrHl6o?si=EOC2VvPSyni2yf8Q"),
        ("만화영화", "지코(ZICO)", "https://youtu.be/nnq7_E_Tzlw?si=TKZCzJGPFsbbh99V"),
        ("Hero(히어로)", "LUCY(루시)", "https://youtu.be/RTiBP4OygiE?si=aX4UT4tIGr2XxVDG"),
        ("Good Guy", "SF9", "https://youtu.be/n8zQysKciao?si=y79ATOL3JMtgjzlS"),
        ("동문서답", "LUCY(루시)", "https://youtu.be/rYwRr0mV5UY?si=Q8gU5vV7ArQBMepp"),
        ("love Like This(네게로)", "SS501", "https://youtu.be/QNycfS3NbXE?si=UB_7Np0XmxAW30lQ"),
        ("괴짜", "지코(ZICO)", "https://youtu.be/JEXsNICXdrc?si=cPsXFX1yUVs0_JJr"),
        ("Summertime", "Dept(뎁트)", "https://youtu.be/0mAJXqaeF8c?si=k0BdqdJINJXby9Ok"),
        ("Favorite", "POW(파우)", "https://youtu.be/SYoTbANl9Eg?si=a1FND_XeYxqctuBl"),
        ("Love ME LOVE ME", "WINNER", "https://youtu.be/ppOWR7ZLl7Q?si=ZwYCgDi_RPepmSz6"),
    ],
    8: [
        ("에라 모르겠다", "BIGBANG", "https://youtu.be/iIPH8LFYFRk?si=K6esyTV2cU3FkUcQ"),
        ("행운을 빌어요", "페퍼톤스", "https://youtu.be/U6dTSMCqlp4?si=gpkVvRjuh7_tzNVQ"),
        ("sweet chaos", "DAY6(데이식스)", "https://youtu.be/PEJe3uJCXYA?si=hQ9AVd5jomLl6Fhy"),
        ("베로니카의 섬", "ONEWE(원위)", "https://youtu.be/6LD2U_ez5tc?si=6IyjHJnwDbxQIWlL"),
        ("You Prlblem", "몬스타엑스", "https://youtu.be/ZJ5GEmAPlHY?si=lWk9h9qy-oqBeBlp"),
        ("Oscar", "pH-1,지소울,BIG Naughty,박재범", "https://youtu.be/6E5W2vg_hU4?si=pd4qj5V0Aomjq1jE"),
        ("Memories", "YUNGBLUD", "https://youtu.be/MFzq4_qCFUQ?si=mDgbPKhYw9RuUMJX"),
        ("하늘을 달리다", "이적", "https://youtu.be/cNFs-FRrdJg?si=RJnIsUvbP2VDdbbn"),
        ("Immortals", "Fall Out Boy", "https://youtu.be/Y4o_8zbelwY?si=hT7uWNF6FPVlXRSa"),
    ],
    9: [
        ("HAPPY", "DAY6(데이식스)", "https://youtu.be/2o1zdX72400?si=yqXU7uIt0mlPR9u6"),
        ("OFF ROAD", "ONEWE(원위)", "https://youtu.be/kQnFUpLEYFM?si=siHabtnPtHqci8Dh"),
        ("very good", "블락비(Block B)", "https://youtu.be/kJGcO5Une-g?si=DIFh4U78RGEorHYs"),
        ("Baby", "ASTRO(아스트로)", "https://youtu.be/IwqEXtsvaDg?si=AqJRRTOuAdJ-ah77"),
        ("JACKPOT", "블락비(Block B)", "https://youtu.be/83Yscg5vtVQ?si=bisZrYbsapm8ioKN"),
        ("Travel(여행)", "BOL4(볼빨간 사춘기)", "https://youtu.be/xRbPAVnqtcs?si=Yo96eRHqwFVjNKZ3"),
    ],
    10: [
        ("Happy", "Mocca", "https://youtu.be/HduKGO9oPPI?si=5TQfXo9mR_wDuxgZ"),
        ("뜨거운 감자", "N.Flying(엔플라잉)", "https://youtu.be/y1iRckD1ys4?si=Ls0vK8Wu2DmfVs10"),
        ("WISH", "NCT WISH", "https://youtu.be/hvQZs3k6Ytk?si=pkoraRA5SIg1pICn"),
        ("Uptown Funk", "Mark Ronson", "https://youtu.be/OPf0YbXqDm0?si=zIi3LkL6ZrkwzTXk"),
        ("Dancing King", "유재석×EXO", "https://youtu.be/4EiNsoTc9kk?si=6s4fDULWAP0bBFJ0"),
        ("SODA POP", "사자 보이즈(Saja Boys)", "https://youtu.be/eny0BqmSwmM?si=_5CElznr2jJreQQO"),
        ("로꾸꺼", "슈퍼주니어-T", "https://youtu.be/K2CNJiAq_cY?si=avsusY3j0l5GrDG8"),
        ("날봐 귀순", "대성", "https://youtu.be/OGSUsOoOhpI?si=sfGxGdjPmWcDJQGV"),

    ],
}

def recommend_song(score):
    if score in songs_by_score:
        song = random.choice(songs_by_score[score])
        title, artist, link = song
        youtube_icon = "https://upload.wikimedia.org/wikipedia/commons/4/42/YouTube_icon_%282013-2017%29.png"
        return f"""
        🎵 <a href="{link}" target="_blank" style="text-decoration: none; color: inherit;">
            {title} - {artist}
        </a>
        <img src="{youtube_icon}" alt="YouTube" width="20" style="vertical-align:middle; margin-left:6px;">
        """
    else:
        return "🎵 추천할 노래가 없습니다."







# Streamlit UI
st.title("감정일기 분석 & 노래 추천")

user_input = st.text_area("오늘 하루를 일기로 적어주세요 👇", height=200)

st.markdown(
    "<p style='font-size:12px; color:red;'>※ 입력하신 일기 내용과 사용자의 정보는 저장되지 않으며, 감정 분석 결과만 저장됩니다. ※</p>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='font-size:12px; color:red;'>※ 오류가 있을 수 있습니다. 양해 부탁드립니다. 또한 욕설은 인식하지 않습니다. ※</p>",
    unsafe_allow_html=True
)

if st.button("감정 분석 시작"):
    if user_input.strip() == "":
        st.warning("내용을 입력해주세요.")
    else:
        score = calculate_sentiment(user_input)

        emotions = {
            1: "😢 매우 부정", 2: "🙁 부정", 3: "😟 조금 부정", 4: "😕 약간 부정",
            5: "😐 중립", 6: "🙂 약간 긍정", 7: "😊 긍정", 8: "😄 매우 긍정",
            9: "🤩 극도로 긍정", 10: "🥳 최고로 긍정"
        }
        emotion = emotions.get(score, "알 수 없음")  # 여기서 emotion 정의

        st.subheader("감정 분석 결과")
        st.write(f"감정 점수 (1~10): **{score}점**")
        st.write(f"예측 감정: {emotion}")

        st.subheader("노래 추천 🎶")
        st.markdown(recommend_song(score), unsafe_allow_html=True)

        # 구글 시트 저장
        save_score_to_sheets(score, emotion)
        st.success("서버에 감정 점수와 감정이 저장되었습니다. 일기 내용은 저장되지 않습니다")


