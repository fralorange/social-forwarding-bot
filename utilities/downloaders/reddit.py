import re
import aiohttp
import asyncio
from tempfile import NamedTemporaryFile
from moviepy.editor import VideoFileClip, AudioFileClip

USER_AGENT = 'Mozilla/5.0 (compatible; SocialForwarder/1.0)'

async def normalize_reddit_post_url_async(url: str) -> str:
    """
    Normalizes reddit post url address asynchronously.
    """
    headers = {'User-Agent': USER_AGENT}
    url_base = url.split('?')[0]

    async with aiohttp.ClientSession(headers=headers) as session:
        if 'redd.it' in url_base or re.search(r'/s', url_base):
            async with session.get(url_base, allow_redirects=True) as resp:
                resp.raise_for_status()
                final_url = str(resp.url)
        else:
            final_url = url_base

    if '/comments' not in final_url:
        raise ValueError(f'Reddit post could not be identified: {final_url}')

    return final_url.split('?')[0].rstrip('/')


async def download_reddit_post_async(url: str) -> bytes:
    """
    Downloads reddit post and returns byte array asynchronously.
    """
    headers = {'User-Agent': USER_AGENT}
    full_url = await normalize_reddit_post_url_async(url)
    json_url = full_url + '.json'

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(json_url) as resp:
            resp.raise_for_status()
            meta = await resp.json()

        try:
            video_info = meta[0]['data']['children'][0]['data']['secure_media']['reddit_video']
            video_url : str = video_info['fallback_url']
            dash_url = video_info.get('dash_url')
            if not dash_url:
                raise RuntimeError("DASH manifest not found.")
        except (KeyError, IndexError, TypeError):
            raise RuntimeError("No video was found or it's not on Reddit.")

        async with session.get(video_url) as video_resp:
            video_resp.raise_for_status()
            video_bytes = await video_resp.read()
        
        async with session.get(dash_url) as dash_resp:
            dash_resp.raise_for_status()
            dash_xml = await dash_resp.text()

        audio_url = extract_audio_url_from_mpd(dash_xml, dash_url)

        if not audio_url:
            return video_bytes
        
        async with session.get(audio_url) as audio_resp:
            if audio_resp.status != 200:
                return video_bytes
            audio_bytes = await audio_resp.read()
        
        combined_bytes = await asyncio.to_thread(combine_video_audio, video_bytes, audio_bytes)
        return combined_bytes 
    
def extract_audio_url_from_mpd(mpd_content: str, dash_url: str) -> str | None:
    """
    Extracts the audio reference from the MPD (DASH manifest).
    """
    import xml.etree.ElementTree as ET
    from urllib.parse import urljoin

    try:
        ns = {'ns': 'urn:mpeg:dash:schema:mpd:2011'}
        root = ET.fromstring(mpd_content)

        for adaptation_set in root.findall(".//ns:AdaptationSet", ns):
            if adaptation_set.attrib.get("contentType") == "audio":
                best_audio = None
                best_bandwidth = 0

                for representation in adaptation_set.findall("ns:Representation", ns):
                    base_url_elem = representation.find("ns:BaseURL", ns)
                    if base_url_elem is not None:
                        bandwidth = int(representation.attrib.get("bandwidth", "0"))
                        if bandwidth > best_bandwidth:
                            best_audio = base_url_elem.text
                            best_bandwidth = bandwidth

                if best_audio:
                    return urljoin(dash_url, best_audio)

    except ET.ParseError:
        return None
    return None

def combine_video_audio(video_bytes: bytes, audio_bytes: bytes) -> bytes:
    """
    Combines video and audio from byte arrays using MoviePy.
    Returns the combined video as bytes.
    """
    with NamedTemporaryFile(suffix='.mp4', delete=False) as video_file:
        video_file.write(video_bytes)
        video_file.flush()
        video_path = video_file.name

    with NamedTemporaryFile(suffix='.mp3', delete=False) as audio_file:
        audio_file.write(audio_bytes)
        audio_file.flush()
        audio_path = audio_file.name

    try:
        video_clip = VideoFileClip(video_path)
        audio_clip = AudioFileClip(audio_path)

        final_clip = video_clip.set_audio(audio_clip)

        with NamedTemporaryFile(suffix='.mp4', delete=False) as output_file:
            output_path = output_file.name

        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            logger=None
        )

        with open(output_path, 'rb') as f:
            combined_bytes = f.read()

    finally:
        import os
        os.remove(video_path)
        os.remove(audio_path)
        os.remove(output_path)

    return combined_bytes