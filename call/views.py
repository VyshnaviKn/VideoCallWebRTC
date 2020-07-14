import json
from django.shortcuts import render
from pyforkurento.client import KurentoClient
from pyforkurento.client import KurentoClient
from pyforkurento.pipeline import MediaPipeline
from pyforkurento.media_element import MediaElement
from pyforkurento.endpoints import WebRTCEndpoint
from rest_framework.views import APIView
from rest_framework.response import Response
from threading import Thread


# Create your views here.
def index(request):
	return render(request, "index.html")

def call_view(request):	
	return render(request,"call.html")

def fun(*args,**kwargs):
	pass
			# print("*"*20)
			# print(args)
			# print(kwargs)
			# print("*"*20)
candidate = None
def add_ice_cand(*args,**kwargs):
		global candidate
		if args:
			print("*"*20)
			print(args)
			#candidate = args[0].get("payload").get("candidate").get("candidate")
			candidate = args[0].get("payload").get("candidate")

web_rtc_endpoint = None
class SendOffer(APIView):
	def post(self, request):
		global web_rtc_endpoint
		offer = request.POST.get('sdp_offer')
		candidate = request.POST.get("candidate")
		client = KurentoClient("ws://localhost:8888/kurento")
		media = client.create_media_pipeline()
		pipeline_id = media.pipeline_id
		session_id = media.session_id
		media_pipeline = MediaPipeline(session_id,pipeline_id,client)
		end_point = media_pipeline.add_endpoint("WebRtcEndpoint",webrtc_send_only =True)
		session_id = end_point.session_id
		element_id = end_point.elem_id
		media_element = MediaElement(session_id,element_id,client)
		web_rtc_endpoint = WebRTCEndpoint(session_id,element_id,client)
		web_rtc_endpoint.add_event_listener("OnIceCandidate",fun)
		web_rtc_endpoint.gather_ice_candidates()
		web_rtc_endpoint.add_event_listener("OnIceGatheringDone",fun)
		result = web_rtc_endpoint.process_offer(offer)
		resp = {"sdpAnswer":result,"id":"PROCESS_SDP_ANSWER"}
		candidate_thread = Thread(target=add_ice_candidate, args=(web_rtc_endpoint,)) 
		candidate_thread.start()
		return Response(resp)

def add_ice_candidate(web_rtc_endpoint):
	web_rtc_endpoint.add_event_listener("OnIceCandidate",add_ice_cand)
	web_rtc_endpoint.gather_ice_candidates()
	res=web_rtc_endpoint.add_ice_candidate(candidate)
	web_rtc_endpoint.add_event_listener("OnIceGatheringDone",fun)
	print("done with gatering")

class AddIceCandidate(APIView):
	def post(self, request):
		candidate = request.POST.get("candidate")
		print("ADDING CANDIDATE")
		web_rtc_endpoint.add_event_listener("OnIceCandidate",fun)
		web_rtc_endpoint.gather_ice_candidates()
		web_rtc_endpoint.add_ice_candidate(candidate)
		web_rtc_endpoint.add_event_listener("OnIceGatheringDone",fun)
