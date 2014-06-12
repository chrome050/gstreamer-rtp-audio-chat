#! /usr/bin/env python 
# Receive
import pygst
pygst.require("0.10")
import gst
#import gobject

class Receive:
	def __init__ (self, AUDIO_CAPS = 'application/x-rtp,media=(string)audio,clock-rate=(int)8000,encoding-name=(string)PCMA', AUDIO_DEPAY = 'rtppcmadepay', AUDIO_DEC = 'alawdec', 
		AUDIO_SINK = 'autoaudiosink', DEST = '192.168.100.27', RTP_RECV_PORT = 5002, RTCP_RECV_PORT = 5003, RTCP_SEND_PORT = 5007):
		print(DEST)
		print(AUDIO_SINK)
		#AUDIO_SINK = 'pulseaudiosink'

		#AUDIO_DEPAY = 'rtpopusdepay'
		#AUDIO_DEC = 'opusdec'


		#DEST = '127.0.0.1'
		#DEST = '172.17.100.27'

		def pad_added_cb(gstrtpbin, new_pad, depay):
		    try:
			sinkpad = gst.Element.get_static_pad(depay, 'sink')
			lres = gst.Pad.link(new_pad, sinkpad)
		    except Exception as e:
			print "Exception e %s" % e

		# the pipeline to hold eveything 
		self.pipeline = gst.Pipeline('rtp_client')

		# the udp src and source we will use for RTP and RTCP
		rtpsrc = gst.element_factory_make('udpsrc', 'rtpsrc')
		rtpsrc.set_property('port', RTP_RECV_PORT)

		# we need to set caps on the udpsrc for the RTP data
		print AUDIO_CAPS
		caps = gst.caps_from_string(AUDIO_CAPS)
		rtpsrc.set_property('caps', caps)

		rtcpsrc = gst.element_factory_make('udpsrc', 'rtcpsrc')
		rtcpsrc.set_property('port', RTCP_RECV_PORT)

		rtcpsink = gst.element_factory_make('udpsink', 'rtcpsink')
		rtcpsink.set_property('port', RTCP_SEND_PORT)
		rtcpsink.set_property('host', DEST)

		# no need for synchronisation or preroll on the RTCP sink
		rtcpsink.set_property('async', False)
		rtcpsink.set_property('sync', False) 

		self.pipeline.add(rtpsrc, rtcpsrc, rtcpsink)

		# the depayloading and decoding
		audiodepay = gst.element_factory_make(AUDIO_DEPAY, 'audiodepay')
		audiodec = gst.element_factory_make(AUDIO_DEC, 'audiodec')

		# the audio playback and format conversion
		audioconv = gst.element_factory_make('audioconvert', 'audioconv')
		audiores = gst.element_factory_make('audioresample', 'audiores')
		audiosink = gst.element_factory_make(AUDIO_SINK, 'audiosink')

		# add depayloading and playback to the pipeline and link
		self.pipeline.add(audiodepay, audiodec, audioconv, audiores, audiosink)

		res = gst.element_link_many(audiodepay, audiodec, audioconv, audiores, audiosink)

		# the gstrtpbin element
		gstrtpbin = gst.element_factory_make('gstrtpbin', 'gstrtpbin')

		self.pipeline.add(gstrtpbin)

		# now link all to the gstrtpbin, start by getting an RTP sinkpad for session 0
		srcpad = gst.Element.get_static_pad(rtpsrc, 'src')
		sinkpad = gst.Element.get_request_pad(gstrtpbin, 'recv_rtp_sink_0')
		lres = gst.Pad.link(srcpad, sinkpad)

		# get an RTCP sinkpad in session 0
		srcpad = gst.Element.get_static_pad(rtcpsrc, 'src')
		sinkpad = gst.Element.get_request_pad(gstrtpbin, 'recv_rtcp_sink_0')
		lres = gst.Pad.link(srcpad, sinkpad)

		# get an RTCP srcpad for sending RTCP back to the sender
		srcpad = gst.Element.get_request_pad(gstrtpbin, 'send_rtcp_src_0')
		sinkpad = gst.Element.get_static_pad(rtcpsink, 'sink')
		lres = gst.Pad.link(srcpad, sinkpad)

		gstrtpbin.connect('pad-added', pad_added_cb, audiodepay) 

	def start(self):
		self.pipeline.set_state(gst.STATE_PLAYING)
	def stop(self):
		self.pipeline.set_state(gst.STATE_READY) 
	def quit(self):
		self.pipeline.set_state(gst.STATE_NULL) 
