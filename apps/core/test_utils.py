from django.test import SimpleTestCase

from .utils import youtube_embed_url, youtube_video_id


class YoutubeVideoIdTests(SimpleTestCase):
    def test_extracts_id_from_watch_url(self):
        self.assertEqual(
            youtube_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
            "dQw4w9WgXcQ",
        )

    def test_extracts_id_from_watch_url_with_extra_params(self):
        self.assertEqual(
            youtube_video_id(
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s&list=PL123"
            ),
            "dQw4w9WgXcQ",
        )

    def test_extracts_id_from_short_url(self):
        self.assertEqual(
            youtube_video_id("https://youtu.be/dQw4w9WgXcQ"), "dQw4w9WgXcQ"
        )

    def test_extracts_id_from_existing_embed_url(self):
        self.assertEqual(
            youtube_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ"),
            "dQw4w9WgXcQ",
        )

    def test_returns_empty_string_for_blank_url(self):
        self.assertEqual(youtube_video_id(""), "")

    def test_returns_empty_string_for_non_youtube_url(self):
        self.assertEqual(youtube_video_id("https://vimeo.com/12345"), "")


class YoutubeEmbedUrlTests(SimpleTestCase):
    def test_builds_embed_url_from_watch_url(self):
        self.assertEqual(
            youtube_embed_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
        )

    def test_returns_empty_string_when_no_id_found(self):
        self.assertEqual(youtube_embed_url("https://example.com"), "")
