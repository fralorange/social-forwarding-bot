import sys
import os
import pytest

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../../src')
    )
)

from src.utilities.downloaders.reddit import download_reddit_post_async

@pytest.mark.asyncio
async def test_download_reddit_post_async_returns_bytes():
    url = ('https://www.reddit.com/r/WynnCraft/'
           'comments/1kz00vi/meme_spare_mythic/'
           '?share_id=R9apnUjQMj-JdSUfQgLDh'
           '&utm_content=1&utm_medium=android_app'
           '&utm_name=androidcss&utm_source=share'
           '&utm_term=14')

    data = await download_reddit_post_async(url)
    assert isinstance(data, (bytes, bytearray)), "Must return raw bytes"
    assert len(data) > 0, "The data must not be empty"
