#! /usr/bin/env python 
import gobject, pygst
pygst.require("0.10")
import gst 

DEST_HOST = '192.168.100.37'

AUDIO_SRC = 'filesrc'
AUDIO_ENC = 'alawenc'
AUDIO_PAY = 'rtppcmapay'

RTP_SEND_PORT = 5002
RTCP_SEND_PORT = 5003
RTCP_RECV_PORT = 5007 


class Send:
    def __init__ (self):
        #pipeline.set_property("gst-debug-level", "4")
        # create pipeline 
        self.pipeline_send = gst.Pipeline('rtp_server')

        # ... add elements
        audiosrc = gst.element_factory_make(AUDIO_SRC, 'audiosrc')
        audiosrc.set_property("location", "/home/pi/media/test.mp3")
        audioconv = gst.element_factory_make('audioconvert', 'audioconv')
        audiores = gst.element_factory_make('audioresample', 'audiores')

        # ... add elements
        audioenc = gst.element_factory_make(AUDIO_ENC, 'audioenc')
        audiopay = gst.element_factory_make(AUDIO_PAY, 'audiopay')

        # add capture and payloading to the pipeline and link
        self.pipeline_send.add(audiosrc, audioconv, audiores, audioenc, audiopay)

        res = gst.element_link_many(audiosrc, audioconv, audiores, audioenc, audiopay)

        # the gstrtpbin element
        gstrtpbin = gst.element_factory_make('gstrtpbin', 'gstrtpbin')

        self.pipeline_send.add(gstrtpbin) 

        # the udp sinks and source we will use for RTP and RTCP
        rtpsink = gst.element_factory_make('udpsink', 'rtpsink')
        rtpsink.set_property('port', RTP_SEND_PORT)
        rtpsink.set_property('host', DEST_HOST)

        rtcpsink = gst.element_factory_make('udpsink', 'rtcpsink')
        rtcpsink.set_property('port', RTCP_SEND_PORT)
        rtcpsink.set_property('host', DEST_HOST)
        # no need for synchronisation or preroll on the RTCP sink
        rtcpsink.set_property('async', False)
        rtcpsink.set_property('sync', False) 

        rtcpsrc = gst.element_factory_make('udpsrc', 'rtcpsrc')
        rtcpsrc.set_property('port', RTCP_RECV_PORT)

        self.pipeline_send.add(rtpsink, rtcpsink, rtcpsrc) 

        # now link all to the gstrtpbin, start by getting an RTP sinkpad for session 0
        sinkpad = gst.Element.get_request_pad(gstrtpbin, 'send_rtp_sink_0')
        srcpad = gst.Element.get_static_pad(audiopay, 'src')
        lres = gst.Pad.link(srcpad, sinkpad)

        # get the RTP srcpad that was created when we requested the sinkpad above and
        # link it to the rtpsink sinkpad
        srcpad = gst.Element.get_static_pad(gstrtpbin, 'send_rtp_src_0')
        sinkpad = gst.Element.get_static_pad(rtpsink, 'sink')
        lres = gst.Pad.link(srcpad, sinkpad)

        # get an RTCP srcpad for sending RTCP to the receiver
        srcpad = gst.Element.get_request_pad(gstrtpbin, 'send_rtcp_src_0')
        sinkpad = gst.Element.get_static_pad(rtcpsink, 'sink')
        lres = gst.Pad.link(srcpad, sinkpad)

        # we also want to receive RTCP, request an RTCP sinkpad for session 0 and
        # link it to the srcpad of the udpsrc for RTCP
        srcpad = gst.Element.get_static_pad(rtcpsrc, 'src')
        sinkpad = gst.Element.get_request_pad(gstrtpbin, 'recv_rtcp_sink_0')
        lres = gst.Pad.link(srcpad, sinkpad)

    def start(self):
        # set the pipeline to playing
        gst.Element.set_state(self.pipeline_send, gst.STATE_PLAYING) 

    def stop(self):
        # set the pipeline to stop
        gst.Element.set_state(self.pipeline_send, gst.STATE_READY)

    def quit(self):
        gst.Element.set_state(self.pipeline_send, gst.STATE_NULL)

