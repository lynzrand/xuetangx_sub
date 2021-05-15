import requests
import io
import os
import json
import pathlib
import pathvalidate

import time
from typing import List, Union
from pprint import pprint

chaps = ["0D16B704A478D3FB9C33DC5901307461"]

URL_BASE = "https://www.xuetangx.com"

class SessionInfo:
    def __init__(self, session_id: str, sign_id: str):
        super().__init__()
        self.session_id = session_id
        self.sign_id = sign_id


def make_video_path(id: str) -> str:
    return f"{URL_BASE}/api/v1/lms/service/subtitle_parse/?c_d={id}&lg=0"


decoder = json.JSONDecoder()

#curl 'https://next.xuetangx.com/api/v1/lms/learn/course/chapter?cid=2251770&sign=THU08091000813' -H 'Accept: application/json, text/plain, */*' -H 'xtbz: xt' -H 'Cookie: login_type=WX;sessionid=ww8nwfwhvu24ulnku658dsxbomr44pl1;'


class Video:
    name: str
    ids: List[int]

    def __init__(self, name: str, ids: List[int]):
        super().__init__()
        self.name = name
        self.ids = ids

    def __repr__(self):
        return f"Video(name: {self.name}, ids: {self.ids})"


class Chapter:
    name: str
    leaf: List[Video]

    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.leaf = []

    def __repr__(self):
        return f"Chapter(name: {self.name}, leaf: {self.leaf})"


def chapter_from_raw(chapter_info: dict) -> Chapter:
    chapter_name = chapter_info["name"]
    chapter = Chapter(chapter_name)
    for leaf in chapter_info["section_leaf_list"]:
        name = leaf["name"]
        videos = [int(video["id"]) for video in leaf["leaf_list"]]
        chapter.leaf.append(Video(name, videos))
    return chapter


def get_course_info(chapter_info: dict) -> List[Chapter]:
    raw_chapters = chapter_info["data"]["course_chapter"]
    return [chapter_from_raw(chap) for chap in raw_chapters]


def fetch_course(id: str, session: SessionInfo) -> dict:
    """
    Gets the chapter info for chapter id `id` with session `session`
    """
    print("Getting course info")
    res = requests.get(
        f"{URL_BASE}/api/v1/lms/learn/course/chapter",
        params={"cid": id,
                "sign": session.sign_id},
        cookies={
            "sessionid": session.session_id,
        },
        headers={
            "xtbz": "xt",
        })

    return decoder.decode(res.text)


def get_leaf_video_id(course_id: int, leaf_id: int,
                      session: SessionInfo) -> Union[str, None]:
    leaf_path = f"{URL_BASE}/api/v1/lms/learn/leaf_info/{course_id}/{leaf_id}/"
    print(f"Fetching {leaf_path}")
    res = requests.get(
        leaf_path,
        params={"sign": session.sign_id},
        cookies={"sessionid": session.session_id},
        headers={
            "xtbz": "xt"
        })
    res_json = decoder.decode(res.text)
    if "data" in res_json and "content_info" in res_json["data"] and "media" in res_json["data"]["content_info"] and "ccid" in res_json["data"]["content_info"]["media"]:
        return res_json["data"]["content_info"]["media"]["ccid"]
    else:
        return None


def get_subtitle(video_id: str) -> Union[List[str], None]:
    res = requests.get(
        f"{URL_BASE}/api/v1/lms/service/subtitle_parse/",
        params={
            "c_d": video_id
        })
    res_json = decoder.decode(res.text)
    if "text" in res_json:
        return res_json["text"]
    else:
        return None


def get_subtitles_and_write(course_id: int, chapters: List[Chapter],
                            target_dir: pathlib.Path, session: SessionInfo):
    # create target dir if not exist
    print("Getting subtitles")
    target_dir.mkdir(parents=True, exist_ok=True)

    for chap in chapters:
        chap_path = target_dir / chap.name
        chap_path.mkdir(parents=True, exist_ok=True)
        print(f"For chapter {chap.name}")
        for leaf in chap.leaf:
            for leaf_item in leaf.ids:
                print(f"Getting info for video {leaf.name} {leaf_item}")
                leaf_info = get_leaf_video_id(course_id, leaf_item, session)
                if leaf_info:
                    print(f"Fetching subtitles for video {leaf.name} {leaf_info}")
                    sub = get_subtitle(leaf_info)
                    if sub:
                        print(f"Writing subtitles for {leaf_info}")
                        sub_file = chap_path / pathvalidate.sanitize_filename(
                            f"{leaf_item}_{leaf.name}.txt")
                        with open(str(sub_file), "w", encoding="utf8") as f:
                            f.write("\n".join([line.strip() for line in sub]))
                    else:
                        print(f"No subtitles for {leaf_info}")
                # sleep a while
                time.sleep(0.1)


if __name__ == "__main__":
    session_id = input("Please enter your session id: ")
    sign_id = input("Please enter your sign id: ")
    session = SessionInfo(session_id, sign_id)

    course_id = input("Please enter course id: ")
    path = input("Please enter output path: ")

    chap = fetch_course(course_id, session)
    chaps = get_course_info(chap)
    pprint(chaps)
    get_subtitles_and_write(int(course_id), chaps, pathlib.Path(path), session)
