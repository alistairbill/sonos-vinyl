settings.log.level.set(3)

vinyl = input.alsa(bufferize=true,fallible=true,device='pcm.liquidsoap_hires')

flac_hifi = %ffmpeg(format="mp4",
                    movflags="+dash+skip_sidx+skip_trailer+frag_custom",
                    frag_duration=10,
                    strict="-2",
                    %audio(codec="flac",
                           channels=2,
                           ar=44100
                    ))

output.harbor.hls(playlist="live.m3u8",
                  fallible=true,
                  port=8002,
                  path="/",
                  [("flac_hifi", flac_hifi)],
                  vinyl)
