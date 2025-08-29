# blinkbridge

**Note**: there is an issue related to local storage systems; please see issue [#1](https://github.com/roger-/blinkbridge/issues/1) for a temporary fix until it's resolved.

blinkbridge is a tool for creating an RTSP stream from a [Blink camera](https://blinkforhome.com/) using [FFmpeg](https://ffmpeg.org/) and [MediaMTX](https://github.com/bluenviron/mediamtx). Blink cameras are battery operated and don't have native RTSP support, so this tool uses the [BlinkPy](https://github.com/fronzbot/blinkpy) Python library to download clips every time motion is detected and then creates an RTSP stream from them.

Due to the slow polling rate of BlinkPy, there will be a **delay of up to ~30 seconds** between when a motion is detected and when the RTSP stream updates (can be changed at risk of the Blink server banning you). The RTSP stream will persist the last recorded frame (i.e. a static video) until the next motion is detected.

Once the RTSP streams are available, you can use them in applications such as [Frigate NVR](https://github.com/blakeblackshear/frigate) (e.g. for better person detection) or [Scrypted](https://github.com/koush/scrypted) (e.g. for Homekit Secure Video support).

# How it works

1. blinkbridge downloads the latest clip for each enabled camera from the Blink server
2. FFmpeg extracts the last frame from each clip and creates a short still video (~0.5s) from it
3. The still video is published on a loop to MediaMTX (using [FFMpeg's concat demuxer](https://trac.ffmpeg.org/wiki/Concatenate#demuxer))
4. When motion is detected, the new clip is downloaded and published
5. A still video from the last frame of the new clip is then published on a loop

# Usage

1. Download `compose.yaml` from this repo and modify accordingly
2. Download `config/config.json`, save to `./config/` and modify accordingly (be sure to enter your Blink login creditials)
3. Run `docker compose run blinkbridge` and enter your Blink verification code when prompted (this only has to be done once and will be saved in `config/.cred.json`). Exit with CTRL+c
4. Run `docker compose up` to start the service. The RTSP URLs will be printed to the console.

# Real-time Motion Events

The default mechanism for detecting motion is to poll the Blink servers, which can have a delay of up to 30 seconds. To get real-time motion events, `blinkbridge` includes a built-in web server that exposes an HTTP endpoint. You can send a `POST` request to this endpoint to immediately trigger a snapshot and update the RTSP stream.

The endpoint is available at `http://<host>:8000/motion_detected_event/{camera_name}`.

## Home Assistant and Alexa Integration Example

You can use this endpoint to integrate with services like Home Assistant and Alexa for real-time motion notifications. Here is an example workflow:

1.  **Create a helper toggle in Home Assistant.** This toggle will be used to signal that a motion event has occurred. For example, you can create an `input_boolean` called `input_boolean.blink_motion_detected`.
2.  **Create an Alexa routine.** In the Alexa app, create a routine that is triggered when your Blink camera detects motion. The action for this routine should be to turn on the helper toggle you created in Home Assistant.
3.  **Create a Home Assistant automation.** This automation will be triggered when the helper toggle is turned on. The action for this automation should be to send a `POST` request to the `blinkbridge` endpoint.

Here is an example of a Home Assistant automation:

```yaml
automation:
  - alias: "Blink Motion Detection"
    trigger:
      - platform: state
        entity_id: input_boolean.blink_motion_detected
        to: "on"
    action:
      - service: rest_command.blink_motion_event
        data:
          camera_name: "Your Camera Name" # Replace with your camera name
      - service: input_boolean.turn_off
        entity_id: input_boolean.blink_motion_detected
```

You will also need to configure the `rest_command` in your `configuration.yaml`:

```yaml
rest_command:
  blink_motion_event:
    url: "http://<blinkbridge_host>:8000/motion_detected_event/{{ camera_name }}"
    method: post
```

This setup allows you to get near real-time motion events from your Blink cameras in your RTSP stream.

# TODO

- [ ] Better error handling
- [ ] Cleanup code
- [ ] Support FFmpeg hardware acceleration (e.g. QSV)
- [ ] Process cameras in parallel and reduce latency
- [ ] Add ONVIF server with motion events

# Related projects

* https://github.com/kaffetorsk/arlo-streamer
