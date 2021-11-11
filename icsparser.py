#!/usr/bin/env python

"""
//  -------------------------------------------------------------
//  author        Giga
//  project       qeeqbox/ics-visualizer
//  email         gigaqeeq@gmail.com
//  description   app.py (CLI)
//  licensee      AGPL-3.0
//  -------------------------------------------------------------
//  contributors list qeeqbox/ics-visualizer/graphs/contributors
//  -------------------------------------------------------------
"""

from json import loads, dumps, dump, load
from os import mkdir, path
from codecs import open as copen
from ixora import QBIxora
from re import search as research

class ICSParser():
	def __init__(self,name,file):
		self.data = []
		self.graph = QBIxora(name)
		self.icspath = path.abspath(path.join(path.dirname(__file__), file))
		with copen(self.icspath, encoding='ascii', errors='ignore') as json_data:
			self.data = load(json_data)

	def get_company(self, item, body, search):
		if "company" in item:
			if item["company"] != "":
				body.append("<b>Company: </b>" + item["company"])
				search.append(item["company"])
		return body,search

	def get_ports(self, item, body, search):
		if "ports" in item:
			if len(item["ports"]) > 0 :
				body.append("<b>Ports: </b>" + " ".join(item["ports"]))
				search.append("Ports: ( {} )".format(" ".join(item["ports"])))
		return body,search

	def get_info(self, item, body):
		if "info" in item:
			if item["info"] != "":
				body.append("<b>Info: </b>" + item["info"])
		return body

	def get_links(self, item, body, search):
		links = ""
		if "refs" in item:
			links += "<b>Links: </b>"
			for ref in item["refs"]:
				if ref == "wiki":
					links += '<a href="{}" target="_blank"><img src="wiki.png" style="padding-right:10px;width:15px;height:15px;"></a>'.format(item["refs"][ref])
					search.append("wikipedia:yes")
				elif ref == "wireshark":
					links += '<a href="{}" target="_blank"><img src="wireshark.png" style="padding-right:10px;width:15px;height:15px;"></a>'.format(item["refs"][ref])
					search.append("wireshark:yes")
				elif ref == "nmap":
					links += '<a href="{}" target="_blank"><img src="nmap.png" style="padding-right:10px;width:15px;height:15px;"></a>'.format(item["refs"][ref])
					search.append("nmap:yes")
				else:
					links += '<a href="{}" target="_blank""><img src="external.png" style="padding-right:10px;width:15px;height:15px;"></a>'.format(item["refs"][ref])
			body.append(links)
		return body, search

	def generate_graph(self):
		temp_sub_names = []
		self.graph.add_node("wireshark",_set = {'header':'{}'.format("wireshark"),'body':'', 'width':20, 'color':'#0277bd'},search='{}'.format("wireshark"))
		self.graph.add_node("wikipedia",_set = {'header':'{}'.format("wikipedia"),'body':'', 'width':20, 'color':'#FEFEFE'},search='{}'.format("wikipedia"))
		self.graph.add_node("ports",_set = {'header':'{}'.format("ports"),'body':'', 'width':20, 'color':'#808080'},search='{}'.format("ports"))
		self.graph.add_node("nmap",_set = {'header':'{}'.format("nmap"),'body':'', 'width':20, 'color':'#81d4fa'},search='{}'.format("nmap"))
		for item in self.data["main"]:
			for group in item["groups"]:
				self.graph.add_node(group,_set = {'header':'{}'.format(group),'body':'', 'width':20, 'color':'#FF0000'},search='{}'.format(group))
		for item in self.data["main"]:
			body = []
			search = []
			link_types = []
			search.append(item["name"])
			body, search = self.get_company(item, body, search)
			body, search = self.get_ports(item, body, search)
			body, search = self.get_links(item, body, search)
			body = self.get_info(item, body)
			self.graph.add_node(item["name"],_set = {'header':'{}'.format(item["name"]),'body': "<hr>".join(body), 'width':12, 'color':'#FFFF00'},search='{}'.format(" | ".join(search)))
			for group in item["groups"]:
				self.graph.add_edge(item["name"],group,{'width':1})
			if "wireshark:yes" in search:
				self.graph.add_edge(item["name"],"wireshark",{'width':1})
			if "wikipedia:yes" in search:
				self.graph.add_edge(item["name"],"wikipedia",{'width':1})
			if "nmap:yes" in search:
				self.graph.add_edge(item["name"],"nmap",{'width':1})

		for item in self.data["sub"]:
			body = []
			search = []
			wireshark = False
			wikipedia = False
			search.append(item["name"])
			body, search = self.get_company(item, body, search)
			body, search = self.get_ports(item, body, search)
			body, search = self.get_links(item, body, search)
			body = self.get_info(item, body)
			self.graph.add_node(item["name"],_set = {'header':'{}'.format(item["name"]),'body': "<hr>".join(body), 'width':7, 'color':'#fe42ad'},search='{}'.format(" | ".join(search)))
			if "wireshark:yes" in search:
				self.graph.add_edge(item["name"],"wireshark",{'width':1})
			if "wikipedia:yes" in search:
				self.graph.add_edge(item["name"],"wikipedia",{'width':1})
			if "nmap:yes" in search:
				self.graph.add_edge(item["name"],"nmap",{'width':1})
			if "ports" in item:
				self.graph.add_edge(item["name"],"ports",{'width':1})
				if len(item["ports"]) > 0 :
					for port in item["ports"]:
						for i, search_q in enumerate(self.graph.graph['search_input']):
							if research(rf" {port} ", search_q):
								target = self.graph.graph["nodes"][self.graph.graph['search_index'][i]]["name"]
								#if target not in temp_sub_names:
								self.graph.add_edge(item["name"],target,{'width':1})
		self.graph.create_graph('#ixora-graph',window_title="ICS-Visualizer", search_title="Search Box",search_msg="Search ICS DB by Name, Port, Company and Protocol", copyright_link="https://github.com/qeeqbox/ICS-Visualizer",copyright_msg="ICS-Visualizer",tools=['search','tooltip','menu','window'], collide=300,distance=300, data=self.graph.graph,method="file_with_json", save_to="app.html",open_file=True)

temp = ICSParser("ICS-Visualizer","data.json")
temp.generate_graph()