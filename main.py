from pysimplesoap.server import SoapDispatcher, SOAPHandler
from http.server import HTTPServer

HOST = "example.com"
PORT = 8001
STREAM_URI = f"http://{HOST}:8002/live.m3u8"
STREAM_LOGO = "logo.png"
STREAM_METADATA_TYPES = {"logo": str}
STREAM_METADATA = {"logo": f"http://{HOST}:{PORT}/{STREAM_LOGO}"}
MEDIA_METADATA_TYPES = {"id": str,
                        "title": str,
                        "mimeType": str,
                        "itemType": str,
                        "streamMetadata": STREAM_METADATA_TYPES}
MEDIA_METADATA = {
    "id": "vinyl",
    "title": "Vinyl",
    "mimeType": "audio/flac",
    "itemType": "stream",
    "streamMetadata": STREAM_METADATA,
}


class Handler(SOAPHandler):
    def do_GET(self):
        if self.path == f"/{STREAM_LOGO}":
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.end_headers()
            self.wfile.write(open(STREAM_LOGO, "rb").read())
        else:
            super().do_GET()


class Server(HTTPServer):
    def __init__(self, dispatcher: SoapDispatcher):
        self.dispatcher = dispatcher
        super().__init__(("", PORT), Handler)


dispatcher = SoapDispatcher("sonos-vinyl",
                            location=f"http://{HOST}:{PORT}",
                            namespace="http://www.sonos.com/Services/1.1")


def get_media_uri(id):
    return {"getMediaURIResult": STREAM_URI}


dispatcher.register_function(
    "getMediaURI", get_media_uri,
    returns={"getMediaURIResult": str},
    args={"id": str}
)


def get_media_metadata(id):
    return {"getMediaMetadataResult": MEDIA_METADATA}


dispatcher.register_function(
    "getMediaMetadata", get_media_metadata,
    returns={"getMediaMetadataResult": MEDIA_METADATA_TYPES},
    args={"id": str}
)


def get_metadata(id, index, count, recursive=False):
    if id in ("root", "vinyl"):
        return {"getMetadataResult": [{
            "index": 0,
            "count": 1,
            "total": 1,
            "mediaMetadata": MEDIA_METADATA}]}
    else:
        return {"getMetadataResult": [{"index": 0, "count": 0, "total": 0}]}


dispatcher.register_function(
    "getMetadata", get_metadata,
    returns={"getMetadataResult": {
        "index": int, "count": int, "total": int,
        "mediaMetadata": MEDIA_METADATA_TYPES}},
    args={"id": str, "index": int, "count": int, "recursive": bool}
)


def get_last_update():
    return {"getLastUpdateResult": {"catalog": "", "favorites": "", "pollInterval": 3600}}


dispatcher.register_function(
    "getLastUpdate", get_last_update,
    returns={"getLastUpdateResult": {"autoRefreshEnabled": bool,
                                     "catalog": str, "favorites": str, "pollInterval": int}},
    args={}
)

if __name__ == "__main__":
    server = Server(dispatcher)
    server.serve_forever()
